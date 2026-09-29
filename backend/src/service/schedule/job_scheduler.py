from typing import Any


class JobScheduler:
    """Schedule recurring application jobs."""

    def add_job(self, func: Any, trigger: Any, seconds: int, args: Any):
        """Register a scheduled job."""
        raise NotImplementedError

    def start(self):
        """Start scheduled jobs."""
        raise NotImplementedError
