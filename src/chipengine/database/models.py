"""
SQLAlchemy models for ChipEngine database.
"""
from datetime import datetime
from typing import Optional
import uuid
import secrets

from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, 
    ForeignKey, Text, JSON, UniqueConstraint, Index,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from . import Base


def generate_uuid():
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


class GameStatus(enum.Enum):
    """Enum for game status."""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentStatus(enum.Enum):
    """Enum for tournament status."""
    SCHEDULED = "scheduled"
    REGISTRATION_OPEN = "registration_open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentFormat(enum.Enum):
    """Enum for tournament formats."""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"


class Bot(Base):
    """Bot model representing an AI player."""
    __tablename__ = "bots"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True, index=True)
    api_key = Column(String(255), nullable=False, unique=True, default=generate_api_key)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Additional fields for bot management
    description = Column(Text, nullable=True)
    owner_email = Column(String(255), nullable=True, index=True)
    last_active = Column(DateTime, nullable=True)
    
    # Relationships
    players = relationship("Player", back_populates="bot", cascade="all, delete-orphan")
    tournament_participations = relationship("TournamentParticipant", back_populates="bot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bot(id={self.id}, name={self.name}, is_active={self.is_active})>"


class Game(Base):
    """Game model representing a single game instance."""
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    game_type = Column(String(50), nullable=False, index=True)
    state = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    winner_id = Column(String, ForeignKey("bots.id"), nullable=True)
    
    # Additional game metadata
    status = Column(SQLEnum(GameStatus), nullable=False, default=GameStatus.WAITING, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    round_number = Column(Integer, nullable=True)  # For tournament games
    config = Column(JSON, nullable=True)  # Game-specific configuration
    
    # Relationships
    winner = relationship("Bot", foreign_keys=[winner_id])
    players = relationship("Player", back_populates="game", cascade="all, delete-orphan")
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan", order_by="Move.timestamp")
    tournament = relationship("Tournament", back_populates="games")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_game_type_status", "game_type", "status"),
        Index("idx_game_tournament", "tournament_id", "round_number"),
    )
    
    def __repr__(self):
        return f"<Game(id={self.id}, type={self.game_type}, status={self.status})>"


class Player(Base):
    """Player model representing a bot's participation in a game."""
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    player_number = Column(Integer, nullable=False)
    final_position = Column(Integer, nullable=True)  # 1st, 2nd, etc.
    
    # Additional player stats
    score = Column(Integer, nullable=True)
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)  # If player disconnected
    
    # Relationships
    bot = relationship("Bot", back_populates="players")
    game = relationship("Game", back_populates="players")
    moves = relationship("Move", back_populates="player", cascade="all, delete-orphan")
    
    # Ensure unique bot per game
    __table_args__ = (
        UniqueConstraint("bot_id", "game_id", name="uq_bot_game"),
        Index("idx_player_game_bot", "game_id", "bot_id"),
    )
    
    def __repr__(self):
        return f"<Player(id={self.id}, bot_id={self.bot_id}, game_id={self.game_id}, number={self.player_number})>"


class Move(Base):
    """Move model representing a single action in a game."""
    __tablename__ = "moves"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    move_data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Additional move metadata
    move_number = Column(Integer, nullable=True)  # Sequential move number in game
    time_taken_ms = Column(Integer, nullable=True)  # Time taken to make the move
    
    # Relationships
    game = relationship("Game", back_populates="moves")
    player = relationship("Player", back_populates="moves")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_move_game_timestamp", "game_id", "timestamp"),
        Index("idx_move_player_timestamp", "player_id", "timestamp"),
    )
    
    def __repr__(self):
        return f"<Move(id={self.id}, game_id={self.game_id}, player_id={self.player_id}, timestamp={self.timestamp})>"


class Tournament(Base):
    """Tournament model representing a competition between multiple bots."""
    __tablename__ = "tournaments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    game_type = Column(String(50), nullable=False, index=True)
    format = Column(SQLEnum(TournamentFormat), nullable=False, default=TournamentFormat.SINGLE_ELIMINATION)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(TournamentStatus), nullable=False, default=TournamentStatus.SCHEDULED, index=True)
    
    # Tournament configuration
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    max_participants = Column(Integer, nullable=True)
    config = Column(JSON, nullable=True)  # Tournament-specific settings
    
    # Relationships
    participants = relationship("TournamentParticipant", back_populates="tournament", cascade="all, delete-orphan")
    games = relationship("Game", back_populates="tournament", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tournament(id={self.id}, name={self.name}, status={self.status})>"


class TournamentParticipant(Base):
    """Association model for bots participating in tournaments."""
    __tablename__ = "tournament_participants"
    
    tournament_id = Column(String, ForeignKey("tournaments.id"), primary_key=True)
    bot_id = Column(String, ForeignKey("bots.id"), primary_key=True)
    
    # Participation details
    registered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    seed = Column(Integer, nullable=True)  # Initial seeding
    
    # Results
    final_rank = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    draws = Column(Integer, nullable=False, default=0)
    
    # Additional stats
    games_played = Column(Integer, nullable=False, default=0)
    score = Column(Integer, nullable=False, default=0)  # For point-based tournaments
    eliminated = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="participants")
    bot = relationship("Bot", back_populates="tournament_participations")
    
    # Indexes
    __table_args__ = (
        Index("idx_participant_tournament_rank", "tournament_id", "final_rank"),
    )
    
    def __repr__(self):
        return f"<TournamentParticipant(tournament_id={self.tournament_id}, bot_id={self.bot_id}, rank={self.final_rank})>"