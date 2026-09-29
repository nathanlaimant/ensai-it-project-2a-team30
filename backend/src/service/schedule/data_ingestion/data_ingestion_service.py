from utils.http_client import HttpClient

from .feed_ingestion_strategy import FeedIngestionStrategy


class DataIngestionService:
    """Execute feed ingestion strategies."""

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def execute_strategy(self, strategy: FeedIngestionStrategy) -> int:
        """Execute one feed strategy."""
        raise NotImplementedError
