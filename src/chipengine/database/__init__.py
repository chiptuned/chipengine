"""
Database initialization and engine setup for ChipEngine.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# Base class for all models
Base = declarative_base()

# Database URL configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./chipengine.db"  # Default to SQLite for development
)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )
else:
    # PostgreSQL and other databases
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )

def init_db():
    """Initialize the database by creating all tables."""
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)