from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from app.routers import auth, coaches, drafts, games, player_notes, players, riot_accounts, stats

app = FastAPI(
    title="Oracle API",
    description="League of Legends coaching app API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/riot.txt")
async def riot_verification():
    """Serve riot.txt for Riot Games verification"""
    return FileResponse("riot.txt", media_type="text/plain")
