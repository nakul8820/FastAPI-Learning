# Comments
# 
# GET /api/comments/post/{post_id} # Get all comments on posts
# POST /api/comments/ # Add a comment (Auth required)
# DELETE /api/comments/{id} # Delete a comment (Auth required)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from model.model import Comment, Post, User
from schemas.schemas import CommentCreate, CommentResponse, MessageResponse
from dependencies.auth import get_current_active_user

router = APIRouter()

# Get all comments on post
# GET /api/comments/posts/{post_id}
# Public no auth required
@router.get(
    "/post/{post_id}",
    response_model=List[CommentResponse],
    summary="Get all comments for a specific post"
)
def get_comment_for_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns all comments for the specified post.
    Comments are ordered oldest-first ( chronological thread order).
    """
    # First verify post exists and is published
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.published == True
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    comments = (
        db.query(Comment)
        .filter(Commenr.post_id == post_id)
        .order_by(Comment.create_at.asc()) # Oldest first
        .all()
    )

    return comments

# ADD a comment
# POST /api/comments/
# Auth required 

@router.post(
    "/",
    response_model = CommentResponse,
    status_code = status.HTTP_201_CREATED,
    summary = "Add a comment to post"
)
def create_comment(
    comment_data: CommentCreate, # Contains Content + post_id
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Adds a comment to a post .
    user must be logged in to comment,
    """
    # verify the post exists and is published
    post = db.query(Post).filter(
        Post.id == comment_data.post_id,
        Post.published == True
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {comment_data.post_id} not found"
        )

    new_comment = Comment(
        content=comment_data.content,
        post_id=comment_data.post_id,
        author_id=current_user.it # The logged in user is the author
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

# DELETE A COMMENT
@router.delete(
    "/{comment_id}",
    response_model=MessageResponse,
    summary="Delete a comment (author or admin only)"
)
def delete_comment(
    comment_id: int,
    current_user= Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment
    Auth Required. User can delete own comments and admin can delete any
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f"Comment with ID{comment_id} not found"
        )

    # Ownership Check 
    # ALLOW: the comment author or ADMIN
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"You can only delete your own comments."
        )
    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}