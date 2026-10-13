"""User-related request and response models exposed by the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoginResponse(BaseModel):
    """Session information returned after authentication."""

    user_id: int
    username: str
    access_token: str


class UserResponse(BaseModel):
    """Public user information. Authentication credentials and session tokens are not exposed."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int | None
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
