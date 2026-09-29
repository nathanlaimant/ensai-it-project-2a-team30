from datetime import datetime


class StationStatus:
    """
    Décrit l'état dynamique et actuel d'une station.

    Parameters
    ----------
    station_status_id : int | None
        Identifiant unique de l'enregistrement de statut. Non-nullable, mais peut être None si l'objet n'a pas été persistée.
    station_id : str
        Identifiant de la station concernée.
    num_bikes_available : int
        Nombre de vélos actuellement disponibles à la location.
    num_bikes_disabled : int | None
        Nombre de vélos présents mais hors service. Nullable.
    num_docks_available : int | None
        Nombre de bornes actuellement libres. Nullable.
    num_docks_disabled : int | None
        Nombre de bornes hors service. Nullable.
    operational_capacity : int
        Capacité opérationnelle actuelle de la station.
    is_installed : bool
        True si la station est physiquement installée.
    is_renting : bool
        True si la station permet actuellement la location de véhicules.
    is_returning : bool
        True si la station permet actuellement le retour de véhicules.
    last_reported : datetime
        Date et heure du dernier rapport d'état reçu.
    vehicle_types_available : list | None
        Liste du nombre de véhicules disponibles par type de véhicule. Nullable.
    vehicle_docks_available : list | None
        Liste du nombre de bornes disponibles par type de véhicule. Nullable.
    station_state : str
        État global de la station (ex: "full", "functional", "empty").
    """

    def __init__(
        self,
        station_id: str,
        num_bikes_available: int,
        num_bikes_disabled: int | None,
        num_docks_available: int | None,
        num_docks_disabled: int | None,
        operational_capacity: int,
        is_installed: bool,
        is_renting: bool,
        is_returning: bool,
        last_reported: datetime,
        vehicle_types_available: list | None,
        vehicle_docks_available: list | None,
        station_state: str,
        station_status_id: int | None = None,
    ):
        self.station_status_id = station_status_id
        self.station_id = station_id
        self.num_bikes_available = num_bikes_available
        self.num_bikes_disabled = num_bikes_disabled
        self.num_docks_available = num_docks_available
        self.num_docks_disabled = num_docks_disabled
        self.operational_capacity = operational_capacity
        self.is_installed = is_installed
        self.is_renting = is_renting
        self.is_returning = is_returning
        self.last_reported = last_reported
        self.vehicle_types_available = vehicle_types_available
        self.vehicle_docks_available = vehicle_docks_available
        self.station_state = station_state
