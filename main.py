"""Main Application Entry Point

WHAT: FastAPI application setup and configuration
WHY: Initializes the web server and connects all components
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from database import create_tables
from config import ALLOWED_ORIGINS, UPLOAD_DIR
from app.routes import auth_router, recipes_router, interactions_router, ai_chat_router

# Create all database tables if they don't exist
# WHY on startup: Ensures database is ready before handling requests
# WHY: Automatically sets up fresh databases (great for development)
create_tables()

# Create the main FastAPI application instance
# WHY title/description: Shows up in API documentation (/docs)
# WHY version: Helps track API changes over time
app = FastAPI(
    title="Recipe Sharing API",
    description="A social platform for sharing recipes with likes, comments, and AI-powered Q&A",
    version="1.0.0"
)

# Add CORS middleware to handle cross-origin requests
# WHAT: Allows frontend (on different port/domain) to access API
# WHY: Browsers block cross-origin requests by default for security
# WHY allow_origins=["*"]: Development mode - allows any website access
# WARNING: Change to specific domains in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Which websites can access ("*" = all)
    allow_credentials=True,        # Allow cookies/auth headers
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],           # Allow all HTTP headers
)

# Set up static file serving for uploaded images/videos
# WHAT: Makes uploaded files accessible via URL
# WHY: Frontend needs to display images from /uploads/... URLs

# Create uploads directory if it doesn't exist
# WHY: Prevents errors when trying to save first file
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Mount the uploads directory as static files
# WHY mount: Makes files in ./uploads accessible at /uploads URL
# Example: ./uploads/1/image.jpg becomes http://localhost:8000/uploads/1/image.jpg
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers - connects route modules to main app
# WHY separate routers: Organizes code by feature (auth, recipes, etc.)
# WHY include_router: Registers all routes from each router
app.include_router(auth_router)         # /auth/login, /auth/register
app.include_router(recipes_router)      # /recipes/...
app.include_router(interactions_router) # /recipes/{id}/like, comments
app.include_router(ai_chat_router)      # /recipes/{id}/ask

# Health check endpoint
# WHAT: Simple endpoint to verify API is running
# WHY: Useful for monitoring, load balancers, automated tests
@app.get("/health")
def health_check():
    """Health check endpoint.
    
    WHAT: Returns API status
    WHY: Monitoring tools and load balancers use this to check if server is alive
    """
    return {
        "status": "healthy",
        "service": "Recipe Sharing API"
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to Recipe Sharing API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
