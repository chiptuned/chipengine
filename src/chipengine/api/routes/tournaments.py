"""
Tournament API routes for ChipEngine.

Handles tournament creation, registration, and management.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...database import engine
from ...database.models import Tournament, TournamentStatus, TournamentFormat
from ...core.tournament import TournamentManager, TournamentError


# Request/Response models
class CreateTournamentRequest(BaseModel):
    """Request to create a new tournament."""
    name: str
    game_type: str
    format: str = "single_elimination"  # single_elimination, round_robin
    max_participants: Optional[int] = None
    config: dict = {}


class CreateTournamentResponse(BaseModel):
    """Response when creating a tournament."""
    tournament_id: str
    name: str
    game_type: str
    format: str
    status: str
    max_participants: Optional[int]
    created_at: str


class JoinTournamentRequest(BaseModel):
    """Request to join a tournament."""
    bot_id: str


class JoinTournamentResponse(BaseModel):
    """Response when joining a tournament."""
    tournament_id: str
    bot_id: str
    seed: Optional[int]
    registered_at: str


class TournamentInfo(BaseModel):
    """Tournament information."""
    tournament_id: str
    name: str
    game_type: str
    format: str
    status: str
    created_at: str
    start_time: Optional[str]
    end_time: Optional[str]
    max_participants: Optional[int]
    current_participants: int
    config: dict


class TournamentListResponse(BaseModel):
    """Response listing tournaments."""
    tournaments: List[TournamentInfo]
    total: int


class BracketResponse(BaseModel):
    """Tournament bracket/standings response."""
    tournament_id: str
    format: str
    status: str
    data: dict  # Format-specific bracket data


# Create router
router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


def get_db():
    """Get database session."""
    with Session(engine) as session:
        yield session


@router.post("", response_model=CreateTournamentResponse)
async def create_tournament(
    request: CreateTournamentRequest,
    db: Session = Depends(get_db)
):
    """Create a new tournament."""
    try:
        # Validate format
        try:
            format_enum = TournamentFormat(request.format)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tournament format: {request.format}"
            )
        
        # Create tournament
        manager = TournamentManager(db)
        tournament = manager.create_tournament(
            name=request.name,
            game_type=request.game_type,
            format=format_enum,
            max_participants=request.max_participants,
            config=request.config
        )
        
        return CreateTournamentResponse(
            tournament_id=tournament.id,
            name=tournament.name,
            game_type=tournament.game_type,
            format=tournament.format.value,
            status=tournament.status.value,
            max_participants=tournament.max_participants,
            created_at=tournament.created_at.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=TournamentListResponse)
async def list_tournaments(
    status: Optional[str] = None,
    game_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List tournaments with optional filtering."""
    query = db.query(Tournament)
    
    # Apply filters
    if status:
        try:
            status_enum = TournamentStatus(status)
            query = query.filter(Tournament.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tournament status: {status}"
            )
    
    if game_type:
        query = query.filter(Tournament.game_type == game_type)
    
    # Get total count
    total = query.count()
    
    # Get tournaments
    tournaments = query.order_by(
        Tournament.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    # Build response
    tournament_list = []
    for t in tournaments:
        # Count participants
        participant_count = len(t.participants)
        
        tournament_list.append(TournamentInfo(
            tournament_id=t.id,
            name=t.name,
            game_type=t.game_type,
            format=t.format.value,
            status=t.status.value,
            created_at=t.created_at.isoformat(),
            start_time=t.start_time.isoformat() if t.start_time else None,
            end_time=t.end_time.isoformat() if t.end_time else None,
            max_participants=t.max_participants,
            current_participants=participant_count,
            config=t.config or {}
        ))
    
    return TournamentListResponse(
        tournaments=tournament_list,
        total=total
    )


@router.get("/{tournament_id}", response_model=TournamentInfo)
async def get_tournament(
    tournament_id: str,
    db: Session = Depends(get_db)
):
    """Get tournament details."""
    tournament = db.query(Tournament).filter_by(id=tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    # Count participants
    participant_count = len(tournament.participants)
    
    return TournamentInfo(
        tournament_id=tournament.id,
        name=tournament.name,
        game_type=tournament.game_type,
        format=tournament.format.value,
        status=tournament.status.value,
        created_at=tournament.created_at.isoformat(),
        start_time=tournament.start_time.isoformat() if tournament.start_time else None,
        end_time=tournament.end_time.isoformat() if tournament.end_time else None,
        max_participants=tournament.max_participants,
        current_participants=participant_count,
        config=tournament.config or {}
    )


@router.post("/{tournament_id}/join", response_model=JoinTournamentResponse)
async def join_tournament(
    tournament_id: str,
    request: JoinTournamentRequest,
    db: Session = Depends(get_db)
):
    """Join a tournament."""
    try:
        manager = TournamentManager(db)
        participant = manager.join_tournament(tournament_id, request.bot_id)
        
        return JoinTournamentResponse(
            tournament_id=participant.tournament_id,
            bot_id=participant.bot_id,
            seed=participant.seed,
            registered_at=participant.registered_at.isoformat()
        )
    
    except TournamentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tournament_id}/start")
async def start_tournament(
    tournament_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a tournament and begin scheduling games."""
    try:
        manager = TournamentManager(db)
        tournament = manager.start_tournament(tournament_id)
        
        # Schedule background task to execute games
        background_tasks.add_task(execute_tournament_games, tournament_id)
        
        return {
            "tournament_id": tournament.id,
            "status": tournament.status.value,
            "message": "Tournament started successfully"
        }
    
    except TournamentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tournament_id}/bracket", response_model=BracketResponse)
async def get_tournament_bracket(
    tournament_id: str,
    db: Session = Depends(get_db)
):
    """Get tournament bracket or standings."""
    try:
        # Check tournament exists
        tournament = db.query(Tournament).filter_by(id=tournament_id).first()
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        manager = TournamentManager(db)
        bracket_data = manager.get_bracket(tournament_id)
        
        return BracketResponse(
            tournament_id=tournament_id,
            format=tournament.format.value,
            status=tournament.status.value,
            data=bracket_data
        )
    
    except TournamentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def execute_tournament_games(tournament_id: str):
    """
    Background task to execute tournament games.
    
    This function runs all games in a tournament automatically,
    advancing rounds as needed until the tournament is complete.
    """
    with Session(engine) as db:
        manager = TournamentManager(db)
        
        try:
            while True:
                # Get all waiting games for this tournament
                from ...database.models import Game, GameStatus
                
                waiting_games = db.query(Game).filter_by(
                    tournament_id=tournament_id,
                    status=GameStatus.WAITING
                ).all()
                
                if not waiting_games:
                    # No games to execute, try to advance tournament
                    if not manager.advance_tournament(tournament_id):
                        # Tournament is complete
                        break
                    continue
                
                # Execute each waiting game
                for game in waiting_games:
                    try:
                        manager.execute_game(game.id)
                    except Exception as e:
                        print(f"Error executing game {game.id}: {e}")
                        # Mark game as cancelled to prevent blocking
                        game.status = GameStatus.CANCELLED
                        db.commit()
                
                # Small delay to prevent tight loop
                import asyncio
                await asyncio.sleep(0.1)
        
        except Exception as e:
            print(f"Error in tournament execution: {e}")
            # Mark tournament as cancelled on critical error
            tournament = db.query(Tournament).filter_by(id=tournament_id).first()
            if tournament and tournament.status == TournamentStatus.IN_PROGRESS:
                tournament.status = TournamentStatus.CANCELLED
                db.commit()