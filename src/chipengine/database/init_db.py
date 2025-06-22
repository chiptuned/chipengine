"""
Database initialization script for ChipEngine.

Run this script to create all database tables.
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path to import chipengine
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from chipengine.database import init_db, engine
from chipengine.database.models import (
    Bot, Game, Player, Move, Tournament, TournamentParticipant
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    try:
        logger.info(f"Initializing database with engine: {engine.url}")
        init_db()
        logger.info("Database initialized successfully!")
        
        # Print created tables
        logger.info("Created tables:")
        for table in [Bot, Game, Player, Move, Tournament, TournamentParticipant]:
            logger.info(f"  - {table.__tablename__}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()