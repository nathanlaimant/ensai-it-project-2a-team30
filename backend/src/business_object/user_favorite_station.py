from datetime import datetime

from pydantic import BaseModel


class UserFavoriteStation(BaseModel):
    """Describe a user's favorite station."""

    user_id: int
    station_id: str
    created_at: datetime
