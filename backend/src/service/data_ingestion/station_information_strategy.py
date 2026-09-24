from ..business_object import StationInformation
from ..dao import StationDAO
from .feed_ingestion_strategy import FeedIngestionStrategy


class StationInformationStrategy(FeedIngestionStrategy[StationInformation]):
    """Ingest station information feeds."""

    def __init__(
        self, dao: StationDAO, feed_name: str, interval_seconds: int, url: str
    ):
        super().__init__(feed_name, interval_seconds, url)
        self.dao = dao

    def parse_payload(self, headers: dict, raw_data: dict) -> list[StationInformation]:
        """Parse station information payloads."""
        raise NotImplementedError

    def persist(self, entities: list[StationInformation]) -> int:
        """Persist station information entities."""
        raise NotImplementedError
