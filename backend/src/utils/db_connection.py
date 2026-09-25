from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from .settings import Settings


class DbConnection:
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
        conn = self._connection_pool.getconn()
        try:
            yield conn
        finally:
            self._connection_pool.putconn(conn)

    def close(self):
        self._connection_pool.closeall()
