from business_object.station_information import StationInformation
from utils.db_connection import DbConnection


class StationDAO:
    """Gère l'accès aux données des informations de stations en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def upsert_station_info(self, station: StationInformation) -> bool:
        """
        Crée ou met à jour les informations d'une station.

        Parameters
        ----------
        station : StationInformation
            Informations de la station à créer ou mettre à jour.

        Returns
        -------
        bool
            True si l'opération a réussi.
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO station_information(station_id, name, short_name, lat, lon, address, is_virtual_station, station_area, contact_phone, capacity, is_charging_station) VALUES"
                        "(%(station_id)s, %(name)s, %(short_name)s, %(lat)s, %(lon)s, %(address)s, %(is_virtual_station)s, %(station_area)s, %(contact_phone)s, %(capacity)s, %(is_charging_station)s) "
                        "RETURNING station_id;",
                        {
                            "station_id": station.station_id,
                            "name": station.name,
                            "short_name": station.short_name,
                            "lat": station.lat,
                            "lon": station.lon,
                            "address": station.address,
                            "is_virtual_station": station.is_virtual_station,
                            "station_area": station.station_area,
                            "contact_phone": station.contact_phone,
                            "capacity": station.capacity,
                            "is_charging_station": station.is_charging_station
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            station.station_id = res["station_id"]
            created = True
        return created

    def get_by_id(self, station_id: str) -> StationInformation:
        """
        Récupère une station à partir de son identifiant.

        Parameters
        ----------
        station_id : str
            Identifiant de la station recherchée.

        Returns
        -------
        StationInformation
            Informations de la station correspondante, ou None si introuvable.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM station_information          "
                        " WHERE station_id = %(station_id)s;   ",
                        {"station_id": station_id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        station = None
        if res:
            station = StationInformation(
                station_id=res["station_id"],
                name=res["name"],
                short_name=res["short_name"],
                lat=res["lat"],
                lon=res["lon"],
                address=res["address"],
                is_virtual_station=res["is_virtual_station"],
                station_area=res["station_area"],
                contact_phone=res["contact_phone"],
                capacity=res["capacity"],
                is_charging_station=res["is_charging_station"]
            )
        return station

    def get_nearby(
        self, lat: float, lon: float, radius_meters: float
    ) -> list[StationInformation]:
        """
        Récupère les stations situées à proximité d'une position donnée.

        Parameters
        ----------
        lat : float
            Latitude du point de référence.
        lon : float
            Longitude du point de référence.
        radius_meters : float
            Rayon de recherche en mètres.

        Returns
        -------
        list of StationInformation
            Liste des stations situées dans le rayon demandé.
        """
        res = None # Use the Haversine formula

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute()
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        stations_list = None
        if res:
            stations_list = []
            for i in range(len(res)):
                stations_list[i] = StationInformation(
                    station_id=res["station_id"],
                    name=res["name"],
                    short_name=res["short_name"],
                    lat=res["lat"],
                    lon=res["lon"],
                    address=res["address"],
                    is_virtual_station=res["is_virtual_station"],
                    station_area=res["station_area"],
                    contact_phone=res["contact_phone"],
                    capacity=res["capacity"],
                    is_charging_station=res["is_charging_station"]
                )
        return stations_list

    def list_stations(self, query_params: dict) -> list[StationInformation]:
        """
        Liste les stations selon des critères de recherche.

        Parameters
        ----------
        query_params : dict
            Critères de filtrage et/ou de pagination.

        Returns
        -------
        list of StationInformation
            Liste des stations correspondant aux critères.
            Ne renvoie rien lorsqu'un des critères n'est pas dans le bon format.
        """
        raise NotImplementedError
