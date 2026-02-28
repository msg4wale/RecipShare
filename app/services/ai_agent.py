import httpx
import json
from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from typing import Optional

async def query_ollama(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Query the Ollama LLM with a prompt
    
    Args:
        prompt: The user's question/prompt
        system_prompt: Optional system message to set the AI's behavior
    
    Returns:
        The AI's response text
    """
    try:
        async with httpx.AsyncClient() as client:
            # Prepare the message
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Call Ollama API
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                },
                timeout=60.0,
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")
            
            # Extract response text
            data = response.json()
            return data.get("message", {}).get("content", "")
    
    except httpx.ConnectError:
        raise Exception(f"Could not connect to Ollama at {OLLAMA_BASE_URL}. Make sure Ollama is running.")
    except Exception as e:
        raise Exception(f"Error querying Ollama: {str(e)}")

def format_recipe_context(recipe) -> str:
    """
    Format recipe data into a context string for the AI
    
    Args:
        recipe: Recipe object with ingredients and other data
    
    Returns:
        Formatted recipe context
    """
    context = f"""
Recipe: {recipe.title}

Description: {recipe.description or "No description provided"}

Ingredients:
"""
    
    for ingredient in recipe.ingredients:
        context += f"- {ingredient.quantity} {ingredient.unit or ''} {ingredient.name}\n"
    
    return context

async def ask_recipe_question(recipe, question: str) -> str:
    """
    Ask a question about a specific recipe using the AI agent
    
    Args:
        recipe: Recipe object with ingredients and other data
        question: User's question about the recipe
    
    Returns:
        AI's response to the question
    """
    # Create system prompt
    system_prompt = """You are a helpful cooking assistant. You help users understand recipes, 
    suggest modifications, answer cooking questions, and provide cooking tips. Be concise and practical."""
    
    # Format recipe context
    recipe_context = format_recipe_context(recipe)
    
    # Combine context with user question
    full_prompt = f"""{recipe_context}

User Question: {question}

Please provide a helpful answer based on the recipe information above."""
    
    # Query Ollama
    response = await query_ollama(full_prompt, system_prompt)
    return response
