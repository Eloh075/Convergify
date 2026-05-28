#!/usr/bin/env python3
"""
Database management script for Career Analysis Platform
"""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from database import init_db, check_db_exists, get_db_info
from config import settings

def create_database():
    """Create database and tables"""
    print("🔧 Creating database and tables...")
    try:
        init_db()
        print("✅ Database created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def check_database():
    """Check database status"""
    print("🔍 Checking database status...")
    info = get_db_info()
    
    print(f"Database URL: {info['url']}")
    print(f"Database exists: {'✅' if info['exists'] else '❌'}")
    print(f"Engine: {info['engine']}")
    
    return info['exists']

def reset_database():
    """Reset database (delete and recreate)"""
    print("⚠️  Resetting database (all data will be lost)...")
    
    # For SQLite, just delete the file
    if "sqlite" in settings.database_url:
        db_path = settings.database_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"🗑️  Deleted database file: {db_path}")
    
    # Recreate database
    return create_database()

def seed_database():
    """Seed database with sample data"""
    print("🌱 Seeding database with sample data...")
    
    from sqlalchemy.orm import sessionmaker
    from database import engine
    from models import User
    import uuid
    from datetime import datetime
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create a default user
        default_user = User(
            id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        session.add(default_user)
        session.commit()
        
        print(f"✅ Created default user: {default_user.id}")
        print("✅ Database seeded successfully!")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        return False
    finally:
        session.close()

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py <command>")
        print("Commands:")
        print("  create  - Create database and tables")
        print("  check   - Check database status")
        print("  reset   - Reset database (delete and recreate)")
        print("  seed    - Seed database with sample data")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        create_database()
    elif command == "check":
        check_database()
    elif command == "reset":
        reset_database()
    elif command == "seed":
        if not check_database():
            print("Database doesn't exist. Creating it first...")
            create_database()
        seed_database()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()