from pydantic import BaseModel


class AuthRequest(BaseModel):
    code: str
    role: str  # coach, player, head_coach


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
