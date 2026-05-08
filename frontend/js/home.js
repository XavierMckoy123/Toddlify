/* ============================================
   HOME PAGE JAVASCRIPT
   ============================================ */

// API Base URL - Update this to your backend URL
const API_BASE_URL = 'http://192.168.100.77:8000';

// DOM Elements
const postBtn = document.getElementById('postBtn');
const searchBtn = document.getElementById('searchBtn');
const profileBtn = document.getElementById('profileBtn');
const postModal = document.getElementById('postModal');
const searchModal = document.getElementById('searchModal');
const closePostModal = document.getElementById('closePostModal');
const closeSearchModal = document.getElementById('closeSearchModal');
const postForm = document.getElementById('postForm');
const searchForm = document.getElementById('searchForm');
const postContent = document.getElementById('postContent');
const charCount = document.getElementById('charCount');
const postsContainer = document.getElementById('postsContainer');
const feedSection = document.getElementById('feedSection');
const searchSection = document.getElementById('searchSection');
const searchResults = document.getElementById('searchResults');
const backBtn = document.getElementById('backBtn');

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    // Load posts when page loads
    loadFeed();
    
    // Set up event listeners
    setupEventListeners();
});

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Navigation buttons
    postBtn.addEventListener('click', openPostModal);
    searchBtn.addEventListener('click', openSearchModal);
    profileBtn.addEventListener('click', () => {
        alert('Profile feature coming soon!');
    });

    // Modal close buttons
    closePostModal.addEventListener('click', closePostModalHandler);
    closeSearchModal.addEventListener('click', closeSearchModalHandler);

    // Forms
    postForm.addEventListener('submit', handlePostSubmit);
    searchForm.addEventListener('submit', handleSearchSubmit);

    // Back button
    backBtn.addEventListener('click', backToFeed);

    // Character counter
    postContent.addEventListener('input', updateCharCount);

    // Close modal when clicking outside
    postModal.addEventListener('click', (e) => {
        if (e.target === postModal) closePostModalHandler();
    });

    searchModal.addEventListener('click', (e) => {
        if (e.target === searchModal) closeSearchModalHandler();
    });
}

// ============================================
// MODAL HANDLERS
// ============================================

function openPostModal() {
    postModal.classList.remove('hidden');
    postModal.classList.add('active');
    postContent.focus();
}

function closePostModalHandler() {
    postModal.classList.add('hidden');
    postModal.classList.remove('active');
    postForm.reset();
    charCount.textContent = '0/500';
}

function openSearchModal() {
    searchModal.classList.remove('hidden');
    searchModal.classList.add('active');
    document.getElementById('searchQuery').focus();
}

function closeSearchModalHandler() {
    searchModal.classList.add('hidden');
    searchModal.classList.remove('active');
    searchForm.reset();
}

function backToFeed() {
    feedSection.classList.add('active');
    searchSection.classList.remove('active');
    document.getElementById('searchQuery').value = '';
    searchResults.innerHTML = '';
}

// ============================================
// CHARACTER COUNTER
// ============================================

function updateCharCount() {
    const length = postContent.value.length;
    charCount.textContent = `${length}/500`;
}

// ============================================
// FORM HANDLERS
// ============================================

