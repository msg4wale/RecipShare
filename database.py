"""
Database Configuration and Session Management

WHAT: Sets up SQLAlchemy ORM connection to SQLite database
WHY: Provides a Pythonic way to interact with database (no raw SQL needed)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL
# WHAT: Specifies which database to use and where it's located
# WHY SQLite: Simple, serverless database perfect for development
# WHY recipes.db: The file that stores all our data
# WHY check_same_thread=False: Allows SQLite to work with FastAPI's async nature
SQLALCHEMY_DATABASE_URL = "sqlite:///./recipes.db"

# Create database engine
# WHAT: The engine manages connections to the database
# WHY connect_args: Required for SQLite to work with multiple threads
# Think of engine as the "car" that drives to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session factory
# WHAT: SessionLocal is a class that creates database sessions
# WHY: Each request gets its own session (prevents data conflicts)
# Think of sessions as "conversations" with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
# WHAT: All our models (Recipe, User, etc.) inherit from this
# WHY: Provides common functionality for all database models
# This is where SQLAlchemy "magic" comes from
Base = declarative_base()

def get_db():
    """
    Dependency that provides a database session to routes.
    
    WHAT: Creates a new database session for each request
    WHY: Ensures each request has its own isolated database connection
    WHY yield: Automatically closes the session when request is done
    
    Usage in routes:
        @router.get("/recipes")
        def get_recipes(db: Session = Depends(get_db)):
            # db is a fresh database session
            # It will automatically close when function returns
    """
    # Create a new database session
    db = SessionLocal()
    
    try:
        # Provide the session to the route
        # WHY yield: Makes this a generator - session stays open during request
        yield db
    finally:
        # Clean up: close the session when request is complete
        # WHY finally: This runs even if an error occurred
        # WHY close: Releases database connection back to the pool
        db.close()
