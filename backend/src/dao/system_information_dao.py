from business_object.system_information import SystemInformation
from utils.db_connection import DbConnection
from utils.log_utils import get_logger

logger = get_logger(__name__)


class SystemInformationDAO:
    """Gère l'accès aux données des informations de système en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def upsert_system_info(self, system_info: SystemInformation) -> bool:
        """
        Crée ou met à jour les informations du système.

        Parameters
        ----------
        system_info : SystemInformation
            Informations système à créer ou mettre à jour.

        Returns
        -------
        bool
            True si l'opération a réussi.
        """
        if not system_info:
            return False

        query = """
            INSERT INTO system_information (
                system_id,
                language,
                name,
                url,
                start_date,
                phone_number,
                email,
                timezone
            ) VALUES (
                %(system_id)s,
                %(language)s,
                %(name)s,
                %(url)s,
                %(start_date)s,
                %(phone_number)s,
                %(email)s,
                %(timezone)s
            )
            ON CONFLICT (system_id)
            DO UPDATE SET
                language = EXCLUDED.language,
                name = EXCLUDED.name,
                url = EXCLUDED.url,
                start_date = EXCLUDED.start_date,
                phone_number = EXCLUDED.phone_number,
                email = EXCLUDED.email,
                timezone = EXCLUDED.timezone
            RETURNING system_id;
        """

        params = {
            "system_id": system_info.system_id,
            "language": system_info.language,
            "name": system_info.name,
            "url": system_info.url,
            "start_date": system_info.start_date,
            "phone_number": system_info.phone_number,
            "email": system_info.email,
            "timezone": system_info.timezone,
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

        return isinstance(res, dict)
