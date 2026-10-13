from utils.db_connection import DbConnection


class SystemInformationDAO:
    """Gère l'accès aux données des informations de système en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection
