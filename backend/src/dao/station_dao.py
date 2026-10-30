from psycopg2.extras import Json

from business_object.station_information import StationInformation
from utils.db_connection import DbConnection
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class StationDAO:
    """Gère l'accès aux données des informations de stations en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    @log
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
        if not station:
            return False

        query = """
            INSERT INTO station_information (
                station_id,
                name,
                short_name,
                lat,
                lon,
                address,
                is_virtual_station,
                station_area,
                contact_phone,
                capacity,
                is_charging_station
            ) VALUES (
                %(station_id)s,
                %(name)s,
                %(short_name)s,
                %(lat)s,
                %(lon)s,
                %(address)s,
                %(is_virtual_station)s,
                %(station_area)s,
                %(contact_phone)s,
                %(capacity)s,
                %(is_charging_station)s
            )
            ON CONFLICT (station_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                short_name = EXCLUDED.short_name,
                lat = EXCLUDED.lat,
                lon = EXCLUDED.lon,
                address = EXCLUDED.address,
                is_virtual_station = EXCLUDED.is_virtual_station,
                station_area = EXCLUDED.station_area,
                contact_phone = EXCLUDED.contact_phone,
                capacity = EXCLUDED.capacity,
                is_charging_station = EXCLUDED.is_charging_station
            RETURNING station_id;
        """

        params = {
            "station_id": station.station_id,
            "name": station.name,
            "short_name": station.short_name,
            "lat": station.lat,
            "lon": station.lon,
            "address": station.address,
            "is_virtual_station": station.is_virtual_station,
            "station_area": (
                Json(station.station_area) if station.station_area else None
            ),
            "contact_phone": station.contact_phone,
            "capacity": station.capacity,
            "is_charging_station": station.is_charging_station,
        }

        res = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    res = cursor.fetchone()
                conn.commit()
        except Exception as e:
            logger.error(e)
            return False

        if res:
            station.station_id = res["station_id"] if isinstance(res, dict) else res[0]
            return True
        return False

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
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM station_information          "
                        " WHERE station_id = %(station_id)s; ",
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
                is_charging_station=res["is_charging_station"],
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
        res = None

        t = 0.01745329251994  # nombre de radian dans 1°

        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT *"
                        "FROM station_information"
                        "WHERE 2 * 6371200 * ASIN(SQRT(POWER(SIN(%(t)s * (lat - %(lat_dep)s) / 2), 2) + COS(lat * %(t)s) * COS(%(lat_dep)s * %(t)s) * POWER(SIN(%(t)s * (lon - %(lon_dep)s) / 2),2))) <= %(radius_meters)s;",
                        {
                            "lat_dep": lat,
                            "lon_dep": lon,
                            "radius_meters": radius_meters,
                            "t": t,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        stations_list = None
        if res:
            stations_list = []
            for i in range(len(res)):
                stations_list[i] = StationInformation(
                    station_id=res[i]["station_id"],
                    name=res[i]["name"],
                    short_name=res[i]["short_name"],
                    lat=res[i]["lat"],
                    lon=res[i]["lon"],
                    address=res[i]["address"],
                    is_virtual_station=res[i]["is_virtual_station"],
                    station_area=res[i]["station_area"],
                    contact_phone=res[i]["contact_phone"],
                    capacity=res[i]["capacity"],
                    is_charging_station=res[i]["is_charging_station"],
                )
        return stations_list

    def list_stations(
        self,
        station_id: str = None,
        name: str = None,
        short_name: str = None,
        lat: int = None,
        lon: int = None,
        address: str = None,
        is_virtual_station: bool = None,
        contact_phone: str = None,
        capacity: int = None,
        is_charging_station: bool = None,
        nb_pages: int = None,
    ) -> list[StationInformation]:
        """
        Liste les stations selon des critères de recherche.
        Tous les arguments de la méthode sont optionnels.

        Arguments
        ----------
        station_id: str = None
            Identifiant de stations
        name: str = None
            Nom de station
        short_name: str = None
            Nom raccourci de station
        lat: int = None
            Latitude de station
        lon: int = None
            Longitude de station
        address: str = None
            Adresse de station
        is_virtual_station: bool = None
            Si True, lister les stations virtuelles
            Si False, lister les stations non virtuelles
        contact_phone: str = None
            Contact téléphonique de station
        capacity: int = None
            Capacité totale de la station
        is_charging_station: bool = None
            Si True, lister les stations avec bornes de charge
            Si False, ne pas lister les stations avec bornes de charge
        nb_pages: int = None
            Nombre de pages de stations à créer

        Returns
        -------
        list of StationInformation
            Liste des stations correspondant aux critères.
            Ne renvoie rien lorsqu'un des critères n'est pas dans le bon format.
        """
        res = None

        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT *"
                        "FROM station_information"
                        "WHERE station_id ILIKE %%(station_id)s%"
                        "AND name ILIKE %%(name)s%"
                        "AND short_name ILIKE %%(short_name)s%"
                        "AND lat = %(lat)s"
                        "AND lon = %(lon)s"
                        "AND address ILIKE %%(address)s%"
                        "AND is_virtual_station = %(is_virtual_station)s"
                        "AND contact_phone ILIKE %%(contact_phone)s%"
                        "AND capacity = %(capacity)s"
                        "AND is_charging_station = %(is_charging_station)s",
                        {
                            "station_id": station_id,
                            "name": name,
                            "short_name": short_name,
                            "lat": lat,
                            "lon": lon,
                            "address": address,
                            "is_virtual_station": is_virtual_station,
                            "contact_phone": contact_phone,
                            "capacity": capacity,
                            "is_charging_station": is_charging_station,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        stations_list = None
        if res:
            stations_list = []
            for i in range(len(res)):
                stations_list[i] = StationInformation(
                    station_id=res[i]["station_id"],
                    name=res[i]["name"],
                    short_name=res[i]["short_name"],
                    lat=res[i]["lat"],
                    lon=res[i]["lon"],
                    address=res[i]["address"],
                    is_virtual_station=res[i]["is_virtual_station"],
                    station_area=res[i]["station_area"],
                    contact_phone=res[i]["contact_phone"],
                    capacity=res[i]["capacity"],
                    is_charging_station=res[i]["is_charging_station"],
                )
            if isinstance(nb_pages, int) and nb_pages > 1:
                sous_liste = []
                for k in range(nb_pages):
                    sous_liste[k] = stations_list[k * nb_pages : (k + 1) * nb_pages - 1]
                stations_list = sous_liste
        return stations_list
