from ..business_object import StationStatus
from ..dao import StationStatusDAO
from .feed_ingestion_strategy import FeedIngestionStrategy


class StationStatusStrategy(FeedIngestionStrategy[StationStatus]):
    """Ingest station status feeds."""

    def __init__(
        self, dao: StationStatusDAO, feed_name: str, interval_seconds: int, url: str
    ):
        super().__init__(feed_name, interval_seconds, url)
        self.dao = dao

    def parse_payload(self, headers: dict, raw_data: dict) -> list[StationStatus]:
        """Parse station status payloads."""
        raise NotImplementedError

    def persist(self, entities: list[StationStatus]) -> int:
        """Persist station status entities."""
        raise NotImplementedError
