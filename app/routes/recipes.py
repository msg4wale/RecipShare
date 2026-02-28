import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from app.models import Recipe, Ingredient, User
from app.schemas import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeListResponse, IngredientSchema
from app.auth import get_current_user
from config import UPLOAD_DIR, MAX_IMAGE_SIZE, MAX_VIDEO_SIZE, ALLOWED_IMAGE_TYPES, ALLOWED_VIDEO_TYPES
import shutil

# Create a router for recipe-related endpoints
# WHY: APIRouter groups related endpoints together for better code organization
# The prefix="/recipes" means all routes here automatically start with /recipes
# The tags=["recipes"] groups these endpoints in the API documentation
router = APIRouter(prefix="/recipes", tags=["recipes"])

def save_upload_file(file: UploadFile, recipe_id: int, file_type: str) -> str:
    """
    Save an uploaded file (image or video) to the server's filesystem.
    
    WHAT: Takes an uploaded file and saves it to a directory specific to the recipe
    WHY: We store files locally to associate media with recipes and serve them later
    
    Args:
        file: The uploaded file from the user
        recipe_id: The ID of the recipe this file belongs to
        file_type: Either "image" or "video" to determine validation rules
        
    Returns:
        str: The URL path where the file can be accessed (e.g., /uploads/1/abc123.jpg)
    """
    # Create a unique directory for this recipe's uploads
    # WHY: Organizing files by recipe_id makes it easier to find and delete related files
    recipe_upload_dir = os.path.join(UPLOAD_DIR, str(recipe_id))
    os.makedirs(recipe_upload_dir, exist_ok=True)  # exist_ok=True prevents errors if directory exists
    
    # Set validation rules based on file type
    # WHY: Images and videos have different size and format requirements
    if file_type == "image":
        max_size = MAX_IMAGE_SIZE
        allowed_types = ALLOWED_IMAGE_TYPES
    else:  # video
        max_size = MAX_VIDEO_SIZE
        allowed_types = ALLOWED_VIDEO_TYPES
    
    # Validate the file's MIME type (e.g., image/jpeg, video/mp4)
    # WHY: Prevents users from uploading malicious or unsupported file types
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {allowed_types}"
        )
    
    # Generate a unique filename using UUID (Universally Unique Identifier)
    # WHY: Prevents filename collisions if two users upload files with the same name
    # WHY: UUID ensures the filename is unique across all uploads
    file_ext = os.path.splitext(file.filename)[1]  # Extract extension (.jpg, .png, etc.)
    filename = f"{uuid.uuid4()}{file_ext}"  # e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg"
    file_path = os.path.join(recipe_upload_dir, filename)
    
    # Save the file to disk
    # WHY: We use a try-except block because file operations can fail (disk full, permissions, etc.)
    try:
        with open(file_path, "wb") as buffer:  # "wb" = write binary mode
            # Copy the uploaded file's content to our local file
            # WHY: shutil.copyfileobj efficiently handles large files in chunks
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        # If anything goes wrong, return a 500 error
        # WHY: Better to fail gracefully than leave partial/corrupted files
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Return the URL path that can be used to access this file
    # WHY: The frontend needs this URL to display the image/video in the browser
    return f"/uploads/{recipe_id}/{filename}"

@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe: RecipeCreate,  # WHAT: The recipe data from the request body
    current_user: dict = Depends(get_current_user),  # WHAT: Authenticated user info from JWT token
    db: Session = Depends(get_db)  # WHAT: Database session for queries
):
    """
    Create a new recipe with its ingredients.
    
    WHAT: Accepts recipe data, validates it, and saves to database
    WHY: This is the main endpoint for users to share their recipes
    
    Flow:
    1. User sends recipe data (title, description, ingredients)
    2. We verify they're logged in (current_user)
    3. Create recipe in database
    4. Create each ingredient linked to that recipe
    5. Return the complete recipe with auto-generated ID
    
    WHY response_model=RecipeResponse: Ensures the response matches our schema
    WHY status_code=201: RESTful convention - 201 means "Created successfully"
    """
    # Create the main recipe object
    # WHY: We link it to the current user so we know who created it
    new_recipe = Recipe(
        user_id=current_user["user_id"],  # Associate recipe with the logged-in user
        title=recipe.title,
        description=recipe.description,
    )
    
    # Add to database session but don't commit yet
    # WHY: We need the recipe ID before we can create ingredients
    db.add(new_recipe)
    db.flush()  # WHAT: Assigns an ID to new_recipe without finalizing the transaction
                # WHY: We need the recipe.id to link ingredients to this recipe
    
    # Create each ingredient and link it to the recipe
    # WHY enumerate: Maintains the order of ingredients for display (1st, 2nd, 3rd, etc.)
    for idx, ingredient in enumerate(recipe.ingredients):
        new_ingredient = Ingredient(
            recipe_id=new_recipe.id,  # Link to the recipe we just created
            name=ingredient.name,
            quantity=ingredient.quantity,
            unit=ingredient.unit,
            order=idx,  # Store the position (important for cooking steps)
        )
        db.add(new_ingredient)
    
    # Commit all changes to database (recipe + all ingredients)
    # WHY: If anything fails, the entire transaction rolls back (all-or-nothing)
    db.commit()
    
    # Refresh to get the complete object with all relationships loaded
    # WHY: Ensures we return the recipe with its ingredients list populated
    db.refresh(new_recipe)
    
    return new_recipe

