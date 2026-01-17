# Oracle - League of Legends Coaching Platform

Oracle is a lightweight coaching platform for League of Legends teams, designed for small teams (~20 users/day). It provides player statistics, draft planning, and coach-player collaboration tools.

## Features (MVP)

- **Simple Access**: Shared access code with role selection (Coach/Player/Head Coach)
- **Team Management**: Track 5 players with multiple Riot accounts (main + smurfs)
- **Statistics**:
  - Player stats (KDA, CS/min, Gold/min, Vision/min, KP%)
  - Lane statistics (e.g., botlane combined stats)
  - SoloQ tracking via Riot Games API
- **Coach-Player Space**: Objectives and notes management
- **Draft Planner**: Track drafts with picks/bans, results, and winrate

## Tech Stack

- **Backend**: FastAPI (Python 3.12), SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS
- **Infrastructure**: Docker Compose (local), Railway (production)
- **Testing**: pytest, ruff

## Prerequisites

- Docker & Docker Compose
- Riot Games API Key ([Get one here](https://developer.riotgames.com))
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

## Quick Start

### 1. Clone and Setup

```bash
# Copy environment variables
cp .env.example .env

# Edit .env and add your Riot API key
# RIOT_API_KEY=RGAPI-your-key-here
```

### 2. Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# The application will be available at:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 3. Initialize Database

```bash
# Run Alembic migrations (in backend container)
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
docker-compose exec backend alembic upgrade head
```

### 4. Access the Application

Open your browser at `http://localhost:5173`

- **Access Code**: `oracle2026` (default, change in `.env`)
- **Roles**: coach, player, head_coach

## Project Structure

```
oracle/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   └── riot/         # Riot API client
│   ├── tests/            # pytest tests
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/             # Vue 3 frontend
│   ├── src/
│   │   ├── views/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── stores/       # Pinia stores
│   │   ├── router/       # Vue Router
│   │   └── api/          # API client
│   └── package.json
├── docker-compose.yml
├── CLAUDE.md            # North Star document
└── README.md
```

## Environment Variables

### Backend

```env
DATABASE_URL=postgresql://oracle_user:oracle_password@postgres:5432/oracle_db
RIOT_API_KEY=RGAPI-your-key-here
RIOT_API_REGION=euw1
RIOT_API_CACHE_TTL=3600
ACCESS_CODE=oracle2026
JWT_SECRET=your-secret-key-change-in-production
```

### Frontend

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Development

### Backend Only

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Only

```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Format & lint
docker-compose exec backend ruff format .
docker-compose exec backend ruff check .
```

## API Endpoints

See full API documentation at `http://localhost:8000/docs` (OpenAPI/Swagger UI)

### Key Endpoints

- `POST /api/v1/auth/validate-code` - Validate access code
- `GET /api/v1/players` - List players
- `GET /api/v1/players/{id}` - Get player details
- `GET /api/v1/stats/player/{id}` - Get player stats
- `POST /api/v1/players/{id}/notes` - Add note/objective
- `GET /api/v1/drafts` - List drafts
- `POST /api/v1/stats/refresh/{riot_account_id}` - Fetch new matches from Riot API

## Riot API Integration

The app uses the Riot Games API to fetch match data:

- **Rate Limits**: 20 req/1s, 100 req/2min (Development key)
- **Caching**: Matches stored in database to avoid re-fetching
- **Regions**: Configurable via `RIOT_API_REGION` (default: euw1)

### Fetching Player Stats

1. Add player via frontend
2. Add Riot account (summoner_name + tag_line)
3. Click "Refresh Stats" to fetch recent matches
4. Stats auto-compute from stored games

## Deployment (Railway)

### Backend

1. Create Railway project
2. Add PostgreSQL service
3. Add backend service (use `backend/Dockerfile`)
4. Set environment variables
5. Deploy

### Frontend

1. Add frontend service (use `frontend/Dockerfile`)
2. Set `VITE_API_BASE_URL` to backend URL
3. Deploy

### Database Migration

```bash
# SSH into backend container
railway run alembic upgrade head
```

## Roadmap (Post-MVP)

- [ ] Champion builds per player
- [ ] Advanced oracle (matchup stats, predictions)
- [ ] Behavioral stats (early deaths, roam frequency)
- [ ] Competitive game tagging
- [ ] Redis caching for Riot API
- [ ] CI/CD pipeline
- [ ] Multi-team support

## Contributing

This is an MVP for a small team. Contributions welcome but keep it simple!

## License

MIT

## Support

For issues or questions, check [CLAUDE.md](./CLAUDE.md) for architecture details.

---

Built with FastAPI, Vue 3, and the Riot Games API.
