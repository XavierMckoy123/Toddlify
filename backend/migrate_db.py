"""
Database migration script to create the Post table
Run this after updating models.py with the new Post model
"""

from sqlalchemy import text
from database import engine, Base
from models import User, Post

def migrate_database():
    """Create all tables defined in models"""
    print("Starting database migration...")
    
    try:
        # Create all tables defined in Base metadata
        Base.metadata.create_all(bind=engine)
        print("✓ Database migration completed successfully!")
        
        # Show created tables
        with engine.connect() as conn:
            inspector_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in inspector_result]
            print(f"\nCreated/Updated tables:")
            for table in tables:
                print(f"  - {table}")
        
        return True
    
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    exit(0 if success else 1)
