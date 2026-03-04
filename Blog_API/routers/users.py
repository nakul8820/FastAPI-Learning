# ==============
# users.py USER MANAGEMENT ROUTES
#
# Get : /api/users/   :List all users (admin only)
# Get : /api/usrs/{id} :Get a users's public profile
# Put : /api/username :Update your own profile
# Delete: /api/usrs/{id} :Delete a user (admin only)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.databas import get_db
from core.security import hash_password
from models.models import User
from schemas.schemas import UserResponse, UserUpdate, MessageResponse
from dependencies.auth import get_current_active_user, get_admin_user

router = APIRouter()

# ---------
# List all the users - admin only
# Get /api/users/

@router.get(
    "/",
    response_model = List[UserResponse],
    summary="List all the users(admin only)"
)

def list_users(
    # get_admin_user checks: is logged in + is active + is admin
    admin: User = Depends(get_admin_user),
    db : Session = Depends(get_db)
):
    """
    Returns all registerd users.
    Only accessible by admin accounts.
    """
    return db.query(User).all()

# GET USER PUBLIC PROFILE
# GET /api/userss/{user_id}
# public - no auth required

@router.get(
    "/{user_id}",
    response_model= UserResponse,
    summary= "Get a user's public profile by ID"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetches a user's public profile
    anyone can view this - no login required.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail= f"User with ID {user_id} not found"
        )
    return user


# Update my profile
# PUT /api/users/me
# Auth required - only updates YOUR OWN profile

@router.put(
    "/me",
    response_model = UserResponse,
    summary = "Update Your Own profile"
)
def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Allows the logged-in user to update their own profile.
    Only send the fields you want to change.
    """
    # Check if new username is taken
    if update_data.username:
        taken = db.query(User).filter(
            User.username == update_data.username,
            User.id != current_user.id
        ).first()
        if taken:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="This username is already taken."
            )
    
    # Check if new email is taken
    if update_dat.email:
        taken = db.query(User).filter(
            User.email == update_data.email,
            Iser.id != current_user.id
        ).first()
        if taken:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="This email is already  in use"
            )
    
    # Apply updates 
    # exclude_unset = True -> only fields explicitly sent by the user
    changes = update_data.dict(exclude_unset=True)
    for field, value in changes.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user

# DELETE A USER - Admin onlt=y
@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete auser account (admin only)"
)

def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    permenently deletes a user account and all their posts / comments
    Admin Only Action.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent admins from deleting themselves
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account."
        )
    
    db.delete(user) # cascade="all, delete" in models will also delete their posts/comments
    db.commit()

    return {"message":f"User '{user.username}' has been deleted."}