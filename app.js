// ...existing code...

function updateAuthUI() {
    const token = localStorage.getItem('token');
    const authLink = document.getElementById('authLink');
    const logoutLink = document.getElementById('logoutLink');
    const createBtn = document.querySelector('.create-btn');
    
    if (token) {
        authLink.classList.add('hidden');
        logoutLink.classList.remove('hidden');
        if (createBtn) createBtn.classList.remove('hidden');
    } else {
        authLink.classList.remove('hidden');
        logoutLink.classList.add('hidden');
        if (createBtn) createBtn.classList.add('hidden');
    }
}

function showCreateRecipe() {
    showSection('createRecipe');
    document.getElementById('ingredientsList').innerHTML = '';
    addIngredient();
}

function showRecipeDetail(recipeId) {
    currentRecipeId = recipeId;
    showSection('recipeDetail');
    loadRecipeDetail(recipeId);
}

// ...existing code...

async function loadRecipeDetail(recipeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`);
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
        recipe.ingredients.forEach(ing => {
            const li = document.createElement('li');
            li.textContent = `${ing.name} - ${ing.quantity} ${ing.unit}`;
            ingredientsList.appendChild(li);
        });
        
        // Show like button if logged in
        const likeBtn = document.querySelector('.like-btn');
        if (localStorage.getItem('token')) {
            likeBtn.classList.remove('hidden');
        } else {
            likeBtn.classList.add('hidden');
        }
        
        document.getElementById('aiMessages').innerHTML = '';
    } catch (error) {
        alert('Error loading recipe: ' + error.message);
    }
}

// ...existing code...