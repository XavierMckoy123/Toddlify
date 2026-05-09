from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from config import FRONTEND_URL
from database import get_db, init_db
from uuid import UUID
import os
from typing import List
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from models import User, Post
from schemas import (
    UserSignup, UserLogin, Token, TokenRefresh,
    UserResponse, PostCreate, PostResponse
)
from auth import hash_password, verify_password

# Initialize database
init_db()

app = FastAPI(
    title="Toddly API",
    description="Instagram-inspired app for sharing toddler moments",
    version="1.0.0"
)

# ✅ CREATE FOLDER FIRST
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HEALTH
# ============================================

@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ============================================
# AUTH
# ============================================

@app.post("/api/auth/signup", response_model=UserResponse, status_code=201)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(
            (User.email == user_data.email) |
            (User.username == user_data.username)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email or username already registered"
            )

        hashed_password = hash_password(user_data.password)

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

        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or username already registered"
        )




@app.post("/api/auth/refresh", response_model=UserResponse)
async def refresh_access_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    payload = verify_token(token_data.refresh_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user_id = UUID(user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = create_access_token({"sub": str(user_id)})

    return {
        "access_token": new_access_token,
        "refresh_token": token_data.refresh_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": str(user.id),
        "username": user.username
    }


# ============================================
# USERS
# ============================================

@app.get("/api/users/search", response_model=List[UserResponse])
async def search_users(q: str, db: Session = Depends(get_db)):
    if not q:
        return []

    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.first_name.ilike(f"%{q}%")) |
        (User.last_name.ilike(f"%{q}%"))
    ).limit(20).all()

    return users

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user_id = UUID(user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user





@app.get("/api/users/{user_id}/posts")
async def get_user_posts(user_id: str, db: Session = Depends(get_db)):
    user_id = UUID(user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts = db.query(Post).filter(
        Post.author_id == user_id
    ).order_by(Post.created_at.desc()).all()

    enriched = []
    for post in posts:
        enriched.append({
            "id": str(post.id),
            "content": post.content,
            "media_url": post.media_url,
            "media_type": post.media_type,
            "author_id": str(post.author_id),
            "author_name": f"{post.author.first_name or ''} {post.author.last_name or ''}".strip(),
            "author_username": post.author.username,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        })

    return enriched


# ============================================
# POSTS
# ============================================

@app.post("/api/posts/create")
async def create_post(
    content: str = Form(None),
    user_id: str = Form(...),
    media: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == UUID(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if (not content or not content.strip()) and not media:
        raise HTTPException(status_code=400, detail="Post must have content or media")

    media_url = None
    media_type = None

    if media:
        file_ext = media.filename.split('.')[-1]
        file_name = f"{uuid4()}.{file_ext}"
        file_path = os.path.join("uploads", file_name)

        contents = await media.read()   # ✅ read once
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        media_url = f"/uploads/{file_name}"

        if media.content_type.startswith("image"):
            media_type = "image"
        elif media.content_type.startswith("video"):
            media_type = "video"

    new_post = Post(
        content=content or "",
        media_url=media_url,
        media_type=media_type,
        author_id=user.id
    )

    db.add(new_post)
    db.commit()

    return {"success": True}   # ✅ cleaner response

@app.get("/api/posts/feed")
async def get_feed(
    db: Session = Depends(get_db),
):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()

    enriched = []
    for post in posts:
        enriched.append({
            "id": str(post.id),
            "content": post.content,
            "media_url": post.media_url,
            "media_type": post.media_type,
            "author_id": str(post.author_id),
            "author_name": f"{post.author.first_name or ''} {post.author.last_name or ''}".strip(),
            "author_username": post.author.username,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        })

    return enriched


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)