# =======================================================================
# main.py - The Entry point of the entire FastAPI application
# Think of this as the "front door" of APP
# Everything starts here
# =======================================================================

from fastapi import FastAPI

# CORSMiddleware allows browsers (frontend apps) to talk to our API
# without this, a React app on localhost:3000 can't call out API
from fastapi.middleware.cors import CORSMiddleware

# We import all our routers ( groups of related routes/ endpoints)
from core.database import engine, Base

# ========================
#Create All database table
# this checks the database and creates any tables
# that don't exists yet ( based on out models)

Base.metadata.create_all(bind=engine)

# ========================
# Create fastAPI application instance 
# Core object - every thing attaches here 

app = FastAPI(
    title="Blog API",
    description="A full-deatured Blog REST API built with FastAPI",
    version="1.0.0",
    docs_url="/docs",  #Swagger UI at /docs
    redoc_url="/redoc"  # Alternative docs at /redov
)

# Core Setting
# CORS = Cross-Origin Resource Sharing 
# This contolds which websites/apps can call out API
# In production, replaces "*" with actual frontend URL
# e.g , ["https://myblong.com"]

app.add_middlewarer(
    CORSMiddleware,
    allow_origin=["*"], # Allow all origin ( fine development)
    allow_credentials=["*"], # Allow cookies/ auth header
    allow_methods=["*"],     # All all the methods
    allow_headers=["*"]      # all all headers
)

# Register Routers
# Routers are like mini-apps 
# each handles a specific section of the API
# The prefix means all routes in that router will starts eith that path.

app.include_router(auth.router,     prefix="/api/auth",     tags=["Authentication"])
app.include_router(users.router,    prefix="/api/users",    tags=["Users"])
app.include_router(posts.router,    prefix="api/posts",     tags=["Posts"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])

# ROOT ENDPOINT 

@app.get("/")
def root():
    return {
        "message": " welcome to Blog API ",
        "docs": "Visit/ docs to explore the API"
    }