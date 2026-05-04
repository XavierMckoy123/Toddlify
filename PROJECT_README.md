# Toddly - Share Your Toddler's Moments

An Instagram-inspired application for parents to share media of their children.

## Current Status: Authentication Phase (Phase 1) - COMPLETE ✅

### Project Structure

```
Toddly/
├── backend/                    # FastAPI Python backend
│   ├── config.py               # Configuration & environment variables
│   ├── main.py                 # FastAPI app & authentication routes
│   ├── models.py               # SQLAlchemy User model
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── auth.py                 # JWT & password hashing utilities
│   ├── database.py             # SQLAlchemy engine & session setup
│   ├── run.py                  # Entry point to run backend
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variables template
│
├── frontend/                   # HTML/CSS/JavaScript frontend
│   ├── login.html              # Login page
│   ├── signup.html             # Registration page
│   ├── js/
│   │   ├── api.js              # API client with auth handling
│   │   ├── login.js            # Login form logic
│   │   └── signup.js           # Signup form with validation
│   └── styles/
│       └── main.css            # Responsive Instagram-inspired styles
│
└── README.md

```

## Backend Implementation ✅

### Core Features Implemented:
- ✅ PostgreSQL database configuration (SQLAlchemy)
- ✅ User model with email, username, password, profile fields
- ✅ Password hashing with bcrypt
- ✅ JWT token generation (access: 15min, refresh: 7 days)
- ✅ Token validation & verification
- ✅ CORS middleware (restricts to frontend origin only)

### API Endpoints:
- ✅ `POST /api/auth/signup` - Register new user
  - Validates email format & uniqueness
  - Validates username (3-100 chars, alphanumeric + `-_`)
  - Hashes password with bcrypt
  - Returns access & refresh tokens
  
- ✅ `POST /api/auth/login` - Authenticate user
  - Validates credentials
  - Generates JWT tokens
  - Handles invalid credentials gracefully
  
- ✅ `POST /api/auth/refresh` - Refresh access token
  - Validates refresh token
  - Returns new access token

## Frontend Implementation ✅

### Pages & Features:
- ✅ **Login Page** (`login.html`)
  - Email & password inputs
  - Password visibility toggle
  - Remember me checkbox
  - Error message display
  - Loading state during submission
  
- ✅ **Signup Page** (`signup.html`)
  - Real-time form validation
  - Email validation with feedback
  - Username validation (3+ chars, alphanumeric + `-_`)
  - Password strength indicator (weak/fair/good)
  - Password confirmation matching
  - Optional first/last name fields
  - Terms acceptance checkbox
  - Success message with auto-redirect
  
- ✅ **API Client** (`api.js`)
  - Centralized API communication
  - Token storage/retrieval
  - Automatic 401 redirect to login
  - Bearer token authorization header

### Styling:
- ✅ Instagram-inspired gradient logo
- ✅ Responsive mobile-first design
- ✅ Smooth transitions & animations
- ✅ Color-coded feedback (errors, success, validation)
- ✅ Loading spinner animation

## Next Steps: Testing & Remaining Tasks

### Remaining (3 todos):
1. **backend-test** - Test endpoints with Postman/curl
2. **frontend-test** - Test form submission & token persistence
3. **security-audit** - Verify password hashing, token validation, CORS

## Setup Instructions

### Backend Setup
1. Navigate to `backend/` directory
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Copy `.env.example` to `.env` and update PostgreSQL credentials:
   ```
   DATABASE_URL=postgresql://user:password@localhost/toddly
   SECRET_KEY=your-secret-key-here
   ```
5. Create PostgreSQL database: `createdb toddly`
6. Install dependencies: `pip install -r requirements.txt`
7. Run backend: `python run.py`

### Frontend Setup
- Open `frontend/login.html` or `frontend/signup.html` in a browser
- Backend must be running on `http://localhost:8001`
- Use a local HTTP server or open directly (for development)

## Database Schema

### Users Table
- `id` (UUID) - Primary key
- `email` (String, unique) - User email
- `username` (String, unique) - Unique username
- `password_hash` (String) - Bcrypt hashed password
- `first_name` (String, optional)
- `last_name` (String, optional)
- `profile_picture_url` (String, optional)
- `bio` (String, optional)
- `created_at` (DateTime) - Account creation timestamp
- `updated_at` (DateTime) - Last update timestamp

## Security Features
✅ Passwords hashed with bcrypt (salt rounds: 12)
✅ JWT tokens with expiration (access: 15min, refresh: 7 days)
✅ CORS restricted to frontend origin only
✅ Input validation on all endpoints (email, username, password)
✅ SQL injection protection via SQLAlchemy ORM
✅ Unique email/username constraints at database level

## Technology Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT, Bcrypt
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Auth**: JWT (JSON Web Tokens), Bearer scheme
- **Database**: PostgreSQL with SQLAlchemy ORM

## Future Features (Out of Scope)
- Home/feed page with post timeline
- Post creation & media upload
- Comment system
- Like/favorite functionality
- Follow/unfollow users
- User profiles & bio editing
- Email verification
- Password reset flow
- OAuth social login
- Push notifications

