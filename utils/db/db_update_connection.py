# db_update_connection.py

import os
import psycopg2
import psycopg2.extras

# Parametry połączenia (ładowane z .env lub zmiennych środowiskowych)
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 5432))
DB_NAME     = os.getenv("DB_NAME", "linkedin_scraper")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def db_update_connection(profile_url: str, contact_info: dict, location: str) -> int:
    """
    Aktualizuje rekord w tabeli `connections` o danym profile_url,
    ustawiając pole contact_info na przekazany słownik (zamieniany na JSONB).

    :param profile_url: URL profilu, według którego filtrujemy rekord.
    :param contact_info: słownik z nowymi danymi contact_info.
    :return: liczba zaktualizowanych rekordów (0 lub 1).
    """
    # Serializujemy dict -> JSONB poprzez psycopg2.extras.Json
    json_value = psycopg2.extras.Json(contact_info)

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE connections
                    SET contact_info = %s, location = %s
                    WHERE profile_url = %s;
                    """,
                    (json_value, location, profile_url)
                )
                updated = cur.rowcount
        print(f"[db_update_connection] Zaktualizowano rekordów: {updated}")
        return updated

    finally:
        conn.close()
