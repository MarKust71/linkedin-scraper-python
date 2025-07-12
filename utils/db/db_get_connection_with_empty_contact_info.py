import os
import psycopg2

# Parametry połączenia (ładowane z .env)
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", 5432)
DB_NAME     = os.getenv("DB_NAME", "linkedin_scraper")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def db_get_connection_with_empty_contact_info():
    """
    Zwraca full_name i profile_url pierwszego rekordu,
    w którym contact_info = pusty JSON ({}) lub contact_info.birthday = '', lub występuje contact_info.unhandled.
    Jeśli nie ma takiego rekordu, zwraca None.
    """
    print("Odczyt z bazy Postgres: pierwszy wynik z pustym contact_info...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    # contact_info jako jsonb równe pustemu JSON-owi
    cur.execute("""
                SELECT full_name, profile_url, contact_info, location
                FROM connections
                WHERE contact_info = '{}'::jsonb
                   OR contact_info::jsonb ->> 'birthday' = ''
                   OR (contact_info::jsonb ->> 'unhandled') IS NOT NULL
                LIMIT 1;
                """)
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        full_name, profile_url, contact_info, location = row
        print(f"Znaleziono: {full_name} — {profile_url}")
        return {"full_name": full_name, "profile_url": profile_url}
    else:
        print("Brak rekordów z pustym contact_info.")
        return None


if __name__ == "__main__":
    # Testowanie funkcji
    result = db_get_connection_with_empty_contact_info()
    if result:
        print(f"Znaleziono rekord: {result}")
    else:
        print("Nie znaleziono żadnych rekordów z pustym contact_info.")
    # Testowanie funkcji
    # print("Koniec testowania.")

