# Recipe Sharing API

A modern FastAPI-based social platform for sharing recipes with interactive features like likes, comments, media uploads, and an AI-powered chat assistant to answer questions about recipes.

## Features

- 👤 **User Authentication** - Register and login with JWT tokens
- 🍳 **Recipe Management** - Create, read, update, delete recipes with ingredients and quantities
- 🖼️ **Media Uploads** - Upload recipe images and preparation videos
- ❤️ **Interactions** - Like, comment, and share recipes
- 🤖 **AI Chat Agent** - Ask questions about recipes powered by Ollama LLM
- 📊 **Recipe Statistics** - View engagement metrics (likes, comments, shares)
- 🔒 **Secure** - Bearer token authentication for protected endpoints

## Tech Stack

- **Backend Framework**: FastAPI 0.112.2
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt
- **API Server**: Uvicorn
- **Data Validation**: Pydantic 2.8
- **LLM**: Ollama (local, open-source)
- **File Storage**: Local filesystem

## Project Structure

```
proj1/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration and environment variables
├── database.py            # SQLAlchemy setup and database session
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── app/
│   ├── __init__.py
│   ├── auth.py           # JWT and password utilities
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── ingredient.py
│   │   └── interaction.py (Comment, Like, Share)
│   ├── schemas/          # Pydantic validation schemas
│   │   ├── user.py
│   │   ├── recipe.py
│   │   └── interaction.py
│   ├── routes/           # API endpoints
│   │   ├── auth.py       (Register, Login)
│   │   ├── recipes.py    (CRUD + media upload)
│   │   ├── interactions.py (Comments, Likes, Shares)
│   │   └── ai_chat.py    (AI Q&A)
│   └── services/         # Business logic
│       └── ai_agent.py   (Ollama integration)
├── uploads/              # User-uploaded media
└── recipes.db           # SQLite database
```

## Installation

### 1. Prerequisites

- Python 3.8+
- Virtual environment activated (already set up)
- Ollama running locally (for AI features)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment

Copy `.env.example` to `.env` and customize if needed:

```bash
cp .env.example .env
```

Default settings will work for local development.

### 4. Setup Ollama (for AI Chat)

```bash
# Install Ollama from https://ollama.ai
# Run Ollama service
ollama serve

# In another terminal, pull a model
ollama pull llama2
```

## Running the Application

### Start Development Server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and get JWT token

### Recipes
- `POST /recipes` - Create a recipe with ingredients
- `GET /recipes` - List all recipes (paginated)
- `GET /recipes/{id}` - Get recipe details
- `PUT /recipes/{id}` - Update recipe (owner only)
- `DELETE /recipes/{id}` - Delete recipe (owner only)
- `POST /recipes/{id}/upload-image` - Upload recipe image
- `POST /recipes/{id}/upload-video` - Upload recipe video

### Comments
- `POST /recipes/{id}/comments` - Add comment to recipe
- `GET /recipes/{id}/comments` - Get recipe comments
- `DELETE /comments/{id}` - Delete comment (author only)

### Likes
- `POST /recipes/{id}/like` - Like a recipe
- `DELETE /recipes/{id}/like` - Unlike a recipe
- `GET /recipes/{id}/likes` - Get like count

### Shares
- `POST /recipes/{id}/share` - Share a recipe
- `GET /recipes/{id}/shares` - Get share count

### Statistics
- `GET /recipes/{id}/stats` - Get likes, comments, shares count

### AI Chat
- `POST /recipes/{id}/ask` - Ask AI a question about the recipe
- `GET /recipes/{id}/ask-suggestions` - Get suggested questions

## Usage Examples

