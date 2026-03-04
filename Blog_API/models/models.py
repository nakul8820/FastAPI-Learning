# ============================================================
# models/models.py — DATABASE MODELS (Tables)
# These Python classes = database tables.
# SQLAlchemy reads these and creates actual SQL tables.
#
# Think of each class as a table, and each attribute as a column.
# ============================================================

from sqlalchemy import(
    Column,     # Defines a column in table
    Integer,    # Integer DataType
    String,     # VARCHAR DataType
    Boolean,    # BOOLEAN DataType
    Text,       # TEXT data type
    DateTime,   # DATETIME data type
    ForeignKey, # Links one table to another 
)

from sqlalchemy.orm import relationship
from datetime import datetime

# Import Base Class ( ALL MODELS MUST INHERIT FROM THIS BASE DATABASE)

from core.database import Base

#---------------
# USER TABLE
# STORE ALL REGISTERED USERS
# ONE USER CAN HAVE mANY POSTS AND MANY COMMENTS

class User(Base):
    # The actual table name in database
    __tablename__ = "users"

    # COLUMNS ______
    id = Column(Integer, primary_key=True, index=True)
    #     ↑ Auto-incrementing unique ID for each user   

    username = Column(String(50), unique=True, nullable=False, index=True)
    #               max- 50 chars , must be unique, can not ne empty

    email = Column(String(100), unique=True, nullable=False, index=True)
    #.              100 chars, index=True make searching by email FAST

    password = Column(String(255), nullable=False)
    #           We store the hashed password here never plain text

    is_active = Column(Boolean, default=True)
    #           active users can log in , Deactivated = soft delete

    is_admin = Column(Boolean, default=False)
    #           Admin user can delete any post / comment

    created_at = Column(DateTime, default=datetime.utcnow)
    #             Automatically set to current time when user is created

    # Relationships
    # This tells SQQLAlchemy user has many posts
    # back_populates="authors" means post has fields called author 
    # thatpoint backs to user 
    posts = relationship("post", back_populates="author", cascade="all, delete")
    comments = relationship("Comment", back_populates="author", cacade="all, delete")
    # cacade = "all, delete" -> when user is deleted, their posts and comments too


# POST TABlE
# Stores All the blog posts
# Each Post belong to ONE user (author)
# One post can have MANY comments.

class Post(Base):
    __tablename__ ="Posts"

    # COLUMNS
    id = Column(Integer, primary_key=True, index= True)

    title = Column(String(200), nullable = False)
    # Post title 200 max char

    content = Column(Text, nullable=False)
    #   Full post body (Text unlimited length)

    Published = Column(Boolean, default=False)
    # False = draft, Published= visible to every one

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # onupdate : automatically updates current time when post is edited 

    # Foreign Key 
    # this column stores the ID of the user who wrote the post.
    # ForeignKey("user_id") must be an ID in user table
    # If the user is deleted, their post are deleted too
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship
    author = relationship("User", back_populates="posts")
    # Now post.author gives you the full user object

    comments = relationship("Comment", back_populates="post", cascade="all, delete")

# COMMENT TABLE
# Stores comments on post .
# Each comment belongs to ONE user and ONE post 

class Comment(Base):
    __tablename__ = "comments"

    # Columns_______
    id = Column(Integer, primary_key=True, index=True)

    content = Column(Text, nullable=False)
    # The actual comment text

    creat_at = Column(DateTime, default=datetime.utcnow)

    # Foreighn Keys
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    #Relationship
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")