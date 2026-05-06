import os
from dotenv import load_dotenv

load_dotenv()

# Database - Using SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./toddly.db")

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

# Password hashing
BCRYPT_ROUNDS = 12
