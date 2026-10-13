from utils.db_connection import DbConnection


class VehicleTypeDAO:
    """Gère l'accès aux données des types de véhicules en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection
