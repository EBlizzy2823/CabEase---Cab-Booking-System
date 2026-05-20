# =============================================================
#  database/db_connection.py — MySQL connection & query helper
# =============================================================

import mysql.connector
from mysql.connector import Error
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_connection():
    """Opens and returns a fresh MySQL connection, or None on failure."""
    try:
        return mysql.connector.connect(
            host     = config.DB_HOST,
            user     = config.DB_USER,
            password = config.DB_PASSWORD,
            database = config.DB_NAME
        )
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None


def execute_query(query: str, params: tuple = (), fetch: bool = False):
    """
    Executes any SQL statement.

    Parameters
    ----------
    query  : SQL string with %s placeholders
    params : values to substitute
    fetch  : True → fetchall() (SELECT)
             False → commit + return lastrowid (INSERT/UPDATE/DELETE)

    Returns
    -------
    list[dict] | int | None
    """
    conn = get_connection()
    if conn is None:
        return None

    result = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
    except Error as e:
        print(f"[QUERY ERROR] {e}")
        if not fetch:
            conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return result


def test_connection() -> bool:
    conn = get_connection()
    if conn and conn.is_connected():
        print("✅  Connected to MySQL successfully!")
        conn.close()
        return True
    print("❌  Connection failed. Check config.py.")
    return False


if __name__ == "__main__":
    test_connection()
