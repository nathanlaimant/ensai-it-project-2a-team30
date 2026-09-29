class StationInformation:
    """
    Décrit les informations fixes d'une station.

    Parameters
    ----------
    station_id : str | None
        Identifiant unique de la station. Non-nullable, mais peut être None si l'objet n'a pas été persistée.
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
    is_virtual_station : bool | None
        True si la station est une zone virtuelle (sans bornes physiques). Nullable.
    station_area : dict | None
        Géométrie (GeoJSON) de la zone couverte par la station. Nullable.
    contact_phone : str | None
        Numéro de téléphone de contact associé à la station. Nullable.
    capacity : int | None
        Capacité totale de la station (doit être > 0). Nullable.
    is_charging_station : bool | None
        True si la station propose des emplacements de recharge électrique. Nullable.
    """

    def __init__(
        self,
        name: str,
        short_name: str | None,
        lat: float,
        lon: float,
        address: str | None,
        is_virtual_station: bool | None,
        station_area: dict | None,
        contact_phone: str | None,
        capacity: int | None,
        is_charging_station: bool | None,
        station_id: str | None = None,
    ):
        self.station_id = station_id
        self.name = name
        self.short_name = short_name
        self.lat = lat
        self.lon = lon
        self.address = address
        self.is_virtual_station = is_virtual_station
        self.station_area = station_area
        self.contact_phone = contact_phone
        self.capacity = capacity
        self.is_charging_station = is_charging_station
