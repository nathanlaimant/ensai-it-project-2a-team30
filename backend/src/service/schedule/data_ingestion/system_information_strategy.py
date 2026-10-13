from typing import Any

import httpx

from business_object.system_information import SystemInformation
from dao.system_information_dao import SystemInformationDAO

from .feed_ingestion_strategy import BaseIngestionStrategy


class SystemInformationStrategy(BaseIngestionStrategy[SystemInformation]):
    """Ingest system information feeds."""

    def __init__(
        self,
        dao: SystemInformationDAO,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, http_client)
        self.dao = dao

    def parse_payload(self, raw_data: Any) -> list[SystemInformation]:
        """Parse system information payload."""
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                return [SystemInformation.from_dict(data)]
        return []

    async def persist(self, entities: list[SystemInformation]) -> int:
        """Persist system information entities."""
        raise NotImplementedError
