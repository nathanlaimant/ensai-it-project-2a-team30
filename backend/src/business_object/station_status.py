from datetime import datetime

from pydantic import BaseModel


class StationStatus(BaseModel):
    """
    Décrit l'état dynamique et actuel d'une station.
 
    Parameters
    ----------
    station_status_id : int
        Identifiant unique de l'enregistrement de statut.
    station_id : str
        Identifiant de la station concernée.
    num_bikes_available : int
        Nombre de vélos actuellement disponibles à la location.
    num_bikes_disabled : int
        Nombre de vélos présents mais hors service.
    num_docks_available : int
        Nombre de bornes actuellement libres.
    num_docks_disabled : int
        Nombre de bornes hors service.
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
    vehicle_types_available : list
        Liste du nombre de véhicules disponibles par type de véhicule.
    vehicle_docks_available : list
        Liste du nombre de bornes disponibles par type de véhicule.
    station_state : str
        État global de la station (ex: "active", "maintenance", "closed").
 
    Returns
    -------
    StationStatus
        Instance représentant l'état de la station.
    """

    station_status_id: int
    station_id: str
    num_bikes_available: int
    num_bikes_disabled: int
    num_docks_available: int
    num_docks_disabled: int
    operational_capacity: int
    is_installed: bool
    is_renting: bool
    is_returning: bool
    last_reported: datetime
    vehicle_types_available: list
    vehicle_docks_available: list
    station_state: str
