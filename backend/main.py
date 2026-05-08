from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from config import FRONTEND_URL
from database import get_db, init_db
from uuid import UUID
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

@app.post("/api/auth/signup", response_model=Token, status_code=201)
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
            status_code=409,
            detail="Email or username already registered"
        )


@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/api/auth/refresh", response_model=Token)
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


# ============================================
# USERS
# ============================================

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user_id = UUID(user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/api/users/search")
async def search_users(q: str, db: Session = Depends(get_db)):
    if not q:
        return []

    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.first_name.ilike(f"%{q}%")) |
        (User.last_name.ilike(f"%{q}%"))
    ).limit(20).all()

    return users


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

@app.post("/api/posts/create", status_code=201)
async def create_post(
    content: str = Form(None),
    media: UploadFile = File(None),
    db: Session = Depends(get_db),
):
        # TEMP: fake logged-in user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users exist")

    user_id = user.id

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if (not content or not content.strip()) and not media:
        raise HTTPException(status_code=400, detail="Post must have content or media")

    media_url = None
    media_type = None

    try:
        new_post = Post(
            content=content.strip() if content else None,
            media_url=media_url,
            media_type=media_type,
            author_id=user_id
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return {
            "id": str(new_post.id),
            "message": "Post created successfully",
            "created_at": new_post.created_at
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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