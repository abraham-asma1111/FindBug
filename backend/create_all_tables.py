"""
Create all database tables using SQLAlchemy models
"""
from src.core.database import engine, Base
from src.domain.models import *  # Import all models

# Create all tables
print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")
