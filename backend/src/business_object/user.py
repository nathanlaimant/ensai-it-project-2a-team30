from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    """Describe an user (account)."""

    user_id: int
    username: str
    password_hashed: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    access_token: str
