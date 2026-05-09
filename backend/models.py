from sqlalchemy import Column, String, DateTime, func, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"

    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    



class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)  # 'image' or 'video'
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, author_id={self.author_id}, created_at={self.created_at})>"
