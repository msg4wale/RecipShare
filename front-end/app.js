const API_BASE_URL = 'http://127.0.0.1:8000';
let currentUser = null;
let currentRecipeId = null;
let isLogin = true;

// Show/Hide Sections
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

function showHome() {
    showSection('home');
}

function showAuth() {
    isLogin = true;
    document.getElementById('authTitle').textContent = 'Login';
    document.getElementById('email').style.display = 'none';
    document.querySelector('.toggle-auth').innerHTML = "Don't have an account? <a href='#' onclick='toggleAuth()'>Register</a>";
    showSection('auth');
}

function showRecipes() {
    showSection('recipes');
    loadRecipes();
}

function showCreateRecipe() {
    showSection('createRecipe');
    document.getElementById('recipeForm').reset();
    document.getElementById('ingredientsList').innerHTML = '';
    addIngredient();
}

function showRecipeDetail(recipeId) {
    currentRecipeId = recipeId;
    showSection('recipeDetail');
    loadRecipeDetail(recipeId);
}

// Toggle Auth Mode
function toggleAuth() {
    isLogin = !isLogin;
    const emailInput = document.getElementById('email');
    const toggleText = document.querySelector('.toggle-auth');
    
    if (isLogin) {
        document.getElementById('authTitle').textContent = 'Login';
        emailInput.style.display = 'none';
        emailInput.removeAttribute('required');
        toggleText.innerHTML = "Don't have an account? <a href='#' onclick='toggleAuth()'>Register</a>";
    } else {
        document.getElementById('authTitle').textContent = 'Register';
        emailInput.style.display = 'block';
        emailInput.setAttribute('required', 'required');
        toggleText.innerHTML = "Already have an account? <a href='#' onclick='toggleAuth()'>Login</a>";
    }
}

// Auth Handler
async function handleAuth(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;
    
    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    const payload = isLogin 
        ? { username, password }
        : { username, email, password };
    
    try {
        console.log(`Sending ${isLogin ? 'login' : 'register'} request to ${API_BASE_URL}${endpoint}/`);
        const response = await fetch(`${API_BASE_URL}${endpoint}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        console.log(`Response status: ${response.status}`);
        const data = await response.json();
        console.log(`Response data:`, data);
        
        if (response.ok) {
            if (isLogin) {
                const token = data.access_token;
                console.log(`Token received: ${token.substring(0, 20)}... (length: ${token.length})`);
                localStorage.setItem('token', token);
                currentUser = username;
                updateAuthUI();
                showHome();
                alert('Logged in successfully!');
            } else {
                alert('Account created! Please log in.');
                isLogin = true;
                document.getElementById('authForm').reset();
                document.getElementById('email').style.display = 'none';
            }
        } else {
            alert('Error: ' + (data.detail || 'Authentication failed'));
        }
    } catch (error) {
        console.error('Fetch error:', error);
        alert('Error: ' + error.message);
    }
}

// Update Auth UI
function updateAuthUI() {
    const token = localStorage.getItem('token');
    const authLink = document.getElementById('authLink');
    const logoutLink = document.getElementById('logoutLink');
    const createBtn = document.getElementById('createBtn');
    
    if (token) {
        authLink.style.display = 'none';
        logoutLink.style.display = 'block';
        if (createBtn) createBtn.style.display = 'inline-block';
    } else {
        authLink.style.display = 'block';
        logoutLink.style.display = 'none';
        if (createBtn) createBtn.style.display = 'none';
    }
}

// Logout
function logout() {
    localStorage.removeItem('token');
    currentUser = null;
    updateAuthUI();
    showHome();
}

// Load Recipes
async function loadRecipes() {
    try {
        console.log(`Fetching recipes from ${API_BASE_URL}/recipes/`);
        const response = await fetch(`${API_BASE_URL}/recipes/`);
        console.log(`Recipes response status: ${response.status}`);
        
        const recipes = await response.json();
        console.log(`Recipes data:`, recipes);
        
        const recipesList = document.getElementById('recipesList');
        recipesList.innerHTML = '';
        
        if (!recipes || recipes.length === 0) {
            recipesList.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No recipes yet. Create one!</p>';
            return;
        }
        
        recipes.forEach(recipe => {
            const card = createRecipeCard(recipe);
            recipesList.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading recipes:', error);
        alert('Error loading recipes: ' + error.message);
    }
}

function createRecipeCard(recipe) {
    const card = document.createElement('div');
    card.className = 'recipe-card';
    card.onclick = () => showRecipeDetail(recipe.id);
    
    card.innerHTML = `
        <div class="recipe-card-image">${recipe.image_url ? `<img src="${recipe.image_url}" alt="${recipe.title}">` : '🍳'}</div>
        <div class="recipe-card-content">
            <h3>${recipe.title}</h3>
            <p>${recipe.description.substring(0, 100)}...</p>
            <div class="recipe-card-stats">
                <span>❤️ ${recipe.likes || 0}</span>
                <span>💬 ${recipe.comments_count || 0}</span>
            </div>
        </div>
    `;
    
    return card;
}

// Load Recipe Detail
async function loadRecipeDetail(recipeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/`);
        const recipe = await response.json();
        
        document.getElementById('detailTitle').textContent = recipe.title;
        document.getElementById('detailDescription').textContent = recipe.description;
        document.getElementById('detailLikes').textContent = recipe.likes || 0;
        document.getElementById('detailComments').textContent = recipe.comments_count || 0;
        
        if (recipe.image_url) {
            document.getElementById('detailImage').src = recipe.image_url;
        }
        
        // Load ingredients
        const ingredientsList = document.getElementById('detailIngredients');
        ingredientsList.innerHTML = '';
        if (recipe.ingredients && recipe.ingredients.length > 0) {
            recipe.ingredients.forEach(ing => {
                const li = document.createElement('li');
                li.textContent = `${ing.name} - ${ing.quantity} ${ing.unit}`;
                ingredientsList.appendChild(li);
            });
        }
        
        // Show like button if logged in
        const likeBtn = document.getElementById('likeBtn');
        if (localStorage.getItem('token')) {
            likeBtn.style.display = 'block';
        } else {
            likeBtn.style.display = 'none';
        }
        
        document.getElementById('aiMessages').innerHTML = '';
    } catch (error) {
        console.error('Error loading recipe:', error);
        alert('Error loading recipe: ' + error.message);
    }
}

