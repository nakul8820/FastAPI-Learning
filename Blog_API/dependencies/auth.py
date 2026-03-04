# ============================================================
# dependencies/auth.py — AUTHENTICATION DEPENDENCIES
# A "dependency" in FastAPI is a function that runs
# BEFORE your endpoint. FastAPI calls it automatically
# and injects the result into your route function.
#
# These dependencies are how we protect routes —
# forcing users to be logged in before accessing them.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_token
from models.models import User

# OAUTH2 SCHME
# This tells fastAPI: Tokens comes from the /api/auth/login endpoint 
# It automatically reads "Authorization: Beare <token>" header
# from incoming requests. 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    token: str = Depends(oauth2_sheme), # FastAPI extractstoken from header
    db: Session = Depends(get_db)       # FastAPI provides Db session
) -> User:
    """
    Dependency that:
    1 . Reads JWT token from the request heaer
    2 . Decodes it to find out WHO is making request
    3 . Fetches that user from database
    4 . Returns the user object ( or raises 401 if invalid)
    
    Usage in route:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get__current_user)):
            # current_user is npw the logged-in user object
            return {"Hello": current_user.username}
    """

    # this exception is what we raise when authentication fails
    # 401 = unauthorised ( not logged in / bad token )
    credentials_exception = HTTPException(
        stauts = status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again",
        headers={"WWWW-Authenticate": "Bearer" }, #standard HTTP header for auth errors
    )

    # Decode the token -> fet the user's email
    email= decoder_token(token)
    if email is None:
        raise credentials_exception # token was invalid or expired

    # Look up the user in the database by their email
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credential_exception # Token had an email but user doesn't exist

    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Extends get_current_user by also checking if the user account is active (not banned/ deactivated)
    This is a dependency that USES another dependency!
    FastAPI handles the chain automatically
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated."
        )
    return current_user

def get_admin_user(
    current_use: User = Depends(get_current_active_user)
) -> User:
    """
    Requires the user to be an ADMIN.
    Use this dependency on admin-only routes.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user