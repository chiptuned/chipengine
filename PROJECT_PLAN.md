# ChipEngine - Project Plan

## Vision
Build a lean, extensible chip engine for bot competitions. Start with Rock Paper Scissors to prove the concept, then expand to Poker and beyond.

## Core Principles

1. **Ship Fast, Learn Fast**: Deploy working software weekly
2. **Lean Development**: Minimum viable features, maximum user value
3. **Bot-First Design**: API and architecture optimized for AI development
4. **Extensible Architecture**: Easy to add new games without breaking existing ones
5. **Real User Testing**: Get feedback from actual bot developers early

## Technical Architecture

### Backend (Python + FastAPI)
```
chipengine/
├── core/              # Game engine interfaces
│   ├── base_game.py   # BaseGame abstract class
│   ├── player.py      # Player and Bot interfaces
│   └── tournament.py  # Tournament management
├── games/             # Game implementations
│   ├── rps.py         # Rock Paper Scissors
│   └── poker.py       # Texas Hold'em (later)
├── api/               # REST API
│   ├── routes/        # API endpoints
│   └── websockets.py  # Real-time updates
├── db/                # Database models
└── server.py          # FastAPI application
```

### Frontend (React + Vite + Tailwind)
```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   │   ├── ui/        # Base components (buttons, cards, etc)
│   │   └── layout/    # Layout components
│   ├── games/         # Game-specific components
│   │   ├── rps/       # Rock Paper Scissors UI
│   │   └── poker/     # Poker UI (later)
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utilities and API client
│   ├── types/         # TypeScript type definitions
│   └── stores/        # State management (Zustand)
├── public/
└── package.json       # Vite + Tailwind + TypeScript
```

### Key Design Decisions

1. **Multi-Game Architecture**: Each game implements BaseGame interface
2. **Isolated Game Logic**: Pure functions for game rules (easy to test/optimize)
3. **API-First**: Web UI is just another client of the API
4. **Real-time Updates**: WebSocket connections for live game state
5. **Modern Frontend**: Vite for fast dev, Tailwind for styling, TypeScript for safety
6. **Component Library**: Headless UI + custom components for consistency
7. **State Management**: Zustand for simple, performant state
8. **SQLite → PostgreSQL**: Start simple, scale when needed

## Development Phases

### Phase 1: RPS MVP (Week 1-2)
**Goal**: Working website that bot developers can use

**Deliverables**:
- Rock Paper Scissors game implementation
- REST API for bot actions
- Basic web interface
- Single elimination tournaments
- Docker deployment

**Success Criteria**:
- 5+ bot developers testing the API
- 100+ games played
- Sub-100ms API response times
- Zero critical bugs

### Phase 2: Multi-Game Platform (Week 3-4)
**Goal**: Prove architecture scales to multiple games

**Deliverables**:
- Texas Hold'em implementation
- Game selection in UI
- Poker-specific API endpoints
- Tournament support for both games
- PokerHandEvaluator integration

**Success Criteria**:
- Both games working with same bot API pattern
- Bots can play both RPS and Poker
- Architecture proven extensible
- Easy to add new games

### Phase 3: Scale & Polish (Week 5+)
**Goal**: Production-ready platform

**Deliverables**:
- Performance optimization
- Advanced tournament formats
- User management and authentication
- Analytics and statistics
- Mobile-responsive UI

**Success Criteria**:
- 1000+ concurrent users
- 10+ different bot implementations
- Professional tournament features
- Ready for next game addition

## Risk Mitigation

**Technical Risks**:
- *Complex game state*: Start with simple RPS, validate architecture
- *Performance bottlenecks*: Profile early, optimize based on real usage
- *Scaling challenges*: Start with SQLite, migrate to PostgreSQL when needed

**Product Risks**:
- *No user adoption*: Deploy early, get feedback from real bot developers
- *Over-engineering*: Focus on MVP features, resist adding complexity
- *Feature creep*: Stick to roadmap, defer non-critical features

## Success Metrics

**Week 2 (RPS MVP)**:
- [ ] Working deployment accessible via URL
- [ ] 5+ external bot developers using API
- [ ] 100+ games played through platform
- [ ] <100ms average API response time
- [ ] Zero data loss or critical bugs

**Week 4 (Multi-Game)**:
- [ ] Both RPS and Poker playable
- [ ] Same bot interface works for both games
- [ ] Tournaments for both game types
- [ ] Architecture documented and extensible

**Week 8 (Scale)**:
- [ ] 1000+ registered users
- [ ] 10+ unique bot implementations
- [ ] Sub-50ms API response times
- [ ] Swiss tournament system
- [ ] Analytics dashboard

This plan balances ambitious goals with pragmatic execution, ensuring we ship working software while building a foundation for long-term growth.