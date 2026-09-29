from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from .settings import Settings


class DbConnection:
    """
    Gère un pool de connexions à la base de données PostgreSQL.
 
    Parameters
    ----------
    settings : Settings
        Configuration contenant les paramètres de connexion à la base
        de données (hôte, port, nom de la base, utilisateur, mot de
        passe, schéma).
    """
    def __init__(self, settings: Settings):
        self._connection_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_database,
            user=settings.postgres_user,
            password=settings.postgres_password,
            options=f"-c search_path={settings.postgres_schema}",
            cursor_factory=RealDictCursor,
        )

    @contextmanager
    def get_connection(self):
        """
        Fournit une connexion issue du pool, sous forme de context manager.
 
        La connexion est automatiquement remise dans le pool à la sortie
        du bloc `with`, qu'une exception soit levée ou non.
 
        Yields
        ------
        connection
            Connexion à la base de données prête à l'emploi.
        """
        conn = self._connection_pool.getconn()
        try:
            yield conn
        finally:
            self._connection_pool.putconn(conn)

    def close(self):
        """
        Ferme toutes les connexions du pool.
 
        Returns
        -------
        None
        """
        self._connection_pool.closeall()
