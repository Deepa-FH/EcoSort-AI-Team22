"""MySQL connection pool and transaction boundary."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from mysql.connector import pooling
from mysql.connector.connection import MySQLConnection


class MySQLDatabase:
    def __init__(self, config: dict, pool_name: str = "ecosort_pool", pool_size: int = 5) -> None:
        self._config = config
        self._pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            autocommit=False,
        )

    @contextmanager
    def connection(self) -> Iterator[MySQLConnection]:
        connection = self._pool.get_connection()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def ping(self) -> bool:
        with self.connection() as connection:
            connection.ping(reconnect=True, attempts=1, delay=0)
        return True
