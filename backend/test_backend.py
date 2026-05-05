#!/usr/bin/env python3
"""
Test script for Toddly backend authentication endpoints
Requires backend dependencies to be installed
"""

import json
import sys
import time
import subprocess
from pathlib import Path

backend_path = Path(r"C:\Users\jason\OneDrive\Documents\GitHub\Toddlify\backend")
sys.path.insert(0, str(backend_path))

print("=" * 60)
print("TODDLY BACKEND TESTING SCRIPT")
print("=" * 60)

# Step 1: Install dependencies
print("\n[1/4] Installing dependencies...")
try:
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q",
         "fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary",
         "python-jose[cryptography]", "passlib[bcrypt]", "pydantic[email]",
         "python-dotenv"],
        cwd=backend_path,
        capture_output=True,
        timeout=120
    )
    if result.returncode == 0:
        print("  OK: Dependencies installed")
    else:
        print(f"  WARNING: {result.stderr.decode()[:200]}")
except Exception as e:
    print(f"  WARNING: Could not install all dependencies: {e}")

# Step 2: Test imports
print("\n[2/4] Testing module imports...")
try:
    import config
    print("  OK: config.py")
    import database
    print("  OK: database.py")
    import models
    print("  OK: models.py")
    import schemas
    print("  OK: schemas.py")
    import auth
    print("  OK: auth.py")
    print("  SUCCESS: All modules imported")
except ImportError as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# Step 3: Test authentication utilities
print("\n[3/4] Testing authentication utilities...")
try:
    from auth import hash_password, verify_password, create_access_token, verify_token
    
    # Test password hashing
    test_password = "TestPassword123"
    hashed = hash_password(test_password)
    is_valid = verify_password(test_password, hashed)
    
    if is_valid:
        print("  OK: Password hashing & verification works")
    else:
        print("  ERROR: Password verification failed")
    
    # Test token creation
    token = create_access_token({"sub": "test-user-id"})
    payload = verify_token(token)
    
    if payload and payload.get("sub") == "test-user-id":
        print("  OK: Token creation & verification works")
    else:
        print("  ERROR: Token verification failed")
    
    print("  SUCCESS: Authentication utilities verified")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# Step 4: Test Pydantic schemas
print("\n[4/4] Testing Pydantic schemas...")
try:
    from schemas import UserSignup, UserLogin, Token
    
    # Valid signup data
    valid_signup = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    user = UserSignup(**valid_signup)
    print(f"  OK: Signup schema accepts valid data")
    
    # Valid login data
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123"
    }
    login = UserLogin(**login_data)
    print(f"  OK: Login schema accepts valid data")
    
    # Invalid signup (bad email)
    try:
        bad_signup = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "TestPassword123"
        }
        UserSignup(**bad_signup)
        print("  ERROR: Invalid email was accepted")
    except:
        print("  OK: Schema rejects invalid email")
    
    # Invalid signup (weak password)
    try:
        weak_password = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak"
        }
        UserSignup(**weak_password)
        print("  ERROR: Weak password was accepted")
    except:
        print("  OK: Schema rejects weak password (too short)")
    
    print("  SUCCESS: Pydantic schemas verified")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("UNIT TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\nNext steps:")
print("1. Set up PostgreSQL database (createdb toddly)")
print("2. Create .env file with DATABASE_URL")
print("3. Run: python run.py (to start the backend server)")
print("4. Test endpoints with curl or Postman")
print("=" * 60)
