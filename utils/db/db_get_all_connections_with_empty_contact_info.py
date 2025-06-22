import os
import psycopg2

# Parametry połączenia (ładowane z .env)
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", 5432)
DB_NAME     = os.getenv("DB_NAME", "linkedin_scraper")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def db_get_all_connections_with_empty_contact_info():
    """
    Zwraca listę słowników z full_name i profile_url
    dla wszystkich rekordów, w których contact_info = pusty JSON ({}).
    """
    print("Odczyt z bazy Postgres: wszystkie wyniki z pustym contact_info...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    cur.execute("""
                SELECT full_name, profile_url
                FROM connections
                WHERE contact_info = '{}'::jsonb;
                """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = []
    for full_name, profile_url in rows:
        results.append({"full_name": full_name, "profile_url": profile_url})

    print(f"Znaleziono {len(results)} rekordów z pustym contact_info.")
    return results


if __name__ == "__main__":
    # Testowanie funkcji
    results = db_get_all_connections_with_empty_contact_info()
    if results:
        for result in results:
            print(f"Znaleziono rekord: {result}")
    else:
        print("Nie znaleziono żadnych rekordów z pustym contact_info.")
    # print("Koniec testowania.")
