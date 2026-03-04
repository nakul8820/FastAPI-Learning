# ============================================================
# schemas/schemas.py — PYDANTIC SCHEMAS (Data Validation)
# Schemas define the SHAPE of data going IN and OUT of the API.
#
# models (models.py) = How data is stored in DATABASE
# Schemas = How data looks in API requests / Response 

# Pydantic automatically:
#   -validates incoming data (e.g email, mustbe calid format)
#   -Converts types (e.g sting "123" -> integer 123)
#   - Generates clear error messages when data is wrong 

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# User Schema 

class UserCreate(BaseModel):
    """
    schema for creating a new user (registration)
    """
    username: str = Field(..., min_length=3, max_length=50)
    #                    "..." means requred and min_length and max_length validation rules

    email: EmailStr
    # EmailStr automatically validates email format
    # "not an email would fail, "user#example.com" passes
    password: str = Field(..., min_length=6)
    # {assword must be 6 characters}

class UserResponse(BaseModel):
    """
    Schema for returning user data in API responses.
    Notice: No password field! we send password back.
    """
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    create_at: datetime

    class Config:
        # this allows Pydantic to read data from SQLAlchemy model objects.
        # without this pydantic can only read plain dictionaries.
        # orm_mode = True -> read from ORM objects , not just dicts
        orm_mode = True

class UserUpdate(BaseModel):
    """
    Schema for updating a user profile
    All fields are optional - the user can update just one field
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    # None means "not provided / don't change"

# Authentication Schemas 

class LoginRequest(BaseModel):
    """ What the user sends to log in """
    email : EmailStr
    password : str

class Token(BaseModel):
    """ What we send BACK after successfull log in. """
    access_token: str   # The JWT token string 
    token_type: str     # Always "bearer" (this is HTTP Standard)


# Post schemas 

class PostCreate(BaseModel):
    """ Schema for creating a new blog post. """
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    published: bool = False # Default: save as draft

class PostUpdate(BaseModel):
    """ Schema for updating Post """
    title: Optional[str] = Field(None, minlength=5, mac_length=200)
    content: Optional[str] = Field(None, min_length=10)
    published: Optional[bool] = None

class PostResponse(BaseModel):
    """ Schemas for returning post data. Includes author info """
    id: int
    title: str
    content: str
    published: bool
    create_at: datetime
    updated_at: datetime
    author_id: int
    author: UserResponse # Nested ! Returns full author object from earlier class UserResponse

    class Config:
        orm_mode = True

class PostSummary(BaseModel):
    """
    Lighter version of PostResponse for listing posts.
    Used in list endpoints to avoid sending full contents.
    Imagine Loading 100 posts - you don't want all the content
    """
    id: int
    title: str
    published: bool
    created_at: datetime
    author: UserResponse

    class Config:
        orm_mode = True

# Comment Schemas

class CommentCreate(BaseModel):
    """ schema for creating comment."""
    content: str = Field(..., min_length=1, mac_length=100)
    post_id : int # which post this comment belongs to 

class CommentResponse(BaseModel):
    """ schema for returning comment data."""
    id: int
    content: str
    created_at: datetime
    author: UserResponse
    post_id: int 

    class Config:
        orm_mode = True

# Generic Response Schemas 

class MessageResponse(BaseModel):
    """
    Simple response for actions that just return a message.
    Example: {"message":"Post Deleted successfully"}
    """
    message: str

class PaginatedPosts(baseModel):
    """
    Response schema for paginated list of posts.
    Pagination = splitting large results into pages.
    """
    total: int # Total number of posts in DB
    page: int  # Current page number 
    limit: int  # How many posts per page
    posts: List[PostSummary] # The actual posts for this page

    class Config:
        orm_mode = True