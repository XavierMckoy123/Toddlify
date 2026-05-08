/* ============================================
   HOME PAGE JAVASCRIPT
   ============================================ */

// API Base URL - Update this to your backend URL
const API_BASE_URL = 'http://192.168.100.77:8001/api';

// DOM Elements - Navigation
const postBtn = document.getElementById('postBtn');
const searchBtn = document.getElementById('searchBtn');
const profileBtn = document.getElementById('profileBtn');

// DOM Elements - Sections
const feedSection = document.getElementById('feedSection');
const searchSection = document.getElementById('searchSection');
const profileSection = document.getElementById('profileSection');
const postsContainer = document.getElementById('postsContainer');
const searchResults = document.getElementById('searchResults');

// DOM Elements - Modals
const postModal = document.getElementById('postModal');
const searchModal = document.getElementById('searchModal');
const closePostModal = document.getElementById('closePostModal');
const closeSearchModal = document.getElementById('closeSearchModal');

// DOM Elements - Post Form
const postForm = document.getElementById('postForm');
const postContent = document.getElementById('postContent');
const charCount = document.getElementById('charCount');
const mediaInput = document.getElementById('mediaInput');
const mediaPreview = document.getElementById('mediaPreview');
const removeMediaBtn = document.getElementById('removeMediaBtn');

// DOM Elements - Search
const searchForm = document.getElementById('searchForm');
const backBtn = document.getElementById('backBtn');

// DOM Elements - Profile
const profileBackBtn = document.getElementById('profileBackBtn');
const profileName = document.getElementById('profileName');
const profileUsername = document.getElementById('profileUsername');
const profileBio = document.getElementById('profileBio');
const profilePostsGrid = document.getElementById('profilePostsGrid');
const profilePicture = document.getElementById('profilePicture');

// Global state
let selectedMediaFile = null;
let currentUserId = null;

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
    profileBtn.addEventListener('click', loadCurrentUserProfile);

    // Modal close buttons
    closePostModal.addEventListener('click', closePostModalHandler);
    closeSearchModal.addEventListener('click', closeSearchModalHandler);

    // Forms
    postForm.addEventListener('submit', handlePostSubmit);
    searchForm.addEventListener('submit', handleSearchSubmit);

    // Back buttons
    backBtn.addEventListener('click', backToFeed);
    profileBackBtn.addEventListener('click', backToFeed);

    // Character counter
    postContent.addEventListener('input', updateCharCount);

    // Media upload
    mediaInput.addEventListener('change', handleMediaSelect);
    removeMediaBtn.addEventListener('click', removeMedia);

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
    removeMedia();
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
    profileSection.classList.remove('active');
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
// MEDIA UPLOAD HANDLERS
// ============================================

function handleMediaSelect(e) {
    const file = e.target.files[0];
    
    if (!file) return;

    // Validate file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
        alert('File size must be less than 50MB');
        mediaInput.value = '';
        return;
    }

    selectedMediaFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (event) => {
        mediaPreview.innerHTML = '';
        
        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = event.target.result;
            mediaPreview.appendChild(img);
        } else if (file.type.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = event.target.result;
            video.controls = true;
            mediaPreview.appendChild(video);
        }
    };
    reader.readAsDataURL(file);
    
    removeMediaBtn.style.display = 'block';
}

