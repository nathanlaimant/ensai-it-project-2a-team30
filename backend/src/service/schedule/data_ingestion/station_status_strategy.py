from typing import Any

import httpx

from business_object.station_status import StationStatus
from dao.station_status_dao import StationStatusDAO

from .feed_ingestion_strategy import FeedIngestionStrategy


class StationInformationStrategy(FeedIngestionStrategy[StationStatus]):
    """Ingest station information feeds."""

    def __init__(
        self,
        dao: StationStatusDAO,
        feed_name: str,
        url: str,
        interval_seconds: int,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, interval_seconds, http_client)
        self.dao = dao

    def parse_payload(self, raw_data: Any) -> list[StationStatus]:
        """Parse station status payloads."""
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                statuses = data.get("stations", [])
                return [
                    StationStatus.from_dict(station_status)
                    for station_status in statuses
                ]
        return []

    async def persist(self, entities: list[StationStatus]) -> int:
        """Persist station status entities."""
        raise NotImplementedError
