from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, recipe_id={self.recipe_id}, user_id={self.user_id})>"


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite unique constraint: one user can like one recipe only once
    __table_args__ = (UniqueConstraint('recipe_id', 'user_id', name='_recipe_user_uc'),)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="likes")

    def __repr__(self):
        return f"<Like(id={self.id}, recipe_id={self.recipe_id}, user_id={self.user_id})>"


class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)
    shared_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="shares")

    def __repr__(self):
        return f"<Share(id={self.id}, recipe_id={self.recipe_id}, user_id={self.shared_by_user_id})>"
