from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from app.models import Recipe
from app.auth import get_current_user
from app.services.ai_agent import ask_recipe_question

router = APIRouter(prefix="/recipes", tags=["ai"])

class RecipeQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)

class RecipeAnswerResponse(BaseModel):
    question: str
    answer: str
    recipe_id: int

@router.post("/{recipe_id}/ask", response_model=RecipeAnswerResponse)
async def ask_about_recipe(
    recipe_id: int,
    request: RecipeQuestionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask the AI assistant a question about a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    try:
        # Get AI response
        answer = await ask_recipe_question(recipe, request.question)
        
        return {
            "question": request.question,
            "answer": answer,
            "recipe_id": recipe_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )

@router.get("/{recipe_id}/ask-suggestions")
async def get_question_suggestions(recipe_id: int, db: Session = Depends(get_db)):
    """Get suggested questions for a recipe"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Return some helpful suggestion questions
    suggestions = [
        "What are some tips for preparing this recipe?",
        "Can I substitute any of the ingredients?",
        "How long does this recipe take to prepare?",
        "What cooking techniques are important for this recipe?",
        "How should I store leftovers from this recipe?",
        "Are there any variations of this recipe?",
    ]
    
    return {"recipe_id": recipe_id, "suggestions": suggestions}
