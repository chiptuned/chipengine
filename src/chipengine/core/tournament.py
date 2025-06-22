"""
Tournament management for ChipEngine.

Handles tournament creation, game scheduling, bracket generation, and results tracking.
"""

from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import random
import math
from enum import Enum
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database import engine
from ..database.models import (
    Tournament, TournamentParticipant, Game, Player, Bot,
    TournamentStatus, TournamentFormat, GameStatus
)
from .base_game import BaseGame, Move
from ..api.game_manager import game_manager


class TournamentError(Exception):
    """Base exception for tournament-related errors."""
    pass


class TournamentManager:
    """
    Manages tournaments including creation, scheduling, and execution.
    
    Supports multiple tournament formats:
    - Single Elimination
    - Double Elimination (future)
    - Round Robin
    - Swiss (future)
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_tournament(
        self,
        name: str,
        game_type: str,
        format: TournamentFormat,
        max_participants: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tournament:
        """Create a new tournament."""
        tournament = Tournament(
            name=name,
            game_type=game_type,
            format=format,
            max_participants=max_participants,
            config=config or {},
            status=TournamentStatus.REGISTRATION_OPEN
        )
        
        self.session.add(tournament)
        self.session.commit()
        
        return tournament
    
    def join_tournament(self, tournament_id: str, bot_id: str) -> TournamentParticipant:
        """Join a bot to a tournament."""
        tournament = self.session.query(Tournament).filter_by(id=tournament_id).first()
        if not tournament:
            raise TournamentError(f"Tournament {tournament_id} not found")
        
        if tournament.status != TournamentStatus.REGISTRATION_OPEN:
            raise TournamentError("Tournament registration is closed")
        
        # Check if bot exists
        bot = self.session.query(Bot).filter_by(id=bot_id).first()
        if not bot:
            raise TournamentError(f"Bot {bot_id} not found")
        
        # Check if bot is already registered
        existing = self.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament_id,
            bot_id=bot_id
        ).first()
        if existing:
            raise TournamentError("Bot is already registered for this tournament")
        
        # Check max participants
        current_count = self.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament_id
        ).count()
        
        if tournament.max_participants and current_count >= tournament.max_participants:
            raise TournamentError("Tournament is full")
        
        # Create participant
        participant = TournamentParticipant(
            tournament_id=tournament_id,
            bot_id=bot_id
        )
        
        self.session.add(participant)
        self.session.commit()
        
        return participant
    
    def start_tournament(self, tournament_id: str) -> Tournament:
        """Start a tournament and schedule initial games."""
        tournament = self.session.query(Tournament).filter_by(id=tournament_id).first()
        if not tournament:
            raise TournamentError(f"Tournament {tournament_id} not found")
        
        if tournament.status != TournamentStatus.REGISTRATION_OPEN:
            raise TournamentError("Tournament has already started or is completed")
        
        # Get participants
        participants = self.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament_id
        ).all()
        
        if len(participants) < 2:
            raise TournamentError("Tournament needs at least 2 participants")
        
        # Update tournament status
        tournament.status = TournamentStatus.IN_PROGRESS
        tournament.start_time = datetime.utcnow()
        
        # Seed participants
        self._seed_participants(tournament, participants)
        
        # Schedule initial games based on format
        if tournament.format == TournamentFormat.SINGLE_ELIMINATION:
            self._schedule_single_elimination_round(tournament, 1)
        elif tournament.format == TournamentFormat.ROUND_ROBIN:
            self._schedule_round_robin_games(tournament)
        else:
            raise TournamentError(f"Tournament format {tournament.format} not yet implemented")
        
        self.session.commit()
        return tournament
    
    def _seed_participants(self, tournament: Tournament, participants: List[TournamentParticipant]):
        """Assign seeds to participants (random for now, could use rankings later)."""
        shuffled = list(participants)
        random.shuffle(shuffled)
        
        for i, participant in enumerate(shuffled):
            participant.seed = i + 1
    
    def _schedule_single_elimination_round(self, tournament: Tournament, round_number: int):
        """Schedule games for a single elimination round."""
        # Get active participants (not eliminated)
        participants = self.session.query(TournamentParticipant).filter(
            and_(
                TournamentParticipant.tournament_id == tournament.id,
                TournamentParticipant.eliminated == False
            )
        ).order_by(TournamentParticipant.seed).all()
        
        # Calculate number of games needed
        num_participants = len(participants)
        num_games = num_participants // 2
        
        # Handle bye (odd number of participants)
        has_bye = num_participants % 2 == 1
        
        # Create games
        games_created = []
        for i in range(num_games):
            player1 = participants[i * 2]
            player2 = participants[i * 2 + 1]
            
            game = self._create_tournament_game(
                tournament,
                [player1.bot_id, player2.bot_id],
                round_number
            )
            games_created.append(game)
        
        # Handle bye - advance the last participant
        if has_bye:
            bye_participant = participants[-1]
            bye_participant.wins += 1
            bye_participant.games_played += 1
        
        return games_created
    
    def _schedule_round_robin_games(self, tournament: Tournament):
        """Schedule all games for a round-robin tournament."""
        participants = self.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament.id
        ).all()
        
        bot_ids = [p.bot_id for p in participants]
        
        # Generate all pairings
        games_created = []
        round_num = 1
        
        for i in range(len(bot_ids)):
            for j in range(i + 1, len(bot_ids)):
                game = self._create_tournament_game(
                    tournament,
                    [bot_ids[i], bot_ids[j]],
                    round_num
                )
                games_created.append(game)
        
        return games_created
    
    def _create_tournament_game(
        self,
        tournament: Tournament,
        bot_ids: List[str],
        round_number: int
    ) -> Game:
        """Create a game for a tournament."""
        # Create game record
        game = Game(
            game_type=tournament.game_type,
            tournament_id=tournament.id,
            round_number=round_number,
            status=GameStatus.WAITING,
            config=tournament.config.get("game_config", {})
        )
        
        self.session.add(game)
        self.session.flush()  # Get game ID
        
        # Create player records
        for i, bot_id in enumerate(bot_ids):
            player = Player(
                bot_id=bot_id,
                game_id=game.id,
                player_number=i + 1
            )
            self.session.add(player)
        
        return game
    
    def execute_game(self, game_id: str) -> Game:
        """Execute a tournament game with bots making automated moves."""
        game_record = self.session.query(Game).filter_by(id=game_id).first()
        if not game_record:
            raise TournamentError(f"Game {game_id} not found")
        
        if game_record.status != GameStatus.WAITING:
            raise TournamentError("Game has already been played")
        
        # Get player records
        players = self.session.query(Player).filter_by(game_id=game_id).all()
        player_ids = [p.bot_id for p in players]
        
        # Create game instance directly
        if game_record.game_type not in game_manager.game_registry:
            raise TournamentError(f"Unknown game type: {game_record.game_type}")
        
        game_class = game_manager.game_registry[game_record.game_type]
        config = game_record.config or {}
        
        # Create game instance with tournament game_id
        if game_record.game_type in ["rps", "rock_paper_scissors"]:
            total_rounds = config.get("total_rounds", 1)
            game_instance = game_class(game_id, player_ids, total_rounds)
        else:
            game_instance = game_class(game_id, player_ids)
        
        # Add to game_manager for tracking
        game_manager.active_games[game_id] = game_instance
        game_manager.move_counter[game_id] = 0
        
        # Update game status
        game_record.status = GameStatus.IN_PROGRESS
        game_record.state = game_instance.get_state().dict()
        
        # Play game with random moves (bots should implement their own logic)
        move_count = 0
        max_moves = 1000  # Prevent infinite games
        
        while not game_instance.is_game_over() and move_count < max_moves:
            current_player = game_instance.state.current_player
            valid_moves = game_instance.get_valid_moves(current_player)
            
            if not valid_moves:
                break
            
            # Random move selection (bots would use their own strategy here)
            chosen_move = random.choice(valid_moves)
            
            # Apply move directly (tournament games don't save individual moves to DB)
            move = Move(
                player=current_player,
                action=chosen_move,
                data={}
            )
            game_instance.apply_move(move)
            game_record.state = game_instance.get_state().dict()
            
            move_count += 1
        
        # Complete game
        game_record.status = GameStatus.COMPLETED
        game_record.completed_at = datetime.utcnow()
        
        # Update winner
        winner = game_instance.get_winner()
        if winner:
            game_record.winner_id = winner
            
            # Update participant stats
            self._update_participant_stats(game_record)
        
        self.session.commit()
        
        # Clean up from game_manager
        if game_id in game_manager.active_games:
            del game_manager.active_games[game_id]
        if game_id in game_manager.move_counter:
            del game_manager.move_counter[game_id]
        
        return game_record
    
    def _update_participant_stats(self, game: Game):
        """Update tournament participant statistics after a game."""
        if not game.tournament_id:
            return
        
        # Get players
        players = self.session.query(Player).filter_by(game_id=game.id).all()
        
        for player in players:
            participant = self.session.query(TournamentParticipant).filter_by(
                tournament_id=game.tournament_id,
                bot_id=player.bot_id
            ).first()
            
            if participant:
                participant.games_played += 1
                
                if game.winner_id == player.bot_id:
                    participant.wins += 1
                    participant.score += 3  # 3 points for win
                elif game.winner_id is None:
                    participant.draws += 1
                    participant.score += 1  # 1 point for draw
                    
                    # In single elimination, handle ties by playing another game
                    # For now, we'll randomly eliminate one player on a tie
                    tournament = self.session.query(Tournament).filter_by(
                        id=game.tournament_id
                    ).first()
                    if tournament.format == TournamentFormat.SINGLE_ELIMINATION:
                        # Get all players in this game
                        all_players = self.session.query(Player).filter_by(game_id=game.id).all()
                        if len(all_players) == 2:
                            # Randomly eliminate one player
                            import random
                            loser_idx = random.randint(0, 1)
                            for idx, p in enumerate(all_players):
                                p_participant = self.session.query(TournamentParticipant).filter_by(
                                    tournament_id=game.tournament_id,
                                    bot_id=p.bot_id
                                ).first()
                                if p_participant and idx == loser_idx:
                                    p_participant.eliminated = True
                                    p_participant.losses += 1
                                    p_participant.score -= 1  # Adjust score
                                elif p_participant and idx != loser_idx:
                                    p_participant.wins += 1
                                    p_participant.draws -= 1  # Adjust draws
                                    p_participant.score += 2  # Adjust score
                else:
                    participant.losses += 1
                    
                    # Eliminate in single elimination
                    tournament = self.session.query(Tournament).filter_by(
                        id=game.tournament_id
                    ).first()
                    if tournament.format == TournamentFormat.SINGLE_ELIMINATION:
                        participant.eliminated = True
    
    def advance_tournament(self, tournament_id: str) -> bool:
        """
        Advance tournament to next round if current round is complete.
        Returns True if tournament advanced, False if already complete.
        """
        tournament = self.session.query(Tournament).filter_by(id=tournament_id).first()
        if not tournament:
            raise TournamentError(f"Tournament {tournament_id} not found")
        
        if tournament.status != TournamentStatus.IN_PROGRESS:
            return False
        
        # Check if all games in current round are complete
        incomplete_games = self.session.query(Game).filter(
            and_(
                Game.tournament_id == tournament_id,
                Game.status != GameStatus.COMPLETED
            )
        ).count()
        
        if incomplete_games > 0:
            return False  # Current round not complete
        
        if tournament.format == TournamentFormat.SINGLE_ELIMINATION:
            return self._advance_single_elimination(tournament)
        elif tournament.format == TournamentFormat.ROUND_ROBIN:
            return self._complete_round_robin(tournament)
        
        return False
    
    def _advance_single_elimination(self, tournament: Tournament) -> bool:
        """Advance a single elimination tournament."""
        # Get active participants
        active_participants = self.session.query(TournamentParticipant).filter(
            and_(
                TournamentParticipant.tournament_id == tournament.id,
                TournamentParticipant.eliminated == False
            )
        ).count()
        
        if active_participants <= 1:
            # Tournament is complete
            self._complete_tournament(tournament)
            return False
        
        # Get current round number
        last_game = self.session.query(Game).filter_by(
            tournament_id=tournament.id
        ).order_by(Game.round_number.desc()).first()
        
        next_round = (last_game.round_number + 1) if last_game else 1
        
        # Schedule next round
        self._schedule_single_elimination_round(tournament, next_round)
        self.session.commit()
        
        return True
    
    def _complete_round_robin(self, tournament: Tournament) -> bool:
        """Complete a round-robin tournament."""
        # All games are scheduled at start, so just complete the tournament
        self._complete_tournament(tournament)
        return False
    
    def _complete_tournament(self, tournament: Tournament):
        """Mark tournament as complete and calculate final rankings."""
        tournament.status = TournamentStatus.COMPLETED
        tournament.end_time = datetime.utcnow()
        
        # Calculate final rankings
        participants = self.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament.id
        ).all()
        
        # Sort by score (wins * 3 + draws), then by wins, then by games played
        participants.sort(
            key=lambda p: (-p.score, -p.wins, p.games_played)
        )
        
        # Assign final ranks
        for i, participant in enumerate(participants):
            participant.final_rank = i + 1
    
    def get_bracket(self, tournament_id: str) -> Dict[str, Any]:
        """Get tournament bracket/standings."""
        tournament = self.session.query(Tournament).filter_by(id=tournament_id).first()
        if not tournament:
            raise TournamentError(f"Tournament {tournament_id} not found")
        
        if tournament.format == TournamentFormat.SINGLE_ELIMINATION:
            return self._get_elimination_bracket(tournament)
        elif tournament.format == TournamentFormat.ROUND_ROBIN:
            return self._get_round_robin_standings(tournament)
        
        return {}
    
    def _get_elimination_bracket(self, tournament: Tournament) -> Dict[str, Any]:
        """Get single elimination bracket structure."""
        # Get all games grouped by round
        games_by_round = defaultdict(list)
        games = self.session.query(Game).filter_by(
            tournament_id=tournament.id
        ).order_by(Game.round_number, Game.created_at).all()
        
        for game in games:
            players = self.session.query(Player).filter_by(game_id=game.id).all()
            game_data = {
                "game_id": game.id,
                "status": game.status.value,
                "winner_id": game.winner_id,
                "players": [
                    {
                        "bot_id": p.bot_id,
                        "bot_name": p.bot.name
                    }
                    for p in players
                ]
            }
            games_by_round[game.round_number].append(game_data)
        
        # Get participants with their status
        participants = self.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament.id
        ).all()
        
        participant_data = [
            {
                "bot_id": p.bot_id,
                "bot_name": p.bot.name,
                "seed": p.seed,
                "eliminated": p.eliminated,
                "final_rank": p.final_rank
            }
            for p in participants
        ]
        
        return {
            "format": "single_elimination",
            "rounds": dict(games_by_round),
            "participants": participant_data,
            "total_rounds": math.ceil(math.log2(len(participants)))
        }
    
    def _get_round_robin_standings(self, tournament: Tournament) -> Dict[str, Any]:
        """Get round-robin standings."""
        participants = self.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament.id
        ).order_by(
            TournamentParticipant.score.desc(),
            TournamentParticipant.wins.desc()
        ).all()
        
        standings = []
        for i, p in enumerate(participants):
            standings.append({
                "rank": i + 1,
                "bot_id": p.bot_id,
                "bot_name": p.bot.name,
                "games_played": p.games_played,
                "wins": p.wins,
                "draws": p.draws,
                "losses": p.losses,
                "score": p.score
            })
        
        # Get head-to-head results
        games = self.session.query(Game).filter_by(
            tournament_id=tournament.id,
            status=GameStatus.COMPLETED
        ).all()
        
        head_to_head = defaultdict(dict)
        for game in games:
            players = self.session.query(Player).filter_by(game_id=game.id).all()
            if len(players) == 2:
                p1_id, p2_id = players[0].bot_id, players[1].bot_id
                result = "win" if game.winner_id == p1_id else ("loss" if game.winner_id == p2_id else "draw")
                head_to_head[p1_id][p2_id] = result
                head_to_head[p2_id][p1_id] = "loss" if result == "win" else ("win" if result == "loss" else "draw")
        
        return {
            "format": "round_robin",
            "standings": standings,
            "head_to_head": dict(head_to_head),
            "total_games": len(games),
            "games_remaining": self.session.query(Game).filter_by(
                tournament_id=tournament.id,
                status=GameStatus.WAITING
            ).count()
        }