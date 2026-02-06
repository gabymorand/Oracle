from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.team import Team
from app.schemas.auth import AuthRequest, AuthResponse, TeamInfo

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/validate-code", response_model=AuthResponse)
async def validate_code(request: AuthRequest, db: Session = Depends(get_db)):
    # Look up team by access code
    team = db.query(Team).filter(Team.access_code == request.code).first()
    if not team:
        raise HTTPException(status_code=401, detail="Invalid access code")

    if request.role not in ["coach", "player", "head_coach"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Generate JWT token with team info
    expiration = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    payload = {
        "role": request.role,
        "team_id": team.id,
        "team_name": team.name,
        "exp": expiration,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return AuthResponse(
        access_token=token,
        role=request.role,
        team=TeamInfo(id=team.id, name=team.name),
    )
