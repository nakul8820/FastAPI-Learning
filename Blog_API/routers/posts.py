# ====== 

# Full CRUD ( create, read , update, delete) for blog posts.
# also includes search and pagination

# GET: /api/posts/ : lists all published posts
# GET: /api/posts/search : search posts by keyword
# GET: /api/posts/my-posts: get yout posts (auth required)
# GET: /api/posts/{id} : Get a single post by ID
# POST: / api/posts/ : create new posts {auth require}
# PUT: /api/posts/{id} : update your post {auth require}
# DELETE: /api/posts/{id} : delete your post {auth require}

import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core import get_db
from models.models import Post, User
from schemas.schemas import (
    PostCreate, PostUpdate, PostResponse,
    PostSummary, PaginatedPosts, MessageResponse
)
from dependencies.auth import get_current_active_user

router = APIRouter()

# List all published posts (with pagination)
# Get /api/posts/
# public - no auth required 

@router.get(
    "/",
    response_model=PaginatedPostes,
    summary="List all published post with pagination"
)
def list_posts(
    # Quesry Parameters - user passes these in the URL like:
    # /api/post/?page=2&limit=5
    page: int = Query(1, ge=1, description="Page Number ( starts at 1)"),
    limit : int = Query(10, ge =1, le=100, description="postsnper page mac 100"),
    db: Session = Depends(get_db)
):
    """
    Returns a paginated list of all PUBLISHED posts.
    Example : GET / api/posts/?page=1&limit=10

    Pagination prevents loading thounds of posts at once -
    you get them in chunks instead
    """
    # Calculate offset ( How many records to skip)
    # page 1: skip 0, show posts 1-10
    # page 2: skip 10, show 10 - 10
    offset = (page - 1) * limit

    # Query only published posts
    query = db.query(Post).filter(Post.published == True)

    total = query.count() # Total matching posts ( for pagination)

    posts = (
        query
        .order_by(Post.created_at.desc()) # Newest First
        .offset(offset)                   # skip previous pages
        .limit(limit)                     # only take 'limit'posts
        .all()
    )

#  Search Posts
# GET /api/posts/search?q=python
# # Public = no auth required

router.get(
    "/search",
    response_model = List[PostSummary],
    summary="Search posts by keyword in the title or context"
)
def search_posts(
    q: str = Query(..., min_length= 2, description="search Key word"),
    db: Session = Depends(get_db)
):
    """
    Searches post titles and content for the given keyword.
    Example: GET  /api/posts/search?q=python

    ilike() = case-insensitive LIKE search
    %q% = wildcard : keyword can appear anywhere in the text
    """
    posts = (
        db.query(Post)
        .filter(
            Post.published == True,
            # Search in BOTH title and content
            # | is OR operator in SQLAlchemy filters
            (Post.title.ilike(f"%{q}%")) | (Post.content.ilike(f"%{q}%"))
        )
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts


# GET MY POSTS
# GET. /api/posts/my-posts
# auth required

@router.get(
    "/my-posts",
    response_model= List[PostSummary],
    summary=" Get All Posts By Currently Logged - In user"
)
def my_post(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns All post ( including drafts) by the current user 
    Author's Dashboard
    """
    posts = (
        db.Query(Post)
        .filter(Post.author_id == current_user.id) # on;y current user posts
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts

# Get a single post by ID
# GET /api/posts/{post_id}
# Public - No auth

@router.get(
    ".{post_id}",
    response_model=PostResponse,
    summary="Get a single post by ID"
)
def get_post(
    post_id: int, #FastAPI extracts this from the URL path
    db: Session = Depends(get_db)
):
    """
    Fetches the post by its ID.
    Else returns not found 404 
    """
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.published == True # only published posts 
    ).first()

    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    return post

## Create a new post
# POST /api/posts/
# Auth Required
router.post(
    "/",
    response_model=PostResponse,
    status_code= status.HTTP_201_CREATED,
    summary="Create a new blog post"
)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new blog post owned by the currently logged-in user.
    Set published=true to make it public , false to keep as draft.
    """
    new_post = Post(
        title = post_data.title,
        content = post_data.content,
        published = post_dara.published,
        author_id = current_user.id # Link post to the logged-in user 
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# Update a POST
# PUT /api/posts/{post_id}
# Auth require - you can only edit YOUR OWN posts

@router.put(
    "/{post_id}",
    reponse_model=PostResponse,
    summary="Update a post (Author only )"
)
def update_post(
    post_id: int,
    post_data: PostResponse,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Updates a post. Only the post's author can update it.
    All fields are optional - send only what you want to change.
    """
    # ---- Find the post
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )

    # Apply changes
    update_data = post_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, firls, value) # Dynamically set each field

    db.commit()
    db.refresh(post)

    return post


# DELETE A POST
# DELETE /api/posts/{post_id}
# Auth required , Delete only your own posts (or admin)

@router.delete(
    "/{post_id}",
    response_model=MessageResponse,
    summary="Delete a post( author or admin only)"
)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session =Depends(get_db)
):
    """
    Deletes a post permanently.
    All comments on this post are also deleted.
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found,"
        )

    # Only author or admin can delete the post 
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code= ststus.HTTP_403_FORBIDDEN,
            detail=" you can only delete your own posts"
        )
    db.delete(post)
    db.commit()

    return {"message": f"post '{post.title}' deleted successfully."}