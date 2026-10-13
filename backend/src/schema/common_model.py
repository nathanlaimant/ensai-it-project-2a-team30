"""Common request and response models exposed by the API."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Confirmation returned after a state-changing operation."""

    message: str