async function handlePostSubmit(e) {
    e.preventDefault();
    
    const content = postContent.value.trim();
    
    if (!content) {
        alert('Please write something before posting!');
        return;
    }

    // Show loading state
    const submitBtn = postForm.querySelector('.submit-btn');
    submitBtn.textContent = 'Posting...';
    submitBtn.disabled = true;

    try {
        // Call API to create post (endpoint should be created in backend)
        const response = await fetch(`${API_BASE_URL}/posts/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Add authorization token if available
                // 'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                content: content
            })
        });

        if (response.ok) {
            // Success message
            alert('Post created successfully!');
            closePostModalHandler();
            // Reload feed
            loadFeed();
        } else {
            throw new Error('Failed to create post');
        }
    } catch (error) {
        console.error('Error creating post:', error);
        alert('Failed to create post. Please try again.');
    } finally {
        submitBtn.textContent = 'Post';
        submitBtn.disabled = false;
    }
}

async function handleSearchSubmit(e) {
    e.preventDefault();
    
    const query = document.getElementById('searchQuery').value.trim();
    
    if (!query) {
        alert('Please enter a search query!');
        return;
    }

    // Hide feed and show search section
    feedSection.classList.remove('active');
    searchSection.classList.add('active');
    
    // Show loading state
    searchResults.innerHTML = '<div class="loading">Searching...</div>';
    
    try {
        // Close modal
        closeSearchModalHandler();
        
        // Fetch search results
        const response = await fetch(`${API_BASE_URL}/users/search?q=${encodeURIComponent(query)}`);
        
        if (response.ok) {
            const data = await response.json();
            displaySearchResults(data);
        } else {
            throw new Error('Search failed');
        }
    } catch (error) {
        console.error('Error searching:', error);
        searchResults.innerHTML = '<div class="error">Failed to search. Please try again.</div>';
    }
}

// ============================================
// API CALLS
// ============================================

async function loadFeed() {
    try {
        postsContainer.innerHTML = '<div class="loading">Loading posts...</div>';
        
        // Fetch posts from API
        const response = await fetch(`${API_BASE_URL}/posts/feed`);
        
        if (response.ok) {
            const posts = await response.json();
            displayPosts(posts);
        } else {
            throw new Error('Failed to load posts');
        }
    } catch (error) {
        console.error('Error loading feed:', error);
        postsContainer.innerHTML = '<div class="error">Failed to load posts. Please try again.</div>';
    }
}

// ============================================
// DISPLAY FUNCTIONS
// ============================================

function displayPosts(posts) {
    if (!posts || posts.length === 0) {
        postsContainer.innerHTML = '<div class="loading">No posts yet. Be the first to post!</div>';
        return;
    }

    postsContainer.innerHTML = '';
    
    posts.forEach(post => {
        const postCard = createPostCard(post);
        postsContainer.appendChild(postCard);
    });
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    // Get first letter of author name for avatar
    const avatarLetter = post.author_name ? post.author_name.charAt(0).toUpperCase() : 'U';
    
    // Format timestamp
    const timestamp = formatTime(post.created_at);
    
    card.innerHTML = `
        <div class="post-header">
            <div class="post-avatar">${avatarLetter}</div>
            <div class="post-meta">
                <div class="post-author">${post.author_name || 'Unknown User'}</div>
                <div class="post-username">@${post.author_username || 'user'}</div>
                <div class="post-timestamp">${timestamp}</div>
            </div>
        </div>
        <div class="post-content">${escapeHtml(post.content)}</div>
        <div class="post-footer">
            <button class="post-action" title="Like">
                ❤️ <span>${post.likes_count || 0}</span>
            </button>
            <button class="post-action" title="Comment">
                💬 <span>${post.comments_count || 0}</span>
            </button>
            <button class="post-action" title="Share">
                🔄 <span>${post.shares_count || 0}</span>
            </button>
        </div>
    `;
    
    return card;
}

function displaySearchResults(users) {
    if (!users || users.length === 0) {
        searchResults.innerHTML = '<div class="loading">No users found.</div>';
        return;
    }

    searchResults.innerHTML = '';
    
    users.forEach(user => {
        const userCard = createUserCard(user);
        searchResults.appendChild(userCard);
    });
}

function createUserCard(user) {
    const card = document.createElement('div');
    card.className = 'user-card';
    
    // Get first letter of name for avatar
    const avatarLetter = user.name ? user.name.charAt(0).toUpperCase() : 'U';
    
    card.innerHTML = `
        <div class="user-avatar">${avatarLetter}</div>
        <div class="user-name">${user.name || 'Unknown'}</div>
        <div class="user-username">@${user.username || 'user'}</div>
        <button class="view-profile-btn" onclick="viewProfile('${user.id}')">
            View Profile
        </button>
    `;
    
    return card;
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Format a timestamp to a relative time string (e.g., "2 hours ago")
 */
function formatTime(timestamp) {
    if (!timestamp) return 'just now';
    
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    
    return date.toLocaleDateString();
}

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, (char) => map[char]);
}

/**
 * View user profile (placeholder function)
 */
function viewProfile(userId) {
    alert(`Viewing profile for user ID: ${userId}`);
    // In a real app, you would navigate to the user's profile page
    // window.location.href = `/profile.html?id=${userId}`;
}

/**
 * Get stored authentication token (if available)
 */
function getToken() {
    return localStorage.getItem('auth_token');
}

console.log('Home page loaded successfully!');
