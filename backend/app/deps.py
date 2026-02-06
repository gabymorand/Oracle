"""FastAPI dependencies for authentication and team context"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.team import Team


@dataclass
class TeamContext:
    """Current team context extracted from JWT"""
    team_id: int
    team_name: str
    role: str


def get_optional_team_context(
    authorization: Optional[str] = Header(None),
) -> Optional[TeamContext]:
    """Extract team context from JWT if present (optional auth)"""
    if not authorization:
        return None

    try:
        # Extract token from "Bearer <token>"
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization

        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        team_id = payload.get("team_id")
        team_name = payload.get("team_name")
        role = payload.get("role")

        if not team_id or not role:
            return None

        return TeamContext(
            team_id=team_id,
            team_name=team_name or "",
            role=role,
        )
    except JWTError:
        return None


def get_current_team(
    authorization: str = Header(...),
) -> TeamContext:
    """Extract and validate team context from JWT (required auth)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        # Extract token from "Bearer <token>"
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization

        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        team_id = payload.get("team_id")
        team_name = payload.get("team_name")
        role = payload.get("role")

        if not team_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return TeamContext(
            team_id=team_id,
            team_name=team_name or "",
            role=role,
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_coach(team_ctx: TeamContext = Depends(get_current_team)) -> TeamContext:
    """Require coach or head_coach role"""
    if team_ctx.role not in ["coach", "head_coach"]:
        raise HTTPException(status_code=403, detail="Coach access required")
    return team_ctx


def require_head_coach(team_ctx: TeamContext = Depends(get_current_team)) -> TeamContext:
    """Require head_coach role"""
    if team_ctx.role != "head_coach":
        raise HTTPException(status_code=403, detail="Head coach access required")
    return team_ctx
