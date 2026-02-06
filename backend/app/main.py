from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import (
    auth,
    calendar,
    coaches,
    draft_series,
    drafts,
    games,
    player_notes,
    players,
    riot_accounts,
    scrim_management,
    stats,
    tier_list,
)


class CORSMiddlewareCustom(BaseHTTPMiddleware):
    """Custom CORS middleware that handles all responses including errors"""

    async def dispatch(self, request: Request, call_next):
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = JSONResponse(content={})
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response

        try:
            response = await call_next(request)
        except Exception as e:
            response = JSONResponse(
                status_code=500,
                content={"detail": str(e)}
            )

        # Add CORS headers to ALL responses
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

        return response


app = FastAPI(
    title="Oracle API",
    description="League of Legends coaching app API",
    version="1.0.0",
)

# Add custom CORS middleware FIRST (before other middleware)
app.add_middleware(CORSMiddlewareCustom)

# Include routers
app.include_router(auth.router)
app.include_router(players.router)
app.include_router(coaches.router)
app.include_router(riot_accounts.router)
app.include_router(player_notes.router)
app.include_router(drafts.router)
app.include_router(draft_series.router)
app.include_router(games.router)
app.include_router(stats.router)
app.include_router(calendar.router)
app.include_router(tier_list.router)
app.include_router(scrim_management.router)


@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
