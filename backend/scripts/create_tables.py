# backend/scripts/create_tables.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import *

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

def drop_tables():
    """Drop all tables (use with caution)"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            drop_tables()
            create_tables()
    else:
        create_tables()