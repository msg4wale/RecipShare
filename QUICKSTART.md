# Quick Start Guide

Get the Recipe Sharing API up and running in 5 minutes!

## Step 1: Start Ollama (for AI features)

Open a terminal and start the Ollama service:

```bash
ollama serve
```

In another terminal, pull a model:

```bash
ollama pull llama2
```

Wait for the model to download (one-time setup).

## Step 2: Start the API Server

In the project directory:

```bash
cd /Users/ade/Workspace/Dev/proj1

# Activate environment if needed
source env/bin/activate

# Start the server
uvicorn main:app --reload --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 3: Test the API

Open a new terminal and try these commands:

### Register a User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Login
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Your token: $TOKEN"
```

### Create a Recipe
```bash
curl -X POST http://localhost:8000/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Simple Pasta",
    "description": "A quick and easy pasta dish",
    "ingredients": [
      {"name": "pasta", "quantity": 400, "unit": "grams"},
      {"name": "olive oil", "quantity": 2, "unit": "tablespoons"},
      {"name": "garlic", "quantity": 3, "unit": "cloves"}
    ]
  }'
```

### Ask the AI About Your Recipe
```bash
curl -X POST http://localhost:8000/recipes/1/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "What cooking time should I use for the pasta?"}'
```

## Step 4: Explore the API Documentation

Visit the interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from your browser!

## Common Tasks

### Upload a Recipe Image
```bash
curl -X POST http://localhost:8000/recipes/1/upload-image \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

### Like a Recipe
```bash
curl -X POST http://localhost:8000/recipes/1/like \
  -H "Authorization: Bearer $TOKEN"
```

### Add a Comment
```bash
curl -X POST http://localhost:8000/recipes/1/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"text": "This recipe is delicious!"}'
```

### Get Recipe Stats
```bash
curl http://localhost:8000/recipes/1/stats
```

## Troubleshooting

**API won't start?**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that port 8000 is available: `lsof -i :8000`

**Ollama not connecting?**
- Make sure Ollama is running: `ollama serve` in another terminal
- Verify OLLAMA_BASE_URL in .env is correct
- Check connection: `curl http://localhost:11434/api/tags`

**Database errors?**
- Reset database: `rm recipes.db`
- It will be recreated automatically on next start

**JWT token expired?**
- Login again to get a fresh token
- Default expiry is 30 minutes (configurable in .env)

## Next Steps

1. Read the [README.md](README.md) for full documentation
2. Explore the Swagger API docs at http://localhost:8000/docs
3. Customize configuration in `.env`
4. Build a frontend to consume the API
5. Deploy to production (PostgreSQL recommended for prod)

## Tips

- Use `--reload` flag during development for auto-restart
- Check database with: `sqlite3 recipes.db ".tables"`
- View uploaded files in: `./uploads/` directory
- Configure more options in: `config.py`

Enjoy building! 🍳
