# Oracle - Quick Start Guide

## Prerequisites

- Docker & Docker Compose installed
- Riot Games API Key ([Get one here](https://developer.riotgames.com))

## Setup (First Time)

### 1. Clone and Configure

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your Riot API key
# RIOT_API_KEY=RGAPI-your-key-here
```

### 2. Start Services

```bash
# Build and start all services
docker compose up --build -d

# Wait for services to be ready (about 30 seconds)
docker compose ps
```

### 3. Initialize Database

```bash
# Generate and apply migrations
docker compose exec backend alembic revision --autogenerate -m "Initial migration"
docker compose exec backend alembic upgrade head
```

### 4. Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Run tests
docker compose exec backend pytest -v
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Login Credentials

- **Access Code**: `oracle2026` (configurable in `.env`)
- **Roles**: `coach`, `player`, `head_coach`

## Common Commands

### Start/Stop

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
```

### Development

```bash
# Run tests
docker compose exec backend pytest

# Format code
docker compose exec backend ruff format .

# Lint code
docker compose exec backend ruff check .

# Access backend shell
docker compose exec backend bash

# Access database
docker compose exec postgres psql -U oracle_user -d oracle_db
```

### Database

```bash
# Create new migration
docker compose exec backend alembic revision --autogenerate -m "Migration message"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback migration
docker compose exec backend alembic downgrade -1
```

### Clean Up

```bash
# Stop and remove containers, networks, volumes
docker compose down -v

# Remove images
docker rmi gabri-backend gabri-frontend
```

## Project Structure

```
oracle/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database connection
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic
│   │   └── riot/             # Riot API client
│   └── tests/                # pytest tests
├── frontend/          # Vue 3 frontend
│   └── src/
│       ├── views/            # Page components
│       ├── components/       # Reusable components
│       ├── stores/           # Pinia state management
│       ├── router/           # Vue Router config
│       ├── api/              # API client
│       └── types/            # TypeScript types
├── docker-compose.yml        # Docker services config
├── .env                      # Environment variables
├── CLAUDE.md                 # Architecture & decisions
└── README.md                 # Full documentation
```

## API Endpoints

### Authentication

```bash
# Validate access code
curl -X POST http://localhost:8000/api/v1/auth/validate-code \
  -H "Content-Type: application/json" \
  -d '{"code":"oracle2026","role":"coach"}'
```

### Players

```bash
# Create player
curl -X POST http://localhost:8000/api/v1/players \
  -H "Content-Type: application/json" \
  -d '{"summoner_name":"Faker","role":"mid"}'

# List players
curl http://localhost:8000/api/v1/players

# Get player details
curl http://localhost:8000/api/v1/players/1
```

### Riot Accounts

```bash
# Add Riot account to player
curl -X POST http://localhost:8000/api/v1/players/1/riot-accounts \
  -H "Content-Type: application/json" \
  -d '{"summoner_name":"Hide on bush","tag_line":"KR1","is_main":true}'
```

### Stats

```bash
# Get player stats
curl http://localhost:8000/api/v1/stats/player/1

# Refresh stats from Riot API
curl -X POST http://localhost:8000/api/v1/stats/refresh/1
```

## Troubleshooting

### Backend not starting

```bash
# Check logs
docker compose logs backend

# Restart backend
docker compose restart backend
```

### Database connection issues

```bash
# Check postgres status
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Verify connection
docker compose exec postgres pg_isready -U oracle_user
```

### Frontend not loading

```bash
# Check frontend logs
docker compose logs frontend

# Restart frontend
docker compose restart frontend

# Rebuild frontend
docker compose up --build frontend
```

### Port conflicts

If ports 5173, 8000, or 5432 are already in use:

1. Edit `docker-compose.yml`
2. Change port mappings (e.g., `5174:5173`)
3. Update `frontend/.env` with new backend port
4. Restart services

## Next Steps

1. Add your team's players via the frontend
2. Add Riot accounts to each player
3. Fetch match data using the "Refresh Stats" button
4. View player statistics and add notes/objectives
5. Create drafts in the Draft Planner (Head Coach role)

## Production Deployment (Railway)

See [README.md](./README.md) for Railway deployment instructions.

## Support

- Check [CLAUDE.md](./CLAUDE.md) for architecture details
- Review [README.md](./README.md) for full documentation
- API docs: http://localhost:8000/docs

---

**Built with FastAPI, Vue 3, and the Riot Games API**
