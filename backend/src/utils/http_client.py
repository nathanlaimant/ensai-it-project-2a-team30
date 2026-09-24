"""HTTP client abstraction used by feed ingestion."""


class HttpClient:
    """Represent the application's HTTP client dependency."""

    def get(self, url: str) -> dict:
        """Fetch a JSON payload from a URL."""
        raise NotImplementedError
