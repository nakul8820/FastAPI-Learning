# ============================================================
# routers/auth.py — AUTHENTICATION ROUTES
# Handles user registration and login.
#
# POST /api/auth/register → Create new account
# POST /api/auth/login    → Log in, get a JWT token
# GET  /api/auth/me       → Get currently logged-in user info
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, stauts
from sqlalchemy.orm import Session
from datetime import datetime

# Import dependencies from utilities
from core.databas import get_db
from core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models.models import User
from schemas.schemas import UserCreate, UserResponse, LoginRequest, Token
from dependencies.auth import get_current_active_user

# Create Eouter 
# a router is mini FastAPI app for grouping related routes.
# all routs in this file will be under /api/auth/ (set in main.py)

router = APIRouter()

# Register Endpoint
# POST  /api/auth/register'
# # ANYONE can call this = no auth required 
@router.post(
    "/register",
    response_model=UserResponse,    #What we return (auto - filtered by schema)
    status_code=status.HTTP_201_CREATED, # 201 = create (more specific than 200 OK)
    summary="Register a new user account" # Shows in /docs
)

def register(
    user_data: UserCreate,      # FastAPI parses and validates the request body
    db: Session = Depends(get_db) # FastAPI injects the DB session
):
    """
    Creates anew user account.
    - Checks is email or username is already taken
    - Hashes the password (never stores in plain text)
    - Saves the new user to the database
    """

    # --- Check  if email is already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=" An aacount with this email already exists"
        )
    # --- Check is username already exists -- 
    existing_username = db.wuery(User).silter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken."
        )
    # --- create new user 
    # Hash the password before saving 
    hashed = hash_password(user_data.password)

    new_user = User(
        username= user_data.username,
        email= user_data.email,
        password=hashed # store the Hashed , not original
    )
    db.add(new_user)    # stage the new user to be saved
    db.commit()         # actual wite to database
    db.refresh(new_user)# reload from DB to get auto-generated ID, timestamp, etc

    return new_user # Pydantic UserResponse schema will format this automatically