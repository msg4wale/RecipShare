"""Ingredient Model - Database representation of recipe ingredients

WHAT: Defines the structure of ingredients table
WHY: Recipes need ingredients with quantities and units
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Ingredient(Base):
    """Ingredient model - belongs to a recipe.
    
    WHAT: Represents one ingredient in a recipe (e.g., "200g pasta")
    WHY: Recipes need structured ingredient lists with quantities
    
    Example:
        name="pasta", quantity=200, unit="grams", order=0
    """
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=True)  # e.g., "cups", "grams", "tablespoons"
    order = Column(Integer, nullable=False)  # Order in which ingredients appear
    
    # Relationship
    recipe = relationship("Recipe", back_populates="ingredients")

    def __repr__(self):
        return f"<Ingredient(id={self.id}, recipe_id={self.recipe_id}, name={self.name}, qty={self.quantity} {self.unit})>"
