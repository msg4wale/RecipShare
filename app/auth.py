"""
Authentication and Authorization Module

WHAT: Handles user authentication (login/register) and JWT token management
WHY: Secures the API - ensures only logged-in users can perform certain actions
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from app.models import User
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context
# WHAT: Configures how passwords are encrypted
# WHY bcrypt: Industry-standard, slow by design to prevent brute-force attacks
# WHY deprecated="auto": Automatically migrates from old hash schemes if needed
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
# WHAT: Tells FastAPI how to extract the JWT token from requests
# WHY tokenUrl="auth/login": Points to the endpoint that issues tokens
# This creates the "Authorize" button in the API docs (/docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain password matches its hashed version.
    
    WHAT: Compares user input with stored hash
    WHY: We never store passwords in plain text for security
    
    Args:
        plain_password: The password the user typed (e.g., "mypassword123")
        hashed_password: The encrypted version from database
        
    Returns:
        bool: True if password is correct, False otherwise
    """
    # WHY pwd_context.verify: Uses bcrypt's secure comparison algorithm
    # WHY not ==: Direct comparison would be vulnerable to timing attacks
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a plain password for storage.
    
    WHAT: Converts plain text password to encrypted hash
    WHY: Security - if database is compromised, attackers can't get real passwords
    
    Example:
        "password123" -> "$2b$12$KIXvZ..." (encrypted, cannot be reversed)
    """
    # WHY pwd_context.hash: Uses bcrypt to create a secure one-way hash
    # WHY "one-way": Cannot reverse the hash back to original password
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token for authenticated users.
    
    WHAT: Generates a signed token containing user info and expiration
    WHY: Tokens allow stateless authentication - no server-side sessions needed
    
    Args:
        data: User information to encode in token (e.g., {"sub": "username"})
        expires_delta: How long until token expires (default from config)
        
    Returns:
        str: The JWT token (long string of encoded data)
    """
    # Make a copy to avoid modifying the original data
    to_encode = data.copy()
    
    # Set expiration time
    # WHY expiration: Security - old tokens become invalid automatically
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use default from config (e.g., 30 minutes)
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration to the token payload
    # WHY "exp": Standard JWT claim for expiration
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    # WHY jwt.encode: Creates a tamper-proof token using SECRET_KEY
    # WHY ALGORITHM: Specifies the signing method (e.g., HS256)
    # Anyone can READ the token, but only we can CREATE valid ones (due to SECRET_KEY)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),  # WHAT: Extracts token from Authorization header
    db: Session = Depends(get_db)
):
    """
    Validate JWT token and return the current user.
    
    WHAT: Dependency that protects endpoints - verifies user is logged in
    WHY: Prevents unauthorized access to protected routes
    
    Flow:
    1. Extract token from request header
    2. Decode and verify signature
    3. Check if user exists in database
    4. Return user info
    
    Usage in routes:
        @router.get("/protected")
        def protected_route(current_user: dict = Depends(get_current_user)):
            # This only runs if token is valid
    """
    # Define exception for invalid credentials
    # WHY 401 Unauthorized: User failed to authenticate
    # WHY WWW-Authenticate header: Required by OAuth2 standard
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        # WHY jwt.decode: Verifies signature and expiration
        # If SECRET_KEY doesn't match or token expired, this raises JWTError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract username from token
        # WHY "sub": Standard JWT claim for "subject" (the user identifier)
        username: str = payload.get("sub")
        
        if username is None:
            # Token is valid but missing username
            raise credentials_exception
            
    except JWTError:
        # Token is invalid, expired, or tampered with
        # WHY: Raise exception to stop request processing
        raise credentials_exception
    
    # Look up user in database
    # WHY: Ensure user still exists (they might have been deleted)
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        # Valid token but user no longer exists
        raise credentials_exception
    
    # Return user information that routes can use
    # WHY dict format: Easy to access user_id, username, etc. in routes
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }
