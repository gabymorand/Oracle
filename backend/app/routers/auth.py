from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from jose import jwt

from app.config import settings
from app.schemas.auth import AuthRequest, AuthResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/validate-code", response_model=AuthResponse)
async def validate_code(request: AuthRequest):
    if request.code != settings.access_code:
        raise HTTPException(status_code=401, detail="Invalid access code")

    if request.role not in ["coach", "player", "head_coach"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Generate JWT token
    expiration = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    payload = {"role": request.role, "exp": expiration}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return AuthResponse(access_token=token, role=request.role)
