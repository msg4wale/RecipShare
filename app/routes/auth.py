"""Authentication Routes - User registration and login endpoints

WHAT: Handles user account creation and authentication
WHY: Users need accounts to create recipes and interact with content
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse
from app.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Create router for authentication endpoints
# WHY prefix="/auth": All routes start with /auth (e.g., /auth/login)
# WHY tags=["auth"]: Groups these in API documentation
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account.
    
    WHAT: Creates a new user in the database
    WHY: Users need accounts to create and share recipes
    
    Flow:
    1. Check if username/email already exists
    2. Hash the password (security)
    3. Create user in database
    4. Return user info (but not password)
    
    WHY 201 Created: RESTful convention for successful resource creation
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    # If user already exists, reject the registration
    # WHY 400 Bad Request: Client error - they sent invalid data
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    
    # Create new user object
    # WHY: Instantiate the User model with provided data
    new_user = User(
        username=user.username,
        email=user.email,
    )
    
    # Hash and store password securely
    # WHY set_password method: Handles bcrypt hashing internally
    # WHY not direct assignment: Never store plain text passwords
    new_user.set_password(user.password)
    
    # Add to database and save
    # WHY add then commit: Standard SQLAlchemy pattern
    db.add(new_user)
    db.commit()  # Actually saves to database
    
    # Refresh to get the auto-generated ID
    # WHY: Database assigns the ID, we need to read it back
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and issue JWT token.
    
    WHAT: Verifies username/password and returns access token
    WHY: Users need tokens to access protected endpoints
    
    Flow:
    1. Look up user by username
    2. Verify password matches
    3. Create JWT token with user info
    4. Return token to client
    
    Security: Token expires after configured time (default 30 min)
    """
    # Find user by username
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not db_user.verify_password(user.password):
        # Authentication failed
        # WHY 401 Unauthorized: Standard code for failed authentication
        # WHY "Invalid username or password": Don't reveal which one was wrong (security)
        # WHY WWW-Authenticate header: Required by OAuth2 specification
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token that expires after configured time
    # WHY timedelta: Tokens should expire for security
    # WHY from config: Makes it easy to adjust expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Generate the actual JWT token
    # WHY "sub": JWT standard claim for "subject" (the user ID)
    # WHY str(db_user.id): Convert to string (JWT spec requires string subjects)
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }
