# Recipe Sharing API - Codebase Documentation

## 📚 Complete Code Explanations with "What" and "Why"

This document provides beginner-friendly explanations for every part of the codebase.

---

## ✅ Files Already Fully Commented

The following files have been updated with comprehensive inline comments:

### Backend Core Files
- ✅ **main.py** - Application entry point with CORS, routing, and static files
- ✅ **database.py** - SQLAlchemy database setup and session management  
- ✅ **app/auth.py** - JWT token creation/validation and password hashing
- ✅ **app/routes/recipes.py** - All recipe CRUD endpoints with file uploads
- ✅ **app/routes/auth.py** - User registration and login endpoints
- ✅ **app/models/recipe.py** - Recipe database model
- ✅ **app/models/ingredient.py** - Ingredient database model
- ✅ **app/services/ai_agent.py** - AI/Ollama integration

### Files With Existing Comments (User Model)

**`app/models/user.py`** - Already has some comments, key concepts:

```python
class User(Base):
    # WHY password_hash: We NEVER store plain passwords (security)
    # WHY pbkdf2_sha256: More flexible than bcrypt (no 72-byte limit)
    password_hash = Column(String, nullable=False)
    
    def set_password(self, password: str):
        # WHY hash before storing: Protects passwords if database is breached
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        # WHY verify method: Securely compares hashes (prevents timing attacks)
        return pwd_context.verify(password, self.password_hash)
```

---

## 📋 Configuration File (`config.py`)

**Current Structure:**

```python
# WHY load_dotenv: Reads .env file for sensitive configuration
# Keeps secrets out of source code (Git)
load_dotenv()

# DATABASE_URL
# WHAT: Connection string for database
# WHY SQLite: Simple, serverless database perfect for development
# Production should use PostgreSQL or MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recipes.db")

# SECRET_KEY
# WHAT: Used to sign JWT tokens (like a password for the API)
# WHY from environment: Different secret for dev/staging/production
# WARNING: MUST change in production or tokens can be forged!
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# ALGORITHM
# WHY HS256: Industry standard HMAC-SHA256 for JWT
ALGORITHM = "HS256"

# ACCESS_TOKEN_EXPIRE_MINUTES
# WHY 30 minutes: Balance between security and user convenience
# Shorter = more secure, Longer = less login prompts
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# File Upload Settings
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
# WHY 5MB images: Large enough for quality, small enough to prevent abuse
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # Convert MB to bytes
# WHY 100MB videos: Videos need more space than images
MAX_VIDEO_SIZE = 100 * 1024 * 1024

# ALLOWED FILE TYPES
# WHY whitelist: Only allow safe, known formats
# WHY set(): Fast membership testing (x in ALLOWED_IMAGE_TYPES)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm"}

# Ollama AI Configuration
# WHY localhost:11434: Ollama's default local server port
# WHY configurable: Can point to remote Ollama instance
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# CORS (Cross-Origin Resource Sharing)
# WHY: Browsers block requests from different origins by default
# WHY split(","): Allows multiple origins from environment variable
# Example: "http://localhost:3000,http://localhost:8080"
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:8000,http://localhost:8080"
).split(",")
```

---

## 🎨 Frontend Files

### **`front-end/index.html`**

All inline styles have been moved to external CSS file for better organization:

```html
<!-- WHY separate CSS file: Keeps styling separate from structure -->
<!-- WHY: Easier to maintain, better caching, cleaner code -->
<link rel="stylesheet" href="style.css">

<!-- WHY .hidden class: Reusable visibility toggle -->
<!-- Better than inline style="display:none" -->
<input type="email" id="email" class="hidden">
```

### **`front-end/style.css`**

```css
/* WHY :root variables: Easy to change colors across entire site */
/* WHY: Consistency + maintainability */
:root {
    --primary-color: #ff6b6b;
    --secondary-color: #4ecdc4;
}

/* WHY .hidden utility class: Reusable across all components */
/* WHY !important: Ensures it always hides (overrides other styles) */
.hidden {
    display: none !important;
}
```

### **`front-end/app.js`**

Key concepts:

