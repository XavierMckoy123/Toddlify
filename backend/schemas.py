from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Signup/Registration Schema
class UserSignup(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Response Schema
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Token Refresh Schema
class TokenRefresh(BaseModel):
    refresh_token: str

# User Response Schema (returned after successful operations)
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allow reading from ORM models


# Post Schemas for file uploads
class PostCreate(BaseModel):
    """Schema for creating a post with file upload"""
    caption: Optional[str] = Field(None, max_length=500)


class PostResponse(BaseModel):
    """Schema for post response"""
    id: str
    user_id: str
    blob_name: str
    blob_url: str
    content_type: str
    file_size: int
    caption: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Schema for listing posts"""
    id: str
    user_id: str
    blob_url: str
    content_type: str
    file_size: int
    caption: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    post_id: str
    blob_url: str
    content_type: str
    file_size: int
    message: str = "File uploaded successfully"


class PostWithUserResponse(PostResponse):
    """Schema for post with user information"""
    user: UserResponse


class UserWithPostsResponse(UserResponse):
    """Schema for user with their posts"""
    posts: List[PostListResponse] = []
