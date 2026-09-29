from typing import Any

import httpx

from business_object.station_information import StationInformation
from dao import StationDAO

from .feed_ingestion_strategy import FeedIngestionStrategy


class StationInformationStrategy(FeedIngestionStrategy[StationInformation]):
    """Ingest station information feeds."""

    def __init__(
        self,
        dao: StationDAO,
        feed_name: str,
        url: str,
        interval_seconds: int,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, interval_seconds, http_client)
        self.dao = dao

    def parse_payload(self, raw_data: Any) -> list[StationInformation]:
        """Parse station information payloads."""
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                stations = data.get("stations", [])
                return [StationInformation.from_dict(station) for station in stations]
        return []

    async def persist(self, entities: list[StationInformation]) -> int:
        """Persist station information entities."""
        raise NotImplementedError
