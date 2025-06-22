"""
Statistics and game history API routes.

Provides endpoints for retrieving game history, player statistics,
leaderboards, and platform-wide analytics.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func, desc, and_

from ...database import engine
from ...database.models import Game, Player, Move, Bot, GameStatus
from ..models import (
    GameSummary, GameDetail, BotStatistics, 
    LeaderboardEntry, PlatformStatistics
)


# Create router
router = APIRouter(prefix="/api/stats", tags=["statistics"])

# Create session factory
SessionLocal = sessionmaker(bind=engine)


@router.get("/games", response_model=List[GameSummary])
async def list_games(
    game_type: Optional[str] = Query(None, description="Filter by game type"),
    status: Optional[str] = Query(None, description="Filter by game status"),
    bot_id: Optional[str] = Query(None, description="Filter by bot participation"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of games to return"),
    offset: int = Query(0, ge=0, description="Number of games to skip"),
    sort: str = Query("created_at_desc", description="Sort order: created_at_desc, created_at_asc, completed_at_desc")
):
    """List games with optional filters."""
    with SessionLocal() as session:
        query = session.query(Game)
        
        # Apply filters
        if game_type:
            query = query.filter(Game.game_type == game_type)
        
        if status:
            try:
                status_enum = GameStatus(status)
                query = query.filter(Game.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        if bot_id:
            # Filter games where the bot participated
            query = query.join(Player).filter(Player.bot_id == bot_id)
        
        # Apply sorting
        if sort == "created_at_desc":
            query = query.order_by(desc(Game.created_at))
        elif sort == "created_at_asc":
            query = query.order_by(Game.created_at)
        elif sort == "completed_at_desc":
            query = query.order_by(desc(Game.completed_at))
        
        # Apply pagination
        games = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        result = []
        for game in games:
            # Get players for this game
            players = session.query(Player).filter_by(game_id=game.id).all()
            
            # Calculate duration
            duration = None
            if game.completed_at and game.created_at:
                duration = (game.completed_at - game.created_at).total_seconds()
            
            result.append(GameSummary(
                game_id=game.id,
                game_type=game.game_type,
                status=game.status.value,
                created_at=game.created_at.isoformat() if game.created_at else "",
                completed_at=game.completed_at.isoformat() if game.completed_at else None,
                players=[
                    {
                        "bot_id": p.bot_id,
                        "player_number": p.player_number,
                        "final_position": p.final_position,
                        "score": p.score
                    }
                    for p in players
                ],
                winner_id=game.winner_id,
                duration_seconds=duration
            ))
        
        return result


@router.get("/games/{game_id}", response_model=GameDetail)
async def get_game_detail(game_id: str):
    """Get detailed information about a specific game including all moves."""
    with SessionLocal() as session:
        # Get game
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Get players
        players = session.query(Player).filter_by(game_id=game_id).all()
        
        # Get moves
        moves = session.query(Move).filter_by(game_id=game_id).order_by(Move.timestamp).all()
        
        # Calculate duration
        duration = None
        if game.completed_at and game.created_at:
            duration = (game.completed_at - game.created_at).total_seconds()
        
        # Build response
        return GameDetail(
            game_id=game.id,
            game_type=game.game_type,
            status=game.status.value,
            created_at=game.created_at.isoformat() if game.created_at else "",
            completed_at=game.completed_at.isoformat() if game.completed_at else None,
            config=game.config or {},
            state=game.state or {},
            players=[
                {
                    "bot_id": p.bot_id,
                    "player_number": p.player_number,
                    "final_position": p.final_position,
                    "score": p.score,
                    "joined_at": p.joined_at.isoformat() if p.joined_at else None
                }
                for p in players
            ],
            moves=[
                {
                    "player_bot_id": next((p.bot_id for p in players if p.id == m.player_id), None),
                    "move_data": m.move_data,
                    "move_number": m.move_number,
                    "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                    "time_taken_ms": m.time_taken_ms
                }
                for m in moves
            ],
            winner_id=game.winner_id,
            duration_seconds=duration
        )


@router.get("/players/{bot_id}", response_model=BotStatistics)
async def get_bot_statistics(
    bot_id: str,
    game_type: Optional[str] = Query(None, description="Filter statistics by game type")
):
    """Get detailed statistics for a specific bot."""
    with SessionLocal() as session:
        # Get bot
        bot = session.query(Bot).filter_by(id=bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Base query for bot's games
        base_query = session.query(Game).join(Player).filter(Player.bot_id == bot_id)
        
        # Apply game type filter if specified
        if game_type:
            base_query = base_query.filter(Game.game_type == game_type)
        
        # Get total games
        total_games = base_query.count()
        
        # Get wins, losses, draws
        completed_games = base_query.filter(Game.status == GameStatus.COMPLETED)
        wins = completed_games.filter(Game.winner_id == bot_id).count()
        
        # Count games with no winner as draws
        draws = completed_games.filter(Game.winner_id.is_(None)).count()
        
        # Losses are completed games where bot participated but didn't win or draw
        losses = completed_games.count() - wins - draws
        
        # Calculate win rate
        win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
        
        # Get average game duration
        avg_duration_result = session.query(
            func.avg(Game.completed_at - Game.created_at)
        ).join(Player).filter(
            Player.bot_id == bot_id,
            Game.status == GameStatus.COMPLETED,
            Game.completed_at.isnot(None)
        ).scalar()
        
        avg_duration = avg_duration_result.total_seconds() if avg_duration_result else 0.0
        
        # Get games by type
        games_by_type_result = session.query(
            Game.game_type,
            func.count(Game.id)
        ).join(Player).filter(
            Player.bot_id == bot_id
        ).group_by(Game.game_type).all()
        
        games_by_type = {game_type: count for game_type, count in games_by_type_result}
        
        # Get recent games
        recent_games_query = base_query.order_by(desc(Game.created_at)).limit(10)
        recent_games = []
        
        for game in recent_games_query:
            players = session.query(Player).filter_by(game_id=game.id).all()
            duration = None
            if game.completed_at and game.created_at:
                duration = (game.completed_at - game.created_at).total_seconds()
            
            recent_games.append(GameSummary(
                game_id=game.id,
                game_type=game.game_type,
                status=game.status.value,
                created_at=game.created_at.isoformat() if game.created_at else "",
                completed_at=game.completed_at.isoformat() if game.completed_at else None,
                players=[
                    {
                        "bot_id": p.bot_id,
                        "player_number": p.player_number,
                        "final_position": p.final_position,
                        "score": p.score
                    }
                    for p in players
                ],
                winner_id=game.winner_id,
                duration_seconds=duration
            ))
        
        return BotStatistics(
            bot_id=bot.id,
            bot_name=bot.name,
            total_games=total_games,
            wins=wins,
            losses=losses,
            draws=draws,
            win_rate=win_rate,
            avg_game_duration=avg_duration,
            games_by_type=games_by_type,
            recent_games=recent_games
        )


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    game_type: str = Query("rps", description="Game type for leaderboard"),
    limit: int = Query(20, ge=1, le=100, description="Number of entries to return"),
    min_games: int = Query(10, ge=1, description="Minimum games played to qualify")
):
    """Get leaderboard for a specific game type."""
    with SessionLocal() as session:
        # Query to get bot statistics for the game type
        bot_stats = session.query(
            Bot.id,
            Bot.name,
            func.count(Game.id).label("games_played"),
            func.count(func.nullif(Game.winner_id == Bot.id, False)).label("wins")
        ).join(
            Player, Player.bot_id == Bot.id
        ).join(
            Game, Game.id == Player.game_id
        ).filter(
            Game.game_type == game_type,
            Game.status == GameStatus.COMPLETED
        ).group_by(
            Bot.id, Bot.name
        ).having(
            func.count(Game.id) >= min_games
        ).all()
        
        # Calculate win rates and create leaderboard entries
        leaderboard = []
        for bot_id, bot_name, games_played, wins in bot_stats:
            win_rate = (wins / games_played * 100) if games_played > 0 else 0.0
            # Simple points system: 3 points per win
            points = wins * 3
            
            leaderboard.append({
                "bot_id": bot_id,
                "bot_name": bot_name,
                "games_played": games_played,
                "wins": wins,
                "win_rate": win_rate,
                "points": points
            })
        
        # Sort by points (descending) then by win rate
        leaderboard.sort(key=lambda x: (x["points"], x["win_rate"]), reverse=True)
        
        # Add ranks and convert to response model
        result = []
        for rank, entry in enumerate(leaderboard[:limit], 1):
            result.append(LeaderboardEntry(
                rank=rank,
                **entry
            ))
        
        return result


@router.get("/summary", response_model=PlatformStatistics)
async def get_platform_statistics():
    """Get platform-wide statistics and analytics."""
    with SessionLocal() as session:
        # Total games
        total_games = session.query(Game).count()
        
        # Active and completed games
        active_games = session.query(Game).filter(
            Game.status == GameStatus.IN_PROGRESS
        ).count()
        
        completed_games = session.query(Game).filter(
            Game.status == GameStatus.COMPLETED
        ).count()
        
        # Total and active bots
        total_bots = session.query(Bot).count()
        
        # Active bots (played in last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_bots = session.query(Bot).join(Player).join(Game).filter(
            Game.created_at >= seven_days_ago
        ).distinct().count()
        
        # Games in last 24h and 7d
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        games_last_24h = session.query(Game).filter(
            Game.created_at >= one_day_ago
        ).count()
        
        games_last_7d = session.query(Game).filter(
            Game.created_at >= seven_days_ago
        ).count()
        
        # Popular game types
        game_type_stats = session.query(
            Game.game_type,
            func.count(Game.id)
        ).group_by(Game.game_type).all()
        
        popular_game_types = {game_type: count for game_type, count in game_type_stats}
        
        # Peak concurrent games (simplified - count max games in any hour)
        # This is a simplified implementation - in production you'd track this in real-time
        peak_concurrent = active_games  # Current active games as approximation
        
        # Average game duration
        avg_duration_result = session.query(
            func.avg(Game.completed_at - Game.created_at)
        ).filter(
            Game.status == GameStatus.COMPLETED,
            Game.completed_at.isnot(None)
        ).scalar()
        
        avg_duration = avg_duration_result.total_seconds() if avg_duration_result else 0.0
        
        return PlatformStatistics(
            total_games=total_games,
            active_games=active_games,
            completed_games=completed_games,
            total_bots=total_bots,
            active_bots=active_bots,
            games_last_24h=games_last_24h,
            games_last_7d=games_last_7d,
            popular_game_types=popular_game_types,
            peak_concurrent_games=peak_concurrent,
            avg_game_duration=avg_duration
        )