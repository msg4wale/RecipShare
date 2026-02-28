# User Stories - Recipe Sharing Application

## Product Vision
Build a social recipe platform where users can create and discover recipes, share cooking media, interact with each other, and get AI-powered cooking help.

## Primary Personas
- Home Cook: wants easy ways to save and share recipes.
- Food Content Creator: wants richer recipe posts with photos/videos.
- Recipe Explorer: wants to browse, like, and comment on recipes.
- Curious Learner: wants contextual cooking guidance from AI.

## Epic 1: Authentication & Account Access

### Story 1.1 - Register Account
As a new user, I want to create an account with username, email, and password so that I can access protected features.

Acceptance Criteria:
- User can submit username, email, and password.
- System rejects duplicate username or email.
- System stores password securely as a hash.
- Successful registration returns created user profile data.

### Story 1.2 - Login and Receive Token
As a registered user, I want to log in and receive an access token so that I can create and manage my own content.

Acceptance Criteria:
- User can log in with valid username and password.
- Invalid credentials return a clear authentication error.
- Successful login returns a JWT access token.
- Token contains user identity and expiration.

## Epic 2: Recipe Management

### Story 2.1 - Create Recipe
As an authenticated user, I want to create a recipe with ingredients so that I can share my cooking ideas.

Acceptance Criteria:
- Only authenticated users can create recipes.
- User can include title, optional description, and ingredient list.
- Ingredients support quantity, unit, and ordering.
- Created recipe is linked to the creator account.

### Story 2.2 - Browse Recipes
As a visitor, I want to view recipe listings so that I can discover content without logging in.

Acceptance Criteria:
- Anyone can fetch recipe list.
- List supports pagination using skip and limit.
- Returned items include key summary fields for display.

### Story 2.3 - View Recipe Details
As a visitor, I want to view full recipe details so that I can understand ingredients and preparation context.

Acceptance Criteria:
- Anyone can request a recipe by id.
- Response includes full ingredient list and media links when available.
- Invalid recipe id returns not-found error.

### Story 2.4 - Update Own Recipe
As a recipe owner, I want to edit my recipe so that I can fix or improve it over time.

Acceptance Criteria:
- Only authenticated owner can update a recipe.
- Non-owner update attempts are forbidden.
- User can update title, description, and ingredients.
- Ingredient updates replace prior ingredient set consistently.

### Story 2.5 - Delete Own Recipe
As a recipe owner, I want to delete my recipe so that I can remove content I no longer want public.

Acceptance Criteria:
- Only authenticated owner can delete a recipe.
- Non-owner delete attempts are forbidden.
- Successful deletion returns no-content response.
- Related recipe data is removed safely.

## Epic 3: Media Uploads

### Story 3.1 - Upload Recipe Image
As a recipe owner, I want to upload an image for my recipe so that others can visually understand the dish.

Acceptance Criteria:
- Only authenticated owner can upload image.
- Uploaded file type must be allowed image mime type.
- File is saved and linked to recipe via image URL.
- Invalid file type returns validation error.

### Story 3.2 - Upload Recipe Video
As a recipe owner, I want to upload a video so that I can demonstrate cooking steps.

Acceptance Criteria:
- Only authenticated owner can upload video.
- Uploaded file type must be allowed video mime type.
- File is saved and linked to recipe via video URL.
- Invalid file type returns validation error.

## Epic 4: Social Interactions

### Story 4.1 - Like and Unlike Recipe
As an authenticated user, I want to like or unlike a recipe so that I can express preference.

Acceptance Criteria:
- Authenticated user can like a recipe.
- User can remove their like (unlike).
- Like counts are retrievable for each recipe.

### Story 4.2 - Comment on Recipe
As an authenticated user, I want to add comments to recipes so that I can share feedback or ask questions.

Acceptance Criteria:
- Authenticated user can add comment text to a recipe.
- Recipe comments can be listed publicly.
- Comment author can delete own comment.

### Story 4.3 - Share Tracking
As a product owner, I want recipe share actions tracked so that I can measure engagement.

Acceptance Criteria:
- Share action endpoint increments/records shares.
- Share counts are retrievable per recipe.

### Story 4.4 - Recipe Engagement Stats
As a user, I want aggregate stats for a recipe so that I can quickly assess its popularity.

Acceptance Criteria:
- Stats endpoint returns likes, comments, and shares counts.
- Stats endpoint works for valid recipe ids.

## Epic 5: AI Cooking Assistant

### Story 5.1 - Ask AI About Recipe
As a user, I want to ask AI questions about a recipe so that I can get contextual cooking guidance.

Acceptance Criteria:
- Authenticated user can ask question tied to a recipe.
- AI prompt uses recipe context (title, description, ingredients).
- Response returns helpful text answer.
- AI service errors are returned with actionable message.

### Story 5.2 - AI Question Suggestions
As a user, I want suggested questions so that I can quickly start useful AI interactions.

Acceptance Criteria:
- Suggestions endpoint returns relevant starter prompts for the recipe.
- Suggestions are recipe-context aware.

## Epic 6: Reliability and Developer Experience

### Story 6.1 - Health Monitoring
As an operator, I want a health endpoint so that I can confirm service availability.

Acceptance Criteria:
- Health endpoint returns service status payload.
- Endpoint responds without authentication.

### Story 6.2 - API Discoverability
As a developer, I want interactive API documentation so that I can test and integrate quickly.

Acceptance Criteria:
- Swagger and ReDoc are available.
- Endpoints are grouped by tags (auth, recipes, interactions, ai-chat).

## Non-Functional Expectations
- Security: JWT-protected routes enforce authentication and ownership checks.
- Validation: Request schemas enforce required fields and constraints.
- Performance: List endpoints support pagination.
- Maintainability: Modular routers, models, schemas, and services.

## MVP Definition
The MVP is complete when users can:
1. Register and log in.
2. Create, browse, view, update, and delete recipes.
3. Upload image/video for owned recipes.
4. Like, comment, share, and view recipe stats.
5. Ask AI questions about a recipe.
