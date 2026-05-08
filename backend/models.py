from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to posts
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    blob_name = Column(String(500), nullable=False)  # Path in Azure Blob Storage
    blob_url = Column(String(500), nullable=False)   # Public URL of the blob
    content_type = Column(String(100), nullable=False)  # MIME type
    file_size = Column(Integer, nullable=False)  # File size in bytes
    caption = Column(Text, nullable=True)  # Optional caption/description
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, blob_name={self.blob_name})>"