```javascript
// WHY API_BASE_URL constant: Easy to change API server address
// WHY 127.0.0.1: More reliable than localhost in some browsers
const API_BASE_URL = 'http://127.0.0.1:8000';

// WHY localStorage: Persists token across page refreshes
// WHY: User stays logged in even after closing browser tab
localStorage.setItem('token', token);

// WHY fetch with Authorization header: JWT token authentication
// Server uses this to identify which user is making the request
fetch(`${API_BASE_URL}/recipes/`, {
    headers: {
        'Authorization': `Bearer ${token}`  // WHY Bearer: OAuth2 standard
    }
})

// WHY try-catch: Network requests can fail (server down, no internet, etc.)
// Prevents app from crashing when errors occur
try {
    const response = await fetch(...);
} catch (error) {
    alert('Error: ' + error.message);
}
```

---

## 🔐 Authentication Flow

**How Login Works (Step-by-Step):**

1. **User enters credentials** → Frontend sends to `/auth/login`
2. **Backend finds user** → Queries database by username
3. **Password verification** → `bcrypt.verify(plain, hash)`
4. **JWT token creation** → Signs token with SECRET_KEY
5. **Token returned** → Frontend stores in localStorage
6. **Protected requests** → Include `Authorization: Bearer ${token}` header
7. **Token validation** → Backend decodes and verifies signature
8. **User identified** → Request proceeds with user_id

**Why JWT (not sessions)?**

- ✅ Stateless: No server-side session storage needed
- ✅ Scalable: Works across multiple servers
- ✅ Mobile-friendly: Easy for mobile apps to use
- ✅ Contains user info: No database lookup needed

---

## 📊 Database Relationships

```
User (1) ←→ (Many) Recipe
  ↓
Recipe (1) ←→ (Many) Ingredient
  ↓
Recipe (1) ←→ (Many) Like
  ↓
Recipe (1) ←→ (Many) Comment
```

**Why these relationships:**

- User can have many recipes (portfolio)
- Recipe has many ingredients (cooking requires multiple items)  
- Recipe can be liked by many users (social feature)
- Recipe can have many comments (community engagement)

**Why `cascade="all, delete-orphan"`:**

- When user is deleted → all their recipes are deleted
- When recipe is deleted → all its ingredients are deleted
- WHY: Prevents orphaned data (ingredients without recipes)
- WHY: GDPR compliance (remove all user data)

---

## 🚀 API Request Flow

**Creating a Recipe (Full Journey):**

```
1. Frontend: User fills form
   ↓
2. Frontend: handleCreateRecipe(e) validates data
   ↓
3. Frontend: fetch('/recipes/', {method: 'POST', body: JSON})
   ↓
4. Backend: CORS middleware checks origin (allowed?)
   ↓
5. Backend: @router.post("/") route matched
   ↓
6. Backend: current_user = Depends(get_current_user)
   ↓
7. Backend: JWT token validated
   ↓
8. Backend: db.add(new_recipe) creates recipe
   ↓
9. Backend: db.add(ingredients) creates each ingredient
   ↓
10. Backend: db.commit() saves to database
    ↓
11. Backend: return RecipeResponse (JSON)
    ↓
12. Frontend: response.json() parses data
    ↓
13. Frontend: showRecipeDetail(recipe.id) displays recipe
```

---

## 🛡️ Security Measures

| What | Why |
|------|-----|
| **Password hashing (bcrypt)** | Attackers can't get real passwords from database |
| **JWT tokens expiration** | Limits damage if token is stolen |
| **CORS configuration** | Prevents unauthorized websites from using API |
| **File type validation** | Prevents malicious file uploads |
| **User ownership checks** | Users can only edit/delete their own recipes |
| **SQL injection protection** | SQLAlchemy parameterizes queries automatically |
| **XSS protection** | Frontend doesn't execute user-submitted HTML |

---

## 🎯 Best Practices Used

1. **Separation of Concerns** - Routes, models, schemas separate
2. **DRY (Don't Repeat Yourself)** - Reusable functions
3. **Type Hints** - Documents expected data types
4. **Error Handling** - try-catch blocks, HTTP status codes
5. **Environment Variables** - Sensitive data in .env
6. **Database Migrations** - SQLAlchemy handles schema changes
7. **API Documentation** - Auto-generated at /docs
8. **Modular Frontend** - Separate HTML, CSS, JS files

---

## 📖 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org
- **JWT Tokens**: https://jwt.io/introduction
- **REST API Design**: https://restfulapi.net
- **Bcrypt Hashing**: https://en.wikipedia.org/wiki/Bcrypt

---

**Questions? Check the inline comments in each file for more detail!**
