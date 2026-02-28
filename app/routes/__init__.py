from .auth import router as auth_router
from .recipes import router as recipes_router
from .interactions import router as interactions_router
from .ai_chat import router as ai_chat_router

__all__ = ["auth_router", "recipes_router", "interactions_router", "ai_chat_router"]
