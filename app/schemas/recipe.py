from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class IngredientSchema(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: Optional[str] = None
    order: int = Field(default=0)

    class Config:
        from_attributes = True

class IngredientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: Optional[str] = None
    order: int = Field(default=0)

class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    ingredients: List[IngredientCreate]

class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    ingredients: Optional[List[IngredientCreate]] = None

class RecipeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    ingredients: List[IngredientSchema]
    created_at: datetime

    class Config:
        from_attributes = True

class RecipeListResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
