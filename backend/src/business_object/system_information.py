from datetime import date

from pydantic import BaseModel


class SystemInformation(BaseModel):
    """Describe the system."""

    system_id: str
    language: str
    name: str
    url: str
    start_date: date
    phone_number: str
    email: str
    timezone: str
