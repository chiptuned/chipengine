"""
Example usage of ChipEngine database models.

This script demonstrates basic CRUD operations with the models.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from chipengine.database import init_db
from chipengine.database.session import get_db_context
from chipengine.database.models import (
    Bot, Game, Player, Move, Tournament, TournamentParticipant,
    GameStatus, TournamentStatus, TournamentFormat
)


def create_example_data():
    """Create some example data in the database."""
    with get_db_context() as db:
        # Create some bots
        bot1 = Bot(
            name="AlphaBot",
            description="A simple AI bot using alpha-beta pruning",
            owner_email="alpha@example.com"
        )
        bot2 = Bot(
            name="RandomBot", 
            description="Makes random valid moves",
            owner_email="random@example.com"
        )
        bot3 = Bot(
            name="NeuralBot",
            description="Deep learning based bot",
            owner_email="neural@example.com"
        )
        
        db.add_all([bot1, bot2, bot3])
        db.commit()
        
        print(f"Created bot: {bot1.name} with API key: {bot1.api_key}")
        print(f"Created bot: {bot2.name} with API key: {bot2.api_key}")
        print(f"Created bot: {bot3.name} with API key: {bot3.api_key}")
        
        # Create a game
        game = Game(
            game_type="rock_paper_scissors",
            status=GameStatus.COMPLETED,
            state={"rounds": 3, "current_round": 3},
            completed_at=datetime.utcnow(),
            winner_id=bot1.id
        )
        db.add(game)
        db.commit()
        
        # Add players to the game
        player1 = Player(
            bot_id=bot1.id,
            game_id=game.id,
            player_number=1,
            final_position=1,
            score=2
        )
        player2 = Player(
            bot_id=bot2.id,
            game_id=game.id,
            player_number=2,
            final_position=2,
            score=1
        )
        db.add_all([player1, player2])
        db.commit()
        
        # Add some moves
        moves = [
            Move(
                game_id=game.id,
                player_id=player1.id,
                move_data={"action": "rock"},
                move_number=1,
                time_taken_ms=50
            ),
            Move(
                game_id=game.id,
                player_id=player2.id,
                move_data={"action": "scissors"},
                move_number=2,
                time_taken_ms=75
            ),
            Move(
                game_id=game.id,
                player_id=player1.id,
                move_data={"action": "paper"},
                move_number=3,
                time_taken_ms=45
            ),
            Move(
                game_id=game.id,
                player_id=player2.id,
                move_data={"action": "rock"},
                move_number=4,
                time_taken_ms=80
            ),
        ]
        db.add_all(moves)
        db.commit()
        
        print(f"\nCreated game {game.id} with {len(moves)} moves")
        
        # Create a tournament
        tournament = Tournament(
            name="RPS Championship 2024",
            game_type="rock_paper_scissors",
            format=TournamentFormat.SINGLE_ELIMINATION,
            status=TournamentStatus.SCHEDULED,
            start_time=datetime.utcnow() + timedelta(days=7),
            max_participants=16,
            config={"best_of": 3, "time_limit_seconds": 300}
        )
        db.add(tournament)
        db.commit()
        
        # Register bots for the tournament
        participants = [
            TournamentParticipant(
                tournament_id=tournament.id,
                bot_id=bot1.id,
                seed=1
            ),
            TournamentParticipant(
                tournament_id=tournament.id,
                bot_id=bot2.id,
                seed=2
            ),
            TournamentParticipant(
                tournament_id=tournament.id,
                bot_id=bot3.id,
                seed=3
            )
        ]
        db.add_all(participants)
        db.commit()
        
        print(f"\nCreated tournament '{tournament.name}' with {len(participants)} participants")


def query_example_data():
    """Query and display example data."""
    with get_db_context() as db:
        # Query all active bots
        print("\n=== Active Bots ===")
        bots = db.query(Bot).filter(Bot.is_active == True).all()
        for bot in bots:
            print(f"- {bot.name} (created: {bot.created_at})")
        
        # Query recent games
        print("\n=== Recent Games ===")
        games = db.query(Game).order_by(Game.created_at.desc()).limit(5).all()
        for game in games:
            player_count = len(game.players)
            status = game.status.value
            print(f"- Game {game.id[:8]}... ({game.game_type}): {player_count} players, status: {status}")
        
        # Query tournament participants
        print("\n=== Tournament Participants ===")
        participants = db.query(TournamentParticipant).join(Tournament).join(Bot).all()
        for p in participants:
            print(f"- {p.bot.name} in '{p.tournament.name}' (seed: {p.seed})")
        
        # Complex query: Get bots with their win counts
        print("\n=== Bot Win Statistics ===")
        from sqlalchemy import func
        
        bot_wins = db.query(
            Bot.name,
            func.count(Game.id).label('wins')
        ).join(
            Game, Game.winner_id == Bot.id
        ).group_by(Bot.id).all()
        
        for bot_name, wins in bot_wins:
            print(f"- {bot_name}: {wins} wins")


def main():
    """Run the example."""
    print("Initializing database...")
    init_db()
    
    print("\nCreating example data...")
    create_example_data()
    
    print("\nQuerying example data...")
    query_example_data()
    
    print("\nExample completed!")


if __name__ == "__main__":
    main()