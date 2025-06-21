import os, psycopg2

# parametrów połączenia nie trzeba wczytywać ponownie, .env jest już załadowane :contentReference[oaicite:1]{index=1}
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", 5432)
DB_NAME     = os.getenv("DB_NAME", "linkedin_scraper")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def db_get_seen_connections():
    # ——— ODCZYT Z BAZY POSTGRES ———
    print("Odczyt z bazy Postgres...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    ## tworzymy tabelę (jeśli nie istnieje) z dodatkowymi polami na zdjęcie i kontakt_info
    cur.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                                                           id             SERIAL PRIMARY KEY,
                                                           full_name      TEXT,
                                                           first_name     TEXT,
                                                           last_name      TEXT,
                                                           profile_url    TEXT UNIQUE,
                                                           occupation     TEXT,
                                                           connected_on   DATE,
                                                           profile_photo  JSONB,
                                                           contact_info   JSONB
                );
                """)
    conn.commit()

    ## ——— Dodaj unikalny indeks na contact_info.profile ———
    cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS unique_contact_profile
                    ON connections (profile_url);
                """)
    conn.commit()

    cur.execute("SELECT profile_url FROM connections;")
    seen_connections = {row[0] for row in cur.fetchall() if row[0]}
    ## zamknięcie połączenia
    cur.close()
    conn.close()
    print("koniec odczytu z bazy Postgres.")
    # ——— KONIEC ODCZYTU ———

    print(f"Znaleziono {len(seen_connections)} już zapisanych połączeń.")

    return seen_connections
