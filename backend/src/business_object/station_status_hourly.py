from datetime import datetime

from pydantic import BaseModel


class StationStatusHourly(BaseModel):
    """
    Décrit l'agrégation horaire des statistiques d'une station.
 
    Parameters
    ----------
    station_id : str
        Identifiant de la station concernée.
    bucket_hour : datetime
        Heure de début du créneau horaire agrégé.
    sample_count : int
        Nombre d'échantillons de statut ayant servi à l'agrégation.
    avg_operational_capacity : float
        Capacité opérationnelle moyenne sur le créneau horaire.
    avg_num_bikes_available : float
        Nombre moyen de vélos disponibles sur le créneau horaire.
    avg_num_docks_available : float
        Nombre moyen de bornes disponibles sur le créneau horaire.
    empty_duration_sec : int
        Durée totale (en secondes) où la station était vide sur le créneau.
    full_duration_sec : int
        Durée totale (en secondes) où la station était pleine sur le créneau.
    empty_events_cnt : int
        Nombre d'occurrences où la station est devenue vide.
    full_events_cnt : int
        Nombre d'occurrences où la station est devenue pleine.
    reliability_score : float
        Score de fiabilité de la station sur le créneau horaire.
 
    Returns
    -------
    StationStatusHourly
        Instance représentant l'agrégation horaire.
    """
    
    station_id: str
    bucket_hour: datetime
    sample_count: int
    avg_operational_capacity: float
    avg_num_bikes_available: float
    avg_num_docks_available: float
    empty_duration_sec: int
    full_duration_sec: int
    empty_events_cnt: int
    full_events_cnt: int
    reliability_score: float
