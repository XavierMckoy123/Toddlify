from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from config import FRONTEND_URL
from database import get_db, init_db
from models import User
from schemas import UserSignup, UserLogin, Token, TokenRefresh, UserResponse
from auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, get_user_id_from_token
from fastapi import File, UploadFile
from typing import Optional
import os
from dotenv import load_dotenv
import uuid
from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions
)
from datetime import datetime, timedelta

# Initialize database
init_db()


load_dotenv()
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)

container_name = "uploads"
account_name = blob_service_client.account_name

account_key = blob_service_client.credential.account_key
print(AZURE_STORAGE_CONNECTION_STRING)
def generate_sas_url(blob_name: str):

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=24)
    )

    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

# Create FastAPI app
app = FastAPI(
    title="Toddly API",
    description="Instagram-inspired app for sharing toddler moments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# Authentication endpoints
@app.post("/api/auth/signup", response_model=Token, status_code=201)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email or username already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate tokens
        access_token = create_access_token({"sub": str(new_user.id)})
        refresh_token = create_refresh_token({"sub": str(new_user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered"
        )

@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Log in a user"""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/refresh", response_model=Token)
async def refresh_access_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh an access token using refresh token"""
    # Verify refresh token
    payload = verify_token(token_data.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Verify user still exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Create new access token
    new_access_token = create_access_token({"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "refresh_token": token_data.refresh_token,  # Keep same refresh token
        "token_type": "bearer"
    }

@app.post("/api/posts/create")
async def create_post(
    content: str,
    media: Optional[UploadFile] = File(None)
):
    """Create a new post"""

    media_url = None

    # Upload media to Azure Blob Storage
    if media:

        file_extension = media.filename.split(".")[-1]

        blob_name = f"{uuid.uuid4()}.{file_extension}"

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )

        file_data = await media.read()

        blob_client.upload_blob(
            file_data,
            overwrite=True,
            content_type=media.content_type
        )

        media_url = generate_sas_url(blob_name)

        media_type = None

        if media.content_type.startswith("image/"):
            media_type = "image"

        elif media.content_type.startswith("video/"):
            media_type = "video"
            

    return {
    "message": "Post created successfully",
    "content": content,
    "media_url": media_url,
    "media_type": media_type
}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
