import re
import unicodedata
from datetime import UTC, datetime
from typing import Any

import httpx

from business_object.station_state import StationState
from business_object.station_status import StationStatus
from dao.station_status_dao import StationStatusDAO

from .feed_ingestion_strategy import BaseIngestionStrategy


class StationStatusStrategy(BaseIngestionStrategy[StationStatus]):
    """
    Ingère le flux de statuts en temps réel des stations.

    Parameters
    ----------
    dao : StationStatusDAO
        DAO permettant la persistance des statuts de stations.
    feed_name : str
        Nom du flux de données ingéré.
    url : str
        URL du flux de données à ingérer.
    http_client : httpx.AsyncClient
        Client HTTP asynchrone utilisé pour récupérer le flux.
    """

    def __init__(
        self,
        dao: StationStatusDAO,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, http_client)
        self.dao = dao

    @staticmethod
    def _classify_vehicle_type(type_id_or_name: Any) -> str:
        """
        Classifie un type de véhicule en 'electric' ou 'mechanical'.

        Prend en charge un large éventail de dénominations françaises, anglaises
        et internationales (vélos électriques, VAE, e-bikes, trottinettes,
        scooters, mopeds, modèles spécifiques Voi, Pony, Vélib, Lime, Tier, Dott, etc.).

        Parameters
        ----------
        type_id_or_name : Any
            L'identifiant ou le nom du type de véhicule à classer.

        Returns
        -------
        str
            "electric" si le type correspond à un véhicule électrique ou motorisé,
            sinon "mechanical".
        """
        if not type_id_or_name:
            return "mechanical"

        # Normalize and remove accents (e.g.: "électrique" -> "electrique", "mécanique" -> "mecanique")
        raw_str = str(type_id_or_name).strip().lower()
        normalized = unicodedata.normalize("NFKD", raw_str)
        name = "".join(c for c in normalized if not unicodedata.combining(c))

        # 1. Detect non-electric patterns (e.g., "non-electric", "non elec", "sans assistance", "unassisted", etc.)
        if re.search(
            r"(?:^|[^a-z0-9])(non[-_ ]?elec[a-z]*|not[-_ ]?elec[a-z]*|nonelec[a-z]*|sans[-_ ]?assistance|pas[-_ ]?elec[a-z]*|unassisted)(?:$|[^a-z0-9])",
            name,
        ):
            return "mechanical"

        # 2. Detect electric / motorized patterns
        if re.search(
            r"(?:^|[^a-z0-9])("
            r"elec[a-z]*|"  # electric, electrique, electrical, etc.
            r"e[-_]?(?:bikes?|velos?|bicycles?|cycles?|scooters?|trott?inettes?|"  # e-bike, e-scooter, e-trottinette, etc.
            r"mopeds?|cargos?|ponys?|rides?|rad|fahrrad)|"  # e-cargo, e-pony, etc.
            r"pedelecs?|epedelecs?|"  # pedelec
            r"vaes?|"  # VAE (Vélo à Assistance Électrique)
            r"boosters?|"  # booster (Vélib)
            r"scooters?|trott?inettes?|kickscooters?|mopeds?|"  # trottinettes, shared scooters
            r"patinettes?|patinetes?|monopattin[oi]|"  # other kinds of trottinettes
            r"batter(?:y|ies)|"  # battery powered
            r"motor[a-z]*|"  # motorized
            r"(?:power[-_ ]?)?assist[a-z]*|"  # Power assist, assisted
            r"voi[-_ ]?(?:scooter|bike|ebike)|"  # Voi specific fleet
            r"tier[-_ ]?(?:scooter|bike|ebike)|"  # Tier specific fleet
            r"dott[-_ ]?(?:scooter|bike|ebike)|"  # Dott specific fleet
            r"lime[-_ ]?(?:s|scooter|bike|ebike)"  # Lime specific fleet
            r")(?:$|[^a-z0-9])",
            name,
        ):
            return "electric"

        return "mechanical"

    @classmethod
    def _parse_vehicle_types(cls, raw_data: Any, default: int = 0) -> dict[str, int]:
        """
        Extrait et regroupe les types de véhicules disponibles en:
        {"mechanical": int, "electric": int}
        """
        counts = {"mechanical": 0, "electric": 0}

        if not raw_data:
            counts["mechanical"] = default
            return counts

        if isinstance(raw_data, list):
            for item in raw_data:
                if not isinstance(item, dict):
                    continue
                # 1. Standard format:
                # raw_data = [{"vehicle_type_id": "type_1", "count": 10}, {"vehicle_type_id": "type_2", "count": 10}]
                type_id = (
                    item.get("vehicle_type_id")
                    or item.get("vehicleTypeId")
                    or item.get("vehicle_type")
                )
                if type_id is not None or "count" in item:
                    try:
                        count = int(item.get("count", 0))
                    except (ValueError, TypeError):
                        count = 0
                    # "mechanical" if type_id is None
                    category = cls._classify_vehicle_type(type_id)
                    counts[category] += count
                else:
                    # 2. Vélib format:
                    # raw_data = [{"type_1": 10}, {"type_2": 10}]
                    for k, v in item.items():
                        try:
                            count = int(v)
                        except (ValueError, TypeError):
                            count = 0
                        category = cls._classify_vehicle_type(k)
                        counts[category] += count
        # 3. Alternative format: {"type_1": 10, "type_2": 10}
        elif isinstance(raw_data, dict):
            for k, v in raw_data.items():
                try:
                    count = int(v)
                except (ValueError, TypeError):
                    count = 0
                category = cls._classify_vehicle_type(k)
                counts[category] += count

        return counts

    @classmethod
    def _parse_vehicle_docks(
        cls, raw_data: Any, default: int | None = None
    ) -> dict[str, int]:
        """
        Extrait et regroupe les bornes disponibles par type en:
        {"mechanical": int, "electric": int}
        """
        counts = {"mechanical": 0, "electric": 0}

        if not raw_data:
            return {"mechanical": default or 0, "electric": default or 0}

        if isinstance(raw_data, list):
            for item in raw_data:
                if not isinstance(item, dict):
                    continue
                # 1. Standard format:
                # raw_data = [
                #   {"vehicle_type_ids": ["type_1", "type_2"], "count": 10},
                #   {"vehicle_type_ids": ["type_3", "type_4"], "count": 10}
                # ]
                try:
                    count = int(item.get("count", 0))
                except (ValueError, TypeError):
                    count = 0
                type_ids = item.get("vehicle_type_ids") or item.get("vehicleTypeIds")
                if isinstance(type_ids, list):
                    categories = {cls._classify_vehicle_type(tid) for tid in type_ids}
                    for cat in categories:
                        counts[cat] += count
                # 2. Vélib format:
                # raw_data = [{"type_1": 10}, {"type_2": 10}]
                else:
                    for k, v in item.items():
                        try:
                            val = int(v)
                        except (ValueError, TypeError):
                            val = 0
                        category = cls._classify_vehicle_type(k)
                        counts[category] += val
        # 3. Alternative format: {"type_1": 10, "type_2": 10}
        elif isinstance(raw_data, dict):
            for k, v in raw_data.items():
                try:
                    val = int(v)
                except (ValueError, TypeError):
                    val = 0
                category = cls._classify_vehicle_type(k)
                counts[category] += val

        return counts

    def from_json_dict(self, json_dict: dict) -> StationStatus:
        """
        Crée une instance de StationStatus à partir d'un dictionnaire JSON.

        Parameters
        ----------
        json_dict : dict
            Données de statut d'une station extraites du JSON.

        Returns
        -------
        StationStatus
            Instance représentant le statut de la station.
        """
        # 1. num_bikes_available
        num_bikes_available = json_dict.get("num_bikes_available")
        if num_bikes_available is None:
            num_bikes_available = json_dict.get("numBikesAvailable", 0)

        # 2. vehicle_types_available (GBFS: vehicle_types_available, Vélib: num_bikes_available_types, etc.)
        raw_vehicle_types = (
            json_dict.get("vehicle_types_available")
            or json_dict.get("vehicleTypesAvailable")
            or json_dict.get("num_bikes_available_types")
            or json_dict.get("numBikesAvailableTypes")
        )
        # 2.1. parse into 2 fixed types
        vehicle_types_available = StationStatusStrategy._parse_vehicle_types(
            raw_vehicle_types, int(num_bikes_available)
        )
        # 2.2. recompute num_bikes_available, using the sum of vehicle types
        if num_bikes_available is None or num_bikes_available == 0:
            calculated_count = (
                vehicle_types_available["mechanical"]
                + vehicle_types_available["electric"]
            )
            if calculated_count > 0 or num_bikes_available is None:
                num_bikes_available = calculated_count
        else:
            num_bikes_available = int(num_bikes_available)

        # 3. num_docks_available
        num_docks_available = json_dict.get("num_docks_available")
        if num_docks_available is None:
            num_docks_available = json_dict.get("numDocksAvailable")

        # temporary unused TODO
        vehicle_docks_available = None
        # 4. vehicle_docks_available (GBFS: vehicle_docks_available, etc.)
        # raw_vehicle_docks = (
        #     json_dict.get("vehicle_docks_available")
        #     or json_dict.get("vehicleDocksAvailable")
        #     or json_dict.get("num_docks_available_types")
        #     or json_dict.get("numDocksAvailableTypes")
        # )
        # 4.1. parse into 2 fixed types
        # vehicle_docks_available = StationStatusStrategy._parse_vehicle_docks(
        #     raw_vehicle_docks,
        #     default=(
        #         int(num_docks_available) if num_docks_available is not None else None
        #     ),
        # )
        # 4.2. recompute num_docks_available, using the sum of vehicle docks
        # if num_docks_available is None and raw_vehicle_docks:
        #     if isinstance(raw_vehicle_docks, list):
        #         num_docks_available = sum(
        #             int(item.get("count", 0))
        #             for item in raw_vehicle_docks
        #             if isinstance(item, dict) and "count" in item
        #         )
        # elif num_docks_available is not None:
        #     num_docks_available = int(num_docks_available)

        # 5. num_bikes_disabled
        num_bikes_disabled = json_dict.get("num_bikes_disabled")
        if num_bikes_disabled is None:
            num_bikes_disabled = json_dict.get("numBikesDisabled")

        # 6. num_docks_disabled
        num_docks_disabled = json_dict.get("num_docks_disabled")
        if num_docks_disabled is None:
            num_docks_disabled = json_dict.get("numDocksDisabled")

        # 7. compute operational_capacity
        operational_capacity = num_bikes_available + (num_docks_available or 0)

        # 8. classify station_state
        # some boolean flags
        # is_installed = json_dict.get("is_installed")
        is_renting = json_dict.get("is_renting")
        is_returning = json_dict.get("is_returning")
        if (num_docks_available is not None and num_docks_available == 0) or (
            is_returning is not None and not is_returning
        ):
            station_state = StationState.FULL
        elif num_bikes_available == 0 or (is_renting is not None and not is_renting):
            station_state = StationState.EMPTY
        else:
            station_state = StationState.FUNCTIONAL

        # 9. last_reported: int timestamp, MUST NOT be None
        last_reported = datetime.fromtimestamp(json_dict["last_reported"], tz=UTC)

        return StationStatus(
            station_id=str(json_dict["station_id"]),
            num_bikes_available=num_bikes_available,
            num_bikes_disabled=num_bikes_disabled,
            num_docks_available=num_docks_available,
            num_docks_disabled=num_docks_disabled,
            operational_capacity=int(operational_capacity),
            last_reported=last_reported,
            vehicle_types_available=vehicle_types_available,
            vehicle_docks_available=vehicle_docks_available,
            station_state=station_state,
        )

    def parse_payload(self, raw_data: Any) -> list[StationStatus]:
        """
        Transforme les données brutes du flux en entités StationStatus.

        Parameters
        ----------
        raw_data : Any
            Contenu brut du flux (format GBFS `station_status`).

        Returns
        -------
        list of StationStatus
            Liste des statuts de stations extraits du flux, ou une liste
            vide si le flux est vide ou mal formé.
        """
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                statuses = data.get("stations", [])
                return [
                    self.from_json_dict(station_status) for station_status in statuses
                ]
        return []

    async def persist(self, entities: list[StationStatus]) -> int:
        """
        Persiste une liste de statuts de stations en base de données.

        Parameters
        ----------
        entities : list of StationStatus
            Statuts de stations à persister.

        Returns
        -------
        int
            Nombre d'entités effectivement persistées.
        """
        if not entities:
            return 0

        return self.dao.bulk_insert_status(entities)
