from typing import Any

import httpx

from business_object.vehicle_type import VehicleType

from .feed_ingestion_strategy import FeedIngestionStrategy


class VehicleTypeStrategy(FeedIngestionStrategy[VehicleType]):
    """Ingest vehicle type feeds."""

    def __init__(
        self,
        dao: VehicleTypeDAO,
        feed_name: str,
        url: str,
        interval_seconds: int,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, interval_seconds, http_client)
        self.dao = dao

    def parse_payload(self, raw_data: Any) -> list[VehicleType]:
        """Parse vehicle type payloads."""
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                vehicle_types = data.get("vehicle_types", [])
                return [
                    VehicleType.from_dict(vehicle_type)
                    for vehicle_type in vehicle_types
                ]
        return []

    async def persist(self, entities: list[VehicleType]) -> int:
        """Persist vehicle type entities."""
        raise NotImplementedError