function removeMedia() {
    selectedMediaFile = null;
    mediaInput.value = '';
    mediaPreview.innerHTML = '';
    removeMediaBtn.style.display = 'none';
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
        // Create FormData for multipart request (to handle file uploads)
        const formData = new FormData();
        formData.append('content', content);
        
        if (selectedMediaFile) {
            formData.append('media', selectedMediaFile);
        }

        // Call API to create post
        const response = await fetch(`${API_BASE_URL}/posts/create`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${api.getAccessToken()}`
            },
            body: formData
        });

        if (response.ok) {
            alert('Post created successfully!');
            closePostModalHandler();
            loadFeed();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create post');
        }
    } catch (error) {
        console.error('Error creating post:', error);
        alert(error.message || 'Failed to create post. Please try again.');
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
    profileSection.classList.remove('active');
    
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
        feedSection.classList.add('active');
        searchSection.classList.remove('active');
        profileSection.classList.remove('active');
        
        postsContainer.innerHTML = '<div class="loading">Loading posts...</div>';
        
        // Fetch posts from API
        const response = await fetch(`${API_BASE_URL}/posts/feed`, {
            headers: {
                'Authorization': `Bearer ${api.getAccessToken()}`
            }
        });
        
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

async function loadCurrentUserProfile() {
    try {
        // Get user ID from token or localStorage
        const userId = localStorage.getItem('user_id');
        
        if (!userId) {
            alert('Please log in first');
            window.location.href = 'login.html';
            return;
        }
        
        loadUserProfile(userId);
    } catch (error) {
        console.error('Error loading current user profile:', error);
        alert('Failed to load profile');
    }
}

async function loadUserProfile(userId) {
    try {
        currentUserId = userId;
        
        feedSection.classList.remove('active');
        searchSection.classList.remove('active');
        profileSection.classList.add('active');
        
        profilePostsGrid.innerHTML = '<div class="loading">Loading profile...</div>';
        
        // Fetch user data
        const userResponse = await fetch(`${API_BASE_URL}/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${api.getAccessToken()}`
            }
        });
        
        if (!userResponse.ok) {
            throw new Error('Failed to load user');
        }
        
        const user = await userResponse.json();
        displayUserProfile(user);
        
        // Fetch user posts
        const postsResponse = await fetch(`${API_BASE_URL}/users/${userId}/posts`, {
            headers: {
                'Authorization': `Bearer ${api.getAccessToken()}`
            }
        });
        
        if (postsResponse.ok) {
            const posts = await postsResponse.json();
            displayProfilePosts(posts);
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
        profilePostsGrid.innerHTML = '<div class="error">Failed to load profile. Please try again.</div>';
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

function displayUserProfile(user) {
    const avatarLetter = user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U';
    
    profilePicture.textContent = avatarLetter;
    profileName.textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'User';
    profileUsername.textContent = `@${user.username}`;
    profileBio.textContent = user.bio || 'No bio added yet';
}

function displayProfilePosts(posts) {
    if (!posts || posts.length === 0) {
        profilePostsGrid.innerHTML = '<div class="loading">No posts yet</div>';
        return;
    }

    profilePostsGrid.innerHTML = '';
    
    posts.forEach(post => {
        const postItem = createProfilePostItem(post);
        profilePostsGrid.appendChild(postItem);
    });
}

function createProfilePostItem(post) {
    const item = document.createElement('div');
    item.className = 'profile-post-item';
    
    if (post.media_url) {
        let mediaHtml;
        if (post.media_type === 'image') {
            mediaHtml = `<img src="${post.media_url}" alt="Post" class="profile-post-image">`;
        } else if (post.media_type === 'video') {
            mediaHtml = `<video src="${post.media_url}" class="profile-post-image"></video>`;
        } else {
            mediaHtml = `<div class="profile-post-image" style="background-color: #f3f4f6; display: flex; align-items: center; justify-content: center;">📄</div>`;
        }
        item.innerHTML = mediaHtml;
    } else {
        item.innerHTML = `<div class="profile-post-image" style="background-color: #f3f4f6; display: flex; align-items: center; justify-content: center; padding: 1rem;">${escapeHtml(post.content.substring(0, 100))}</div>`;
    }
    
    return item;
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    // Get first letter of author name for avatar
    const avatarLetter = post.author_name ? post.author_name.charAt(0).toUpperCase() : 'U';
    
    // Format timestamp
    const timestamp = formatTime(post.created_at);
    
    // Build media HTML if exists
    let mediaHtml = '';
    if (post.media_url) {
        if (post.media_type === 'image') {
            mediaHtml = `<div class="post-media"><img src="${post.media_url}" alt="Post media"></div>`;
        } else if (post.media_type === 'video') {
            mediaHtml = `<div class="post-media"><video src="${post.media_url}" controls></video></div>`;
        }
    }
    
    card.innerHTML = `
        <div class="post-header">
            <div class="post-avatar">${avatarLetter}</div>
            <div class="post-meta">
                <div class="post-author" style="cursor: pointer;" onclick="loadUserProfile('${post.author_id}')">
                    ${post.author_name || 'Unknown User'}
                </div>
                <div class="post-username">@${post.author_username || 'user'}</div>
                <div class="post-timestamp">${timestamp}</div>
            </div>
        </div>
        ${mediaHtml}
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
    const avatarLetter = user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U';
    
    card.innerHTML = `
        <div class="user-avatar">${avatarLetter}</div>
        <div class="user-name">${(user.first_name || 'User')} ${user.last_name || ''}`.trim() + `</div>
        <div class="user-username">@${user.username || 'user'}</div>
        <button class="view-profile-btn" onclick="loadUserProfile('${user.id}')">
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

console.log('Home page loaded successfully!');
