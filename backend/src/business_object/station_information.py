from pydantic import BaseModel


class StationInformation(BaseModel):
    """
    Décrit les informations fixes d'une station.
    
    Parameters
    ----------
    station_id : str
        Identifiant unique de la station.
    name : str
        Nom complet et public de la station.
    short_name : str
        Nom court de la station.
    lat : float
        Latitude GPS de la station (entre -90 et 90).
    lon : float
        Longitude GPS de la station (entre -180 et 180).
    address : str
        Adresse postale de la station.
    is_virtual_station : bool
        True si la station est une zone virtuelle (sans bornes physiques).
    station_area : dict
        Géométrie (GeoJSON) de la zone couverte par la station.
    contact_phone : str
        Numéro de téléphone de contact associé à la station.
    capacity : int
        Capacité totale de la station (doit être > 0).
    is_charging_station : bool
        True si la station propose des emplacements de recharge électrique.
 
    Returns
    -------
    StationInformation
        Instance validée représentant la station.
    """

    station_id: str
    name: str
    short_name: str
    lat: float
    lon: float
    address: str
    is_virtual_station: bool
    station_area: dict
    contact_phone: str
    capacity: int
    is_charging_station: bool
