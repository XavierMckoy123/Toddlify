from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from config import FRONTEND_URL
from database import get_db, init_db
from models import User, Post
from fastapi import Form
from schemas import (
    UserSignup, UserLogin, Token, TokenRefresh, UserResponse,
    PostCreate, PostResponse, PostListResponse, FileUploadResponse
)
from auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, get_user_id_from_token
from blob_storage import get_blob_manager

# Initialize database
init_db()

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


# ==================== FILE UPLOAD ENDPOINTS ====================

@app.post("/api/posts/upload", response_model=FileUploadResponse, status_code=201)
async def upload_post(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),  # ✅ FIXED
    current_user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """Upload a file and create a post"""
    try:
        blob_manager = get_blob_manager()
        file_content = await file.read()
        
        # Upload to blob storage
        upload_result = blob_manager.upload_file(
            file_content=file_content,
            filename=file.filename,
            user_id=current_user_id,
            content_type=file.content_type
        )
        
        # Create post record in database
        new_post = Post(
            user_id=current_user_id,
            blob_name=upload_result["blob_name"],
            blob_url=upload_result["blob_url"],
            content_type=upload_result["content_type"],
            file_size=upload_result["file_size"],
            caption=caption
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return FileUploadResponse(
            post_id=str(new_post.id),
            blob_url=new_post.blob_url,
            content_type=new_post.content_type,
            file_size=new_post.file_size
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@app.get("/api/posts", response_model=List[PostListResponse])
async def get_all_posts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Get all posts from all users (paginated)"""
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific post by ID"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@app.get("/api/users/{user_id}/posts", response_model=List[PostListResponse])
async def get_user_posts(
    user_id: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Get all posts from a specific user (paginated)"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@app.delete("/api/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    current_user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """Delete a post (only owner can delete)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user is owner
    if str(post.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )
    
    # Delete from blob storage
    try:
        blob_manager = get_blob_manager()
        blob_manager.delete_file(post.blob_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
    
    # Delete from database
    db.delete(post)
    db.commit()


@app.patch("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_caption(
    post_id: str,
    post_data: PostCreate,
    current_user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """Update post caption (only owner can update)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user is owner
    if str(post.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )
    
    post.caption = post_data.caption
    db.commit()
    db.refresh(post)
    
    return post

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
