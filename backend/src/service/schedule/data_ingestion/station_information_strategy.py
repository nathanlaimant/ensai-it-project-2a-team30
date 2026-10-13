from typing import Any

import httpx

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO

from .feed_ingestion_strategy import BaseIngestionStrategy


class StationInformationStrategy(BaseIngestionStrategy[StationInformation]):
    """Ingest station information feeds."""

    def __init__(
        self,
        dao: StationDAO,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, http_client)
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
