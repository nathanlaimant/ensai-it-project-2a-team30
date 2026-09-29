from datetime import datetime


class StationStatusHourly:
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
    """

    def __init__(
        self,
        station_id: str,
        bucket_hour: datetime,
        sample_count: int,
        avg_operational_capacity: float,
        avg_num_bikes_available: float,
        avg_num_docks_available: float,
        empty_duration_sec: int,
        full_duration_sec: int,
        empty_events_cnt: int,
        full_events_cnt: int,
        reliability_score: float,
    ):
        self.station_id = station_id
        self.bucket_hour = bucket_hour
        self.sample_count = sample_count
        self.avg_operational_capacity = avg_operational_capacity
        self.avg_num_bikes_available = avg_num_bikes_available
        self.avg_num_docks_available = avg_num_docks_available
        self.empty_duration_sec = empty_duration_sec
        self.full_duration_sec = full_duration_sec
        self.empty_events_cnt = empty_events_cnt
        self.full_events_cnt = full_events_cnt
        self.reliability_score = reliability_score
