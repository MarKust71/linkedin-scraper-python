# %%
# INIT
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os, pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

from dotenv import load_dotenv
load_dotenv(override=True)

from contact_utils import parse_contact_info_sections
from name_utils    import split_name

import psycopg2
from psycopg2.extras import Json
from datetime import datetime

# parametrów połączenia nie trzeba wczytywać ponownie, .env jest już załadowane :contentReference[oaicite:1]{index=1}
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", 5432)
DB_NAME     = os.getenv("DB_NAME", "linkedin_scraper")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def click_load_more_button(driver):
    """
    Kliknij przycisk 'Load more' na stronie z kontaktami.
    """
    CLASS_BUTTON_LOAD_MORE = ("_65f106a7 d9081127 fbba024a d2075618 d04644ed c48a48b2 dee56120 d9dc1def _5a2214ac "
                              "_22150fc8 _31c9ed19 b2684152")
    classes = CLASS_BUTTON_LOAD_MORE.split()
    css = "button." + ".".join(classes)

    # czekamy na załadowanie przycisku 'Load more'
    print("Czekam na załadowanie przycisku 'Load more'...")
    try:
        web_elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
        )
        print(f"Znaleziono {len(web_elements)} elementów z klasą CLASS_BUTTON_LOAD_MORE.")

        try:
            button_load_more = driver.find_element(By.XPATH, f"//button[@class='{CLASS_BUTTON_LOAD_MORE}']")
            button_load_more.click()
            print("Kliknięto przycisk 'Load more'.")
        except Exception as e:
            print("Nie znaleziono przycisku 'Load more' lub wystąpił błąd:", e)

    except Exception as e:
        print("!!! Nie udało się załadować elementów z klasą CLASS_CONNECTION_BLOCK. Sprawdź klasy CSS.")
        exit()

driver = webdriver.Chrome()

# %%
# LOGIN
driver.get("https://www.linkedin.com/login/pl")

if driver.current_url == "https://www.linkedin.com/login/pl":
    try:
        member_profile_block = driver.find_element(By.XPATH, "//div[@class='member-profile-block']")
        member_profile_block.click()
    except Exception as e:
        email_input = driver.find_element(By.ID, "username")
        email_input.send_keys(os.environ["EMAIL"])

        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(os.environ["PASSWORD"])

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        try:
            sleep(3)
            element = driver.find_element(By.ID, "captcha-internal")
            print("Please complete the exercise to continue.")

        except Exception as e:
            pass

print("Login successful.")


# %%
# PRZEJŚCIE DO STRONY Z KONTAKTAMI

# TODO: sprawdzenie, czy jesteśmy zalogowani, ew. przekierowanie do logowania
try:
    driver.find_element(By.ID, "global-nav")
    # idziemy dalej
except Exception as e:
    # nie idziemy dalej
    pass

# przejście do strony z kontaktami
print("przejście do strony z kontaktami")
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")

# #     # klikamy przycisk 'Load more'
# click_load_more_button(driver)
# #     # klikamy przycisk 'Load more'
# click_load_more_button(driver)
# #     # klikamy przycisk 'Load more'
# click_load_more_button(driver)
# #     # klikamy przycisk 'Load more'
# click_load_more_button(driver)
# #     # klikamy przycisk 'Load more'
# click_load_more_button(driver)

# czekamy na załadowanie elementów z klasą CLASS_CONNECTION_BLOCK - zdjęć profilowych
print("Czekam na załadowanie elementów z klasą CLASS_CONNECTION_BLOCK - zdjęć profilowych...")
CLASS_CONNECTION_BLOCK = ("_396fac21 _6339973d dfb572da _8d7fbe02 _218d89ab _2ab12687 _0bbcb5e1 _22150fc8 f130b3fb "
                          "_4a832557")
classes = CLASS_CONNECTION_BLOCK.split()
css = "div." + ".".join(classes) + " img"
try:
    web_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
    )
    print(f"Znaleziono {len(web_elements)} elementów z klasą CLASS_CONNECTION_BLOCK - zdjęcie profilowe.")
except Exception as e:
    print("!!! Nie udało się załadować elementów z klasą CLASS_CONNECTION_BLOCK - zdjęcie profilowe. Sprawdź klasy CSS.")
    # driver.quit()
    # exit()

# pobranie źródła strony i sparsowanie BeautifulSoup
print("Pobieram źródło strony i parsuję BeautifulSoup...")
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
connections = soup.find_all("div", class_=CLASS_CONNECTION_BLOCK)
number_of_connections = len(connections)

print("****************************")
print(f"{number_of_connections} connections found on page.")

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
seen_profiles = {row[0] for row in cur.fetchall() if row[0]}
## zamknięcie połączenia
cur.close()
conn.close()
print("koniec odczytu z bazy Postgres.")
# ——— KONIEC ODCZYTU ———


# %%
# tworzymy listę do przechowywania informacji o kontaktach
print("tworzenie listy do przechowywania informacji o kontaktach...")
CLASS_CONNECTION_NAME = "d2075618 _8ba1fc3a"
CLASS_CONNECTION_OCCUPATION = ("c3135742 e4709ff1 b15431b0 _99465215 _2b2c6cff fcbad3a4 _0620198f _92decd7d bf1f8d3e "
                               "_88268f11 d04644ed _28b6abf7 _8a814f8c aad4e596")
CLASS_CONNECTION_CONNECTED = "c3135742 e4709ff1 _92decd7d bf1f8d3e _88268f11 d04644ed _28b6abf7 _184b7550 aad4e596"

connections_list = []
for connection in connections:
    connection_dict = {}

    try:
        full_name = connection.find("a", class_=CLASS_CONNECTION_NAME).text.strip()
        first_name, last_name = split_name(full_name)

        profile_url = connection.find("a", class_=CLASS_CONNECTION_NAME)["href"]
    except Exception as e:
        print("!!! Błąd podczas pobierania imienia i nazwiska lub URL profilu:", e)
        full_name = None
        first_name, last_name = None, None
        profile_url = None

    try:
        occupation = connection.find("p", class_=CLASS_CONNECTION_OCCUPATION).text.strip()
    except Exception as e:
        print("!!! Błąd podczas pobierania zawodu:", e)
        occupation = None

    try:
        connected_on = (connection.find("p", class_=CLASS_CONNECTION_CONNECTED)
                        .text
                        .strip()
                        .replace("connected on ", ""))
    except Exception as e:
        print("!!! Błąd podczas pobierania daty połączenia:", e)
        connected_on = None

    try:
        profile_photo_src = connection.find("img")["src"]
        profile_photo_alt = connection.find("img")["alt"]
    except Exception as e:
        print(f"!!! {full_name} - Błąd podczas pobierania zdjęcia profilowego lub imienia i nazwiska:", e)
        profile_photo_src = None
        profile_photo_alt = None

    connection_dict.update({
        "full_name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "profile_url": profile_url,
        "occupation": occupation,
        "connected_on": connected_on,
        "profile_photo": {"src": profile_photo_src, "alt": profile_photo_alt},
    })

    if profile_url not in seen_profiles:
        connections_list.append(connection_dict.copy())

print("****************************")
print(f"{len(connections_list)} connections to process.")



# %%
# PRZEJŚCIE DO PROFILI KONTAKTÓW I POBRANIE INFORMACJI KONTAKTOWYCH
for connection in connections_list:
    profile_url = connection["profile_url"]
    full_name = connection["full_name"]
    # tworzy nową kartę
    driver.switch_to.new_window("tab")
    # ładuje URL w tej karcie
    driver.get(profile_url)

    link_contact_info = driver.find_element(By.XPATH, "//a[@id='top-card-text-details-contact-info']")
    # klika w link do kontaktów
    link_contact_info.click()

    sleep(2)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    contact_info_sections = soup.find_all("section", class_="pv-contact-info__contact-type")

    contact_info_dict = parse_contact_info_sections(contact_info_sections, full_name)
    connection["contact_info"] = contact_info_dict

    # zamknij zakładkę
    driver.close()
    # wróć na pierwszą kartę:
    driver.switch_to.window(driver.window_handles[0])

print("****************************")
pprint.pprint(connections_list)
print(f"Zebrano informacje o {len(connections_list)} kontaktach.")


# %%
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