// Create Recipe
async function handleCreateRecipe(e) {
    e.preventDefault();
    
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login first');
        return;
    }
    
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const ingredients = [];
    
    document.querySelectorAll('.ingredient-item').forEach(item => {
        const name = item.querySelector('.ingredient-name').value;
        const quantity = item.querySelector('.ingredient-quantity').value;
        const unit = item.querySelector('.ingredient-unit').value;
        
        if (name && quantity && unit) {
            ingredients.push({ name, quantity: parseFloat(quantity), unit });
        }
    });
    
    if (ingredients.length === 0) {
        alert('Please add at least one ingredient');
        return;
    }
    
    const payload = { title, description, ingredients };
    
    try {
        console.log(`Creating recipe with token: ${token.substring(0, 20)}...`);
        const response = await fetch(`${API_BASE_URL}/recipes/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        
        console.log(`Create recipe response status: ${response.status}`);
        const data = await response.json();
        console.log(`Create recipe response data:`, data);
        
        if (response.ok) {
            const recipe = data;
            
            // Upload image if provided
            const imageFile = document.getElementById('recipeImage').files[0];
            if (imageFile) {
                const formData = new FormData();
                formData.append('file', imageFile);
                
                await fetch(`${API_BASE_URL}/recipes/${recipe.id}/upload-image/`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });
            }
            
            alert('Recipe created successfully!');
            showRecipes();
        } else {
            alert('Error creating recipe: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error creating recipe:', error);
        alert('Error: ' + error.message);
    }
}

// Add Ingredient
function addIngredient() {
    const container = document.getElementById('ingredientsList');
    const item = document.createElement('div');
    item.className = 'ingredient-item';
    item.innerHTML = `
        <input type="text" class="ingredient-name" placeholder="Ingredient name" required>
        <input type="number" class="ingredient-quantity" placeholder="Quantity" step="0.1" required>
        <input type="text" class="ingredient-unit" placeholder="Unit (g, ml, tsp, etc)" required>
        <button type="button" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(item);
}

// Like Recipe
async function likeRecipe() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login first');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${currentRecipeId}/like/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            loadRecipeDetail(currentRecipeId);
            alert('Recipe liked!');
        }
    } catch (error) {
        console.error('Error liking recipe:', error);
        alert('Error: ' + error.message);
    }
}

// AI Question Handler
async function handleAIQuestion(e) {
    e.preventDefault();
    
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login first');
        return;
    }
    
    const question = document.getElementById('aiQuestion').value;
    const messagesDiv = document.getElementById('aiMessages');
    
    // Display user message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.textContent = question;
    messagesDiv.appendChild(userMsg);
    
    document.getElementById('aiQuestion').value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${currentRecipeId}/ask/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const aiMsg = document.createElement('div');
            aiMsg.className = 'message ai';
            aiMsg.textContent = data.answer;
            messagesDiv.appendChild(aiMsg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        } else {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'message ai';
            errorMsg.textContent = 'Error: ' + (data.detail || 'Failed to get AI response');
            messagesDiv.appendChild(errorMsg);
        }
    } catch (error) {
        console.error('Error in AI question:', error);
        const errorMsg = document.createElement('div');
        errorMsg.className = 'message ai';
        errorMsg.textContent = 'Error: ' + error.message;
        messagesDiv.appendChild(errorMsg);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('App initialized');
    updateAuthUI();
    showHome();
});
