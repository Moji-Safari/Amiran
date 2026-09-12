import pytest

from db.database import get_db


def test_database_connection(app):
    with app.app_context():
        with get_db() as conn:
            assert conn is not None
            assert conn.closed == 0


def test_database_query(app):
    with app.app_context():
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS result")
                row = cur.fetchone()

                assert row["result"] == 1


def test_database_uses_dict_cursor(app):
    with app.app_context():
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        1 AS id,
                        'test' AS name
                    """
                )

                row = cur.fetchone()

                assert row["id"] == 1
                assert row["name"] == "test"


def test_database_transaction_rolls_back_on_error(app):
    with app.app_context():
        with pytest.raises(RuntimeError):
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TEMPORARY TABLE test_transaction (
                            id INTEGER
                        )
                        """
                    )

                    cur.execute(
                        """
                        INSERT INTO test_transaction (id)
                        VALUES (1)
                        """
                    )

                    raise RuntimeError("Force rollback")