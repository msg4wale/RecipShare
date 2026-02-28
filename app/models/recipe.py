"""Recipe Model - Database representation of recipes

WHAT: Defines the structure of the recipes table
WHY: Core feature - stores all recipe information users share
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Recipe(Base):
    """Recipe model with ingredients, media, and user relationships.
    
    WHAT: Represents a cooking recipe in the database
    WHY: Main content type of the application
    
    Relationships:
    - Belongs to one user (many-to-one)
    - Has many ingredients (one-to-many)
    - Has many likes (one-to-many)
    - Has many comments (one-to-many)
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="recipe", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="recipe", cascade="all, delete-orphan")
    shares = relationship("Share", back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recipe(id={self.id}, title={self.title}, user_id={self.user_id})>"
