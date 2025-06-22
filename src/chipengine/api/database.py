"""Database setup and models for ChipEngine."""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import secrets
import hashlib

Base = declarative_base()
engine = create_engine("sqlite:///chipengine.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Bot(Base):
    """Bot registration model."""
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    api_key = Column(String(64), unique=True, index=True, nullable=False)
    api_key_hash = Column(String(64), nullable=False)  # SHA256 hash for security
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    games = relationship("Game", back_populates="bot")
    moves = relationship("Move", back_populates="bot")
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()


class Game(Base):
    """Game instance model."""
    __tablename__ = "games"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    game_type = Column(String(50), nullable=False)
    status = Column(String(20), default="active")  # active, completed, abandoned
    players = Column(Text, nullable=False)  # JSON array of player names
    winner = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Bot that created the game
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    bot = relationship("Bot", back_populates="games")
    
    # Game state and moves
    current_state = Column(Text, nullable=True)  # JSON game state
    moves = relationship("Move", back_populates="game")


class Move(Base):
    """Game move model."""
    __tablename__ = "moves"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String(36), ForeignKey("games.id"), nullable=False)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    player = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    data = Column(Text, nullable=True)  # JSON additional data
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="moves")
    bot = relationship("Bot", back_populates="moves")


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()