import os, psycopg2, pprint
from datetime import datetime

from psycopg2._json import Json

# parametrów połączenia nie trzeba wczytywać ponownie, .env jest już załadowane :contentReference[oaicite:1]{index=1}
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", 5432)
DB_NAME     = os.getenv("DB_NAME", "linkedin_scraper")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def db_add_connections(connections_list):
    # ——— ZAPIS DO BAZY POSTGRES ———
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    for c in connections_list:
        # parsowanie daty w formacie "March 10, 2022" lub innego (usuwa "connected on ")
        try:
            dt = datetime.strptime(c["connected_on"], "%B %d, %Y").date()
        except Exception:
            dt = None

        pprint.pprint(c)
        cur.execute("""
                    INSERT INTO connections
                    (full_name, first_name, last_name, profile_url,
                     occupation, connected_on, profile_photo, contact_info)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (profile_url) DO NOTHING;
                    """, (
                        c["full_name"],
                        c["first_name"],
                        c["last_name"],
                        c["profile_url"],
                        c["occupation"],
                        dt,
                        Json(c.get("profile_photo", {})),
                        Json(c.get("contact_info", {}))
                    ))
    conn.commit()

    # zamknięcie połączenia
    cur.close()
    conn.close()
    # ——— KONIEC ZAPISU ———
