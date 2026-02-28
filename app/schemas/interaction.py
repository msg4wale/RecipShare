from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ShareResponse(BaseModel):
    id: int
    recipe_id: int
    shared_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LikeCountResponse(BaseModel):
    recipe_id: int
    like_count: int

class ShareCountResponse(BaseModel):
    recipe_id: int
    share_count: int

class RecipeStatsResponse(BaseModel):
    recipe_id: int
    like_count: int
    comment_count: int
    share_count: int
