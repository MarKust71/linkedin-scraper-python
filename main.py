# %%
# INIT
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os, pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

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

# %%
# PRZEJŚCIE DO STRONY Z KONTAKTAMI

# TODO: sprawdzenie, czy jesteśmy zalogowani, ew. przekierowanie do logowania
try:
    driver.find_element(By.ID, "global-nav")
    # idziemy dalej
except Exception as e:
    # nie idziemy dalej
    pass

driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")

CLASS_CONNECTION_BLOCK = ("_5e590a8c bb062603 _4af99c28 d880256b _9dc9853e f4ee1050 "
                          "_4efe9d11 fce0f231 _62ca92a5 dd602475")
CLASS_CONNECTION_NAME = "afaedf57 _6acc9de9"
CLASS_CONNECTION_OCCUPATION = ("c90e8693 _66e83a99 _3fdefac7 _242f944e _45d391f2 a5a15547 be3a6b7b _08dd3c9b "
                               "_0975679c _961dcb74 _695b6b97 _86d42c62 aa362e2d c82cd034")
CLASS_CONNECTION_CONNECTED = "c90e8693 _66e83a99 _08dd3c9b _0975679c _961dcb74 _695b6b97 _86d42c62 d93572b4 c82cd034"

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

classes = CLASS_CONNECTION_BLOCK.split()
css = "div." + ".".join(classes) + " img"
WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
)

page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
connections = soup.find_all("div", class_=CLASS_CONNECTION_BLOCK)
number_of_connections = len(connections)

print("****************************")
print(f"{number_of_connections} connections found.")

# ——— ODCZYT Z BAZY POSTGRES ———
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# tworzymy tabelę (jeśli nie istnieje) z dodatkowymi polami na zdjęcie i kontakt_info
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

# ——— Dodaj unikalny indeks na contact_info.profile ———
cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_contact_profile
--                ON connections ((contact_info->>'profile'));
                ON connections (profile_url);
            """)
conn.commit()

# cur.execute("SELECT contact_info->>'profile' FROM connections;")
cur.execute("SELECT profile_url FROM connections;")
seen_profiles = {row[0] for row in cur.fetchall() if row[0]}
# zamknięcie połączenia
cur.close()
conn.close()
# ——— KONIEC ODCZYTU ———


connections_list = []
for connection in connections:
    connection_dict = {}

    full_name = connection.find("a", class_=CLASS_CONNECTION_NAME).text.strip()
    profile_url = connection.find("a", class_=CLASS_CONNECTION_NAME)["href"]
    occupation = connection.find("p", class_=CLASS_CONNECTION_OCCUPATION).text.strip()
    connected_on = (connection.find("p", class_=CLASS_CONNECTION_CONNECTED)
                    .text
                    .strip()
                    .replace("connected on ", ""))
    profile_photo_src = connection.find("img")["src"]
    profile_photo_alt = connection.find("img")["alt"]

    first_name, last_name = split_name(full_name)

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

# %%
# PRZEJŚCIE DO PROFILI KONTAKTÓW I POBRANIE INFORMACJI KONTAKTOWYCH
for connection in connections_list:
    profile_url = connection["profile_url"]
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

    contact_info_dict = parse_contact_info_sections(contact_info_sections)
    connection["contact_info"] = contact_info_dict

    # zamknij zakładkę
    driver.close()
    # wróć na pierwszą kartę:
    driver.switch_to.window(driver.window_handles[0])

print("****************************")
pprint.pprint(connections_list)


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


# %%
CLASS_BUTTON_LOAD_MORE = ("_8986dcdf _7711c173 _3cde6b8b afaedf57 _695b6b97 a71e3076 _4b8e13ff _556fc494 _224a1a2a "
                          "fce0f231 a368a5d7 _9fe01952")

try:
    button_load_more = driver.find_element(By.XPATH, f"//button[@class='{CLASS_BUTTON_LOAD_MORE}']")
    button_load_more.click()
except Exception as e:
    print("No more connections to load or button not found.")
    pass
