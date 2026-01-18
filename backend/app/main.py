from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.routers import auth, coaches, drafts, games, player_notes, players, riot_accounts, stats

app = FastAPI(
    title="Oracle API",
    description="League of Legends coaching app API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "http://localhost:3000",  # Alternative local port
        "https://oraclesc.up.railway.app",  # Production frontend
        "https://oracle-services.up.railway.app",  # Production backend (for docs)
        "*",  # Allow all for Railway compatibility
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Additional CORS headers middleware for Railway compatibility
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)

    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "https://oraclesc.up.railway.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    return response

# Include routers
app.include_router(auth.router)
app.include_router(players.router)
app.include_router(coaches.router)
app.include_router(riot_accounts.router)
app.include_router(player_notes.router)
app.include_router(drafts.router)
app.include_router(games.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
