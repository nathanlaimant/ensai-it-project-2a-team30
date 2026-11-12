from psycopg2.extras import Json

from business_object.station_information import StationInformation
from utils.db_connection import DbConnection
from utils.log_utils import get_logger

logger = get_logger(__name__)


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
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, params)
                        res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            return False

        if res:
            station.station_id = res["station_id"] if isinstance(res, dict) else res[0]
            return True
        return False

    def get_by_id(self, station_id: str) -> StationInformation | None:
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
        query = """
            SELECT *
            FROM station_information
            WHERE 2 * 6371200 * ASIN(
                LEAST(
                    1.0,
                    SQRT(
                        GREATEST(
                            0.0,
                            POWER(SIN(%(t)s * (lat - %(lat_dep)s) / 2), 2)
                            + COS(lat * %(t)s)
                            * COS(%(lat_dep)s * %(t)s)
                            * POWER(SIN(%(t)s * (lon - %(lon_dep)s) / 2), 2)
                        )
                    )
                )
            ) <= %(radius_meters)s;
        """

        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        query,
                        {
                            "lat_dep": lat,
                            "lon_dep": lon,
                            "radius_meters": radius_meters,
                            "t": t,
                        },
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        stations_list = None
        if res:
            stations_list = []
            for i in range(len(res)):
                stations_list.append(
                    StationInformation(
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
                )
        return stations_list

    def list_stations(
        self,
        station_id: str | None = None,
        name: str | None = None,
        short_name: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        address: str | None = None,
        is_virtual_station: bool | None = None,
        contact_phone: str | None = None,
        capacity: int | None = None,
        min_capacity: int | None = None,
        max_capacity: int | None = None,
        is_charging_station: bool | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[StationInformation]:
        """
        Liste les stations selon des critères de recherche.
        Tous les arguments de la méthode sont optionnels.

        Parameters
        ----------
        station_id: str | None = None
            Identifiant de stations
        name: str | None = None
            Nom de station
        short_name: str | None = None
            Nom raccourci de station
        lat: float | None = None
            Latitude de station
        lon: float | None = None
            Longitude de station
        address: str | None = None
            Adresse de station
        is_virtual_station: bool | None = None
            Si True, lister les stations virtuelles
            Si False, lister les stations non virtuelles
        contact_phone: str | None = None
            Contact téléphonique de station
        capacity: int | None = None
            Capacité totale de la station
        min_capacity: int | None = None
            Capacité minimale de la station
        max_capacity: int | None = None
            Capacité maximale de la station
        is_charging_station: bool | None = None
            Si True, lister les stations avec bornes de charge
            Si False, ne pas lister les stations avec bornes de charge
        page: int = 1
            Numéro de la page de stations à créer
        size: int = 10
            Taille de la page de stations à créer

        Returns
        -------
        list of StationInformation
            Liste des stations correspondant aux critères.
            Renvoie une liste vide lorsqu'un des critères n'est pas dans le bon format.
        """
        res = None

        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * "
                        "FROM station_information "
                        "WHERE ((%(station_id)s IS NULL) OR (station_id ILIKE %(station_id)s)) "
                        "AND ((%(name)s IS NULL) OR (name ILIKE %(name)s)) "
                        "AND ((%(short_name)s IS NULL) OR (short_name ILIKE %(short_name)s)) "
                        "AND ((%(lat)s IS NULL) OR (lat = %(lat)s)) "
                        "AND ((%(lon)s IS NULL) OR (lon = %(lon)s)) "
                        "AND ((%(address)s IS NULL) OR (address ILIKE %(address)s)) "
                        "AND ((%(is_virtual_station)s IS NULL) OR (is_virtual_station = %(is_virtual_station)s)) "
                        "AND ((%(contact_phone)s IS NULL) OR (contact_phone ILIKE %(contact_phone)s)) "
                        "AND ((%(capacity)s IS NULL) OR (capacity = %(capacity)s)) "
                        "AND ((%(min_capacity)s IS NULL) OR (capacity >= %(min_capacity)s)) "
                        "AND ((%(max_capacity)s IS NULL) OR (capacity <= %(max_capacity)s)) "
                        "AND ((%(is_charging_station)s IS NULL) OR (is_charging_station = %(is_charging_station)s)) "
                        "ORDER BY station_id LIMIT %(size)s OFFSET %(offset)s;",
                        {
                            "station_id": (
                                "%" + station_id + "%" if station_id else None
                            ),
                            "name": "%" + name + "%" if name else None,
                            "short_name": (
                                "%" + short_name + "%" if short_name else None
                            ),
                            "lat": lat,
                            "lon": lon,
                            "address": "%" + address + "%" if address else None,
                            "is_virtual_station": is_virtual_station,
                            "contact_phone": (
                                "%" + contact_phone + "%" if contact_phone else None
                            ),
                            "capacity": capacity,
                            "min_capacity": min_capacity,
                            "max_capacity": max_capacity,
                            "is_charging_station": is_charging_station,
                            "size": size,
                            "offset": (page - 1) * size,
                        },
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        stations_list = []
        if res:
            for i in range(len(res)):
                stations_list.append(
                    StationInformation(
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
                )
        return stations_list
