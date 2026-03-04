# core/database.py — DATABASE CONNECTION SETUP
# This file handles everythng related to connecting to Database
# Using SQLite for simplicity 

#SQLAlchemy is ORM (object Relational Mapper )
# ORL = lets you write python classes instead of raw SQL

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL 

DATABASE_URL = "sqlite:///./blog.db"

# PostgreSQL ( production ready , )

# DATABASE_URL ="pstgresql://user:password@localhost/blog_db"

# Create engine
# Engine is actual connection to the database
# connect_args is neede only for SQLite(not for PostgreSQL)
# It allows multiple threads to use the same connection.

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}  # remove for PostgreSQL
)

# Session factory 
#  A session is like conversation with database.
# Every API request gets its own session to read/write data.

SessionLocal = sessionmaker(
    autocommit = False, # we manually control when to save changes
    autoflush = False, # we control when to sync changes to DB
    bind = engine
)

# BASE CLASS
# ALl our database models (user, post, commit)
# will inherit from this Base class.
# SQLAlchemy uses it to track which classes are tables.

Base = declarative_base()

# Get DATABASE SESSION (DEPENDENCY)
# FastAPI calls this function before running any endpoint that needs DB

# yeild means give the session to the endpoint 
# and when the endpoint is done , run the cleanup, (db.close())
# this ensures the DB connection is ALWAYS closed,
# even if an error occurs

def get_db():
    db = SessionLocal() #open a new session
    try:
        yield db        # Give it to the end-point
    finally:
        db.close()      # Always close when done