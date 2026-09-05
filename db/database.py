from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from flask import g
from psycopg2 import pool

_pool: pool.ThreadedConnectionPool | None = None


def init_pool(app):
    global _pool
    _pool = pool.ThreadedConnectionPool(
        minconn=app.config["DB_POOL_MIN"],
        maxconn=app.config["DB_POOL_MAX"],
        dsn=app.config["DATABASE_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def get_conn():
    if "db_conn" not in g:
        g.db_conn = _pool.getconn()
        g.db_conn.autocommit = False
    return g.db_conn


def release_conn(e=None):
    conn = g.pop("db_conn", None)
    if conn is not None:
        # commit/rollback is handled exclusively by get_db(); here we only
        # return the connection to the pool to avoid a double-commit.
        _pool.putconn(conn)


@contextmanager
def get_db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