### 1. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "chef_john",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "chef_john",
  "email": "john@example.com",
  "created_at": "2024-02-22T10:00:00"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "chef_john",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { "id": 1, "username": "chef_john", ... }
}
```

### 3. Create a Recipe

```bash
curl -X POST http://localhost:8000/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Chocolate Chip Cookies",
    "description": "Delicious homemade cookies",
    "ingredients": [
      {"name": "flour", "quantity": 2.25, "unit": "cups"},
      {"name": "butter", "quantity": 1, "unit": "cup"},
      {"name": "sugar", "quantity": 0.75, "unit": "cup"}
    ]
  }'
```

### 4. Upload Recipe Image

```bash
curl -X POST http://localhost:8000/recipes/1/upload-image \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/recipe_image.jpg"
```

### 5. Add a Comment

```bash
curl -X POST http://localhost:8000/recipes/1/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"text": "These cookies are amazing!"}'
```

### 6. Like a Recipe

```bash
curl -X POST http://localhost:8000/recipes/1/like \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 7. Ask AI About Recipe

```bash
curl -X POST http://localhost:8000/recipes/1/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"question": "Can I substitute butter with coconut oil?"}'
```

Response:
```json
{
  "question": "Can I substitute butter with coconut oil?",
  "answer": "Yes, you can substitute butter with coconut oil in a 1:1 ratio. Coconut oil will give your cookies a slightly different texture and flavor...",
  "recipe_id": 1
}
```

## Database Models

### User
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `password_hash` - Hashed password
- `created_at` - Account creation timestamp

### Recipe
- `id` - Primary key
- `user_id` - Owner user ID (foreign key)
- `title` - Recipe name
- `description` - Recipe description
- `image_url` - Path to recipe image
- `video_url` - Path to recipe video
- `created_at` - Recipe creation timestamp

### Ingredient
- `id` - Primary key
- `recipe_id` - Recipe ID (foreign key)
- `name` - Ingredient name
- `quantity` - Amount needed
- `unit` - Measurement unit (cups, grams, etc.)
- `order` - Display order

### Comment
- `id` - Primary key
- `recipe_id` - Recipe ID (foreign key)
- `user_id` - Commenter ID (foreign key)
- `text` - Comment text
- `created_at` - Comment timestamp

### Like
- `id` - Primary key
- `recipe_id` - Recipe ID (foreign key)
- `user_id` - User ID (foreign key)
- `created_at` - Like timestamp
- Unique constraint: One like per user per recipe

### Share
- `id` - Primary key
- `recipe_id` - Recipe ID (foreign key)
- `shared_by_user_id` - Sharer ID (foreign key)
- `created_at` - Share timestamp

## Configuration

Edit `.env` to customize:

```env
# Database
DATABASE_URL=sqlite:///./recipes.db

# JWT
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File uploads
UPLOAD_DIR=./uploads
MAX_IMAGE_SIZE=5242880        # 5MB
MAX_VIDEO_SIZE=104857600      # 100MB

# Ollama AI
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Security Notes

- Always use HTTPS in production
- Change `SECRET_KEY` in production
- Use strong passwords
- Implement rate limiting for production
- Validate file uploads thoroughly
- Add CSRF protection if serving frontend from same domain

## Testing

(Add pytest tests in future implementation)

## Future Enhancements

- [ ] User profiles with follower system
- [ ] Recipe ratings and reviews
- [ ] Search and filter recipes
- [ ] Recipe categories and tags
- [ ] User-to-user messaging
- [ ] Recipe difficulty levels
- [ ] Preparation time estimates
- [ ] Nutritional information
- [ ] Export recipes to PDF
- [ ] Mobile app support
- [ ] Real-time notifications

## Troubleshooting

### Ollama connection error
- Ensure Ollama is running: `ollama serve`
- Check OLLAMA_BASE_URL in .env
- Verify model is downloaded: `ollama list`

### Database issues
- Delete `recipes.db` to reset: `rm recipes.db`
- Database will be recreated on next app start

### Import errors
- Verify virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.8+)

## License

MIT

## Support

For issues, questions, or contributions, please open an issue or submit a pull request.
