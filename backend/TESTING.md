# Toddly Backend Testing Guide

This guide explains how to test the Toddly authentication backend.

## Prerequisites

1. **PostgreSQL installed and running**
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Or use a cloud PostgreSQL service

2. **Python 3.8+**
   - Verify with: `python --version`

3. **Dependencies installed**
   - From `backend/` directory: `pip install -r requirements.txt`

## Setup Steps

### 1. Create PostgreSQL Database

```bash
# Using psql (PostgreSQL command line)
createdb toddly
```

Or using a GUI tool like pgAdmin.

### 2. Create .env file

In `backend/` directory, create `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost/toddly
SECRET_KEY=your-secret-key-change-in-production-12345
FRONTEND_URL=http://localhost:8000
HOST=0.0.0.0
PORT=8001
```

Replace `user` and `password` with your PostgreSQL credentials.

### 3. Run Unit Tests

```bash
cd backend
python test_backend.py
```

This tests:
- ✓ Module imports
- ✓ Password hashing
- ✓ Token generation & verification
- ✓ Schema validation

## Testing API Endpoints

### Option 1: Using curl (Command Line)

**Start the backend:**
```bash
cd backend
python run.py
```

Server will run on `http://localhost:8001`

**Test Signup (Create Account):**
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "username": "jane_doe",
    "password": "SecurePass123",
    "first_name": "Jane",
    "last_name": "Doe"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Test Login:**
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "password": "SecurePass123"
  }'
```

**Test Refresh Token:**
```bash
curl -X POST http://localhost:8001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGc..."
  }'
```

Replace `eyJhbGc...` with actual token from signup/login response.

### Option 2: Using Postman (GUI)

1. Download & install Postman: https://www.postman.com/downloads/
2. Create a new collection "Toddly Auth"
3. Create requests:

**Signup Request:**
- Method: POST
- URL: `http://localhost:8001/api/auth/signup`
- Body (JSON):
```json
{
  "email": "john@example.com",
  "username": "john_smith",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Smith"
}
```

**Login Request:**
- Method: POST
- URL: `http://localhost:8001/api/auth/login`
- Body (JSON):
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Refresh Token Request:**
- Method: POST
- URL: `http://localhost:8001/api/auth/refresh`
- Body (JSON):
```json
{
  "refresh_token": "paste_refresh_token_here"
}
```

## Test Cases

### ✓ Successful Signup
```json
Request:
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "TestPassword123"
}

Response (201 Created):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### ✓ Successful Login
```json
Request:
{
  "email": "test@example.com",
  "password": "TestPassword123"
}

Response (200 OK):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### ✓ Invalid Email on Signup
```json
Request:
{
  "email": "not-an-email",
  "username": "testuser",
  "password": "TestPassword123"
}

Response (422 Unprocessable Entity):
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "invalid email format"
    }
  ]
}
```

### ✓ Weak Password on Signup
```json
Request:
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "weak"
}

Response (422 Unprocessable Entity):
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters"
    }
  ]
}
```

### ✓ Duplicate Email
```json
Request (after creating account with same email):
{
  "email": "duplicate@example.com",
  "username": "newuser",
  "password": "TestPassword123"
}

Response (409 Conflict):
{
  "detail": "Email or username already registered"
}
```

### ✓ Invalid Login Credentials
```json
Request:
{
  "email": "test@example.com",
  "password": "WrongPassword123"
}

Response (401 Unauthorized):
{
  "detail": "Invalid email or password"
}
```

### ✓ Token Refresh
```json
Request:
{
  "refresh_token": "eyJ..."
}

Response (200 OK):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### ✗ Invalid Refresh Token
```json
Request:
{
  "refresh_token": "invalid.token.here"
}

Response (401 Unauthorized):
{
  "detail": "Invalid or expired refresh token"
}
```

## Verifying Security

### 1. Check Password Hashing
```bash
# Connect to database
psql -U user -d toddly

# View users table
SELECT id, email, username, password_hash FROM users;
```

✓ Password hashes should NOT match the original password
✓ All passwords should start with `$2b$` (bcrypt indicator)

### 2. Test CORS
```bash
# Request from different origin
curl -X OPTIONS http://localhost:8001/api/auth/signup \
  -H "Origin: http://example.com" \
  -H "Access-Control-Request-Method: POST"
```

✓ Should be rejected (not allowed origin)

```bash
# Request from allowed origin
curl -X OPTIONS http://localhost:8001/api/auth/signup \
  -H "Origin: http://localhost:8000" \
  -H "Access-Control-Request-Method: POST"
```

✓ Should be accepted (allowed origin)

### 3. Test Token Expiration
```bash
# Get access token
# Wait 15+ minutes (ACCESS_TOKEN_EXPIRE_MINUTES = 15)
# Try to use expired token

curl -X GET http://localhost:8001/api/protected \
  -H "Authorization: Bearer eyJ..." # expired token
```

✓ Should return 401 Unauthorized

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "psycopg2: could not connect to server"
- PostgreSQL not running
- Wrong credentials in .env
- Database doesn't exist (run `createdb toddly`)

### "Address already in use" (port 8001)
- Another process using port 8001
- Change PORT in .env or kill the process

### CORS errors in browser
- Make sure FRONTEND_URL in .env matches your frontend origin
- Default: `http://localhost:8000`

## Next Steps

1. ✓ Backend unit tests pass
2. Test endpoints with curl/Postman
3. Test frontend login/signup pages
4. Run security audit
5. Deploy to production

See PROJECT_README.md for full documentation.
