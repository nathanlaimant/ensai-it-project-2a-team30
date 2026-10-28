"""Station-related request and response models exposed by the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from business_object.station_state import StationState


class StationSearchRequest(BaseModel):
    """
    Requête de recherche de stations selon des critères spécifiques.

    Parameters
    ----------
    name : str, optional
        Recherche les stations dont le nom contient cette chaîne de caractères.

    short_name : str, optional
        Recherche les stations dont le nom court contient cette chaîne de caractères.

    address : str, optional
        Recherche les stations dont l'adresse contient cette chaîne de caractères.

    min_capacity : int, optional
        Recherche les stations dont la capacité est supérieure ou égale à cette valeur.

    max_capacity : int, optional
        Recherche les stations dont la capacité est inférieure ou égale à cette valeur.

    page: int
        Numéro de page pour la pagination (1 par défaut)

    size: int
        Nombre d'éléments par page (10 par défaut, maximum 100)

    Returns
    -------
    StationSearchRequest
        Instance représentant les critères de recherche.
    """

    name: str | None = None
    short_name: str | None = None
    address: str | None = None
    min_capacity: int | None = None
    max_capacity: int | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)


class StationInfoResponse(BaseModel):
    """
    Réponse contenant les informations d'une station.

    Parameters
    ----------
    station_id : str
        Identifiant unique de la station.
    name : str
        Nom complet et public de la station.
    short_name : str | None
        Nom court de la station. Nullable.
    lat : float
        Latitude GPS de la station (entre -90 et 90).
    lon : float
        Longitude GPS de la station (entre -180 et 180).
    address : str | None
        Adresse postale de la station. Nullable.
    station_area : dict | None
        Géométrie (GeoJSON) de la zone couverte par la station. Nullable.
    contact_phone : str | None
        Numéro de téléphone de contact associé à la station. Nullable.
    capacity : int | None
        Capacité totale de la station. Nullable.

    Returns
    -------
    StationInfoResponse
        Instance représentant les informations d'une station.
    """

    model_config = ConfigDict(from_attributes=True)

    station_id: str
    name: str
    short_name: str | None = None
    lat: float
    lon: float
    address: str | None = None
    station_area: dict | None = None
    contact_phone: str | None = None
    capacity: int | None = None


class StationStatusResponse(BaseModel):
    """
    Réponse contenant les informations de statut d'une station.

    Parameters
    ----------
    num_bikes_available : int
        Nombre de vélos disponibles à la station.
    num_docks_available : int | None
        Nombre de bornes disponibles à la station. Nullable.
    last_reported : datetime
        Date et heure de la dernière mise à jour du statut.
    vehicle_types_available : dict[str, int] | None
        Répartition des vélos disponibles par type.
    vehicle_docks_available : dict[str, int] | None
        Répartition des bornes disponibles par type.
    station_state : StationState
        État actuel de la station.
    reliability_score : float | None
        Score de fiabilité le plus récent du statut de la station. None si non disponible.

    Returns
    -------
    StationStatusResponse
        Instance représentant le statut d'une station.
    """

    model_config = ConfigDict(from_attributes=True)

    num_bikes_available: int
    num_docks_available: int | None = None
    last_reported: datetime
    vehicle_types_available: dict[str, int] | None = None
    vehicle_docks_available: dict[str, int] | None = None
    station_state: StationState
    reliability_score: float | None = None