@router.get("/", response_model=List[RecipeListResponse])
def get_recipes(
    skip: int = 0,  # WHAT: How many recipes to skip (for pagination)
    limit: int = 10,  # WHAT: Maximum number of recipes to return
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of all recipes.
    
    WHAT: Returns recipes with pagination support
    WHY: Pagination prevents loading thousands of recipes at once (performance)
    
    Example: /recipes?skip=0&limit=10 returns first 10 recipes
             /recipes?skip=10&limit=10 returns recipes 11-20
    
    WHY no authentication required: Public recipes should be viewable by anyone
    """
    # Query the database for recipes with pagination
    # WHY offset(skip): Skips the first 'skip' recipes (for page 2, 3, etc.)
    # WHY limit(limit): Only returns up to 'limit' recipes (prevents overwhelming client)
    recipes = db.query(Recipe).offset(skip).limit(limit).all()
    
    return recipes

@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,  # WHAT: The ID from the URL path (e.g., /recipes/5)
    db: Session = Depends(get_db)
):
    """
    Get a single recipe by its ID.
    
    WHAT: Returns complete recipe details including all ingredients
    WHY: Users need to see full recipe information before cooking
    
    WHY {recipe_id} in path: RESTful convention for accessing specific resources
    """
    # Search for the recipe in the database
    # WHY .first(): Returns the recipe or None if not found
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    # Handle case where recipe doesn't exist
    # WHY 404: RESTful convention - "Not Found" is the appropriate status code
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return recipe

@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,  # WHAT: The updated recipe data (all fields optional)
    current_user: dict = Depends(get_current_user),  # WHY: Only logged-in users can update
    db: Session = Depends(get_db)
):
    """
    Update an existing recipe (only by the owner).
    
    WHAT: Allows recipe owner to modify title, description, or ingredients
    WHY: Users need to fix typos or improve their recipes over time
    
    Security: Only the user who created the recipe can update it
    """
    # Find the recipe in the database
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    # Check if recipe exists
    # WHY: Can't update something that doesn't exist
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Verify ownership - only the creator can modify
    # WHY: Security - prevents users from modifying other people's recipes
    # WHY 403 Forbidden: User is authenticated but not authorized for this action
    if db_recipe.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this recipe"
        )
    
    # Update recipe fields if provided
    # WHY we check 'if recipe.title': Only update fields that were sent
    # This allows partial updates (user can update just title without changing description)
    if recipe.title:
        db_recipe.title = recipe.title
    if recipe.description is not None:  # WHY check 'is not None': Allows setting to empty string
        db_recipe.description = recipe.description
    
    # Update ingredients if provided
    if recipe.ingredients:
        # Delete all existing ingredients first
        # WHY: Simpler to delete all and recreate than to update individual items
        # This handles additions, removals, and reordering in one operation
        db.query(Ingredient).filter(Ingredient.recipe_id == recipe_id).delete()
        
        # Add the new ingredients
        for idx, ingredient in enumerate(recipe.ingredients):
            new_ingredient = Ingredient(
                recipe_id=recipe_id,
                name=ingredient.name,
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                order=idx,
            )
            db.add(new_ingredient)
    
    # Save all changes to database
    db.commit()
    db.refresh(db_recipe)  # Reload with updated relationships
    
    return db_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a recipe (only by the owner).
    
    WHAT: Permanently removes a recipe and all its ingredients
    WHY: Users should be able to remove recipes they no longer want to share
    
    WHY 204 No Content: RESTful convention - successful deletion returns no body
    """
    # Find the recipe
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    # Verify it exists
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Verify ownership
    # WHY: Security - only the creator can delete their recipe
    if db_recipe.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this recipe"
        )
    
    # Delete the recipe
    # WHY: SQLAlchemy's cascade settings will automatically delete related ingredients
    db.delete(db_recipe)
    db.commit()
    
    # WHY no return: 204 status means "success but no content to return"

@router.post("/{recipe_id}/upload-image")
def upload_recipe_image(
    recipe_id: int,
    file: UploadFile = File(...),  # WHAT: The uploaded image file
                                    # WHY File(...): FastAPI knows to expect multipart/form-data
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an image for a recipe.
    
    WHAT: Accepts an image file and associates it with a recipe
    WHY: Visual appeal - users want to see what the dish looks like
    
    Flow:
    1. Verify recipe exists and user owns it
    2. Save image to filesystem
    3. Update recipe with image URL
    4. Return the URL for frontend to display
    """
    # Find the recipe
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    # Verify existence
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Verify ownership
    # WHY: Only recipe owner should be able to change its image
    if db_recipe.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload to this recipe"
        )
    
    # Save the file to disk and get URL
    # WHY separate function: Reusable for both images and videos
    image_url = save_upload_file(file, recipe_id, "image")
    
    # Update the recipe's image_url field
    # WHY: Frontend needs this URL to display the image
    db_recipe.image_url = image_url
    db.commit()
    db.refresh(db_recipe)
    
    # Return just the URL
    # WHY: Frontend immediately needs this to preview the uploaded image
    return {"image_url": image_url}

@router.post("/{recipe_id}/upload-video")
def upload_recipe_video(
    recipe_id: int,
    file: UploadFile = File(...),  # WHAT: The uploaded video file
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a cooking video for a recipe.
    
    WHAT: Accepts a video file and associates it with a recipe
    WHY: Video tutorials are extremely helpful for complex cooking techniques
    
    Note: Very similar to upload_image but uses video validation rules
    """
    # Find the recipe
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    # Verify existence
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Verify ownership
    if db_recipe.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload to this recipe"
        )
    
    # Save the video file
    # WHY "video" parameter: Uses different size/type validation than images
    video_url = save_upload_file(file, recipe_id, "video")
    
    # Update the recipe's video_url field
    db_recipe.video_url = video_url
    db.commit()
    db.refresh(db_recipe)
    
    return {"video_url": video_url}
