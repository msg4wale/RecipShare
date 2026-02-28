from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from app.models import Recipe, Comment, Like, Share, User
from app.schemas import CommentCreate, CommentResponse, LikeCountResponse, ShareCountResponse, RecipeStatsResponse
from app.auth import get_current_user

router = APIRouter(prefix="/recipes", tags=["interactions"])

# ========== COMMENTS ==========

@router.post("/{recipe_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    recipe_id: int,
    comment: CommentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Create comment
    new_comment = Comment(
        recipe_id=recipe_id,
        user_id=current_user["user_id"],
        text=comment.text,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment

@router.get("/{recipe_id}/comments", response_model=List[CommentResponse])
def get_comments(recipe_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get all comments for a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    comments = db.query(Comment).filter(
        Comment.recipe_id == recipe_id
    ).offset(skip).limit(limit).all()
    
    return comments

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only by author)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    db.delete(comment)
    db.commit()

# ========== LIKES ==========

@router.post("/{recipe_id}/like", response_model=dict, status_code=status.HTTP_201_CREATED)
def like_recipe(
    recipe_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        (Like.recipe_id == recipe_id) & (Like.user_id == current_user["user_id"])
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this recipe"
        )
    
    # Create like
    new_like = Like(
        recipe_id=recipe_id,
        user_id=current_user["user_id"],
    )
    db.add(new_like)
    db.commit()
    
    return {"message": "Recipe liked successfully"}

@router.delete("/{recipe_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_recipe(
    recipe_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlike a recipe"""
    like = db.query(Like).filter(
        (Like.recipe_id == recipe_id) & (Like.user_id == current_user["user_id"])
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't liked this recipe"
        )
    
    db.delete(like)
    db.commit()

@router.get("/{recipe_id}/likes", response_model=LikeCountResponse)
def get_like_count(recipe_id: int, db: Session = Depends(get_db)):
    """Get the number of likes for a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    like_count = db.query(func.count(Like.id)).filter(Like.recipe_id == recipe_id).scalar()
    
    return {
        "recipe_id": recipe_id,
        "like_count": like_count or 0
    }

# ========== SHARES ==========

@router.post("/{recipe_id}/share", response_model=dict, status_code=status.HTTP_201_CREATED)
def share_recipe(
    recipe_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Create share record
    new_share = Share(
        recipe_id=recipe_id,
        shared_by_user_id=current_user["user_id"],
    )
    db.add(new_share)
    db.commit()
    
    return {"message": "Recipe shared successfully"}

@router.get("/{recipe_id}/shares", response_model=ShareCountResponse)
def get_share_count(recipe_id: int, db: Session = Depends(get_db)):
    """Get the number of shares for a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    share_count = db.query(func.count(Share.id)).filter(Share.recipe_id == recipe_id).scalar()
    
    return {
        "recipe_id": recipe_id,
        "share_count": share_count or 0
    }

# ========== STATS ==========

@router.get("/{recipe_id}/stats", response_model=RecipeStatsResponse)
def get_recipe_stats(recipe_id: int, db: Session = Depends(get_db)):
    """Get statistics for a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    like_count = db.query(func.count(Like.id)).filter(Like.recipe_id == recipe_id).scalar() or 0
    comment_count = db.query(func.count(Comment.id)).filter(Comment.recipe_id == recipe_id).scalar() or 0
    share_count = db.query(func.count(Share.id)).filter(Share.recipe_id == recipe_id).scalar() or 0
    
    return {
        "recipe_id": recipe_id,
        "like_count": like_count,
        "comment_count": comment_count,
        "share_count": share_count
    }
