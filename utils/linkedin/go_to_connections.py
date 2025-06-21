import os

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# parametrów połączenia nie trzeba wczytywać ponownie, .env jest już załadowane :contentReference[oaicite:1]{index=1}
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", 5432)
DB_NAME     = os.getenv("DB_NAME", "linkedin_scraper")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

CLASS_CONNECTION_BLOCK = ("_396fac21 _6339973d dfb572da _8d7fbe02 _218d89ab _2ab12687 _0bbcb5e1 _22150fc8 f130b3fb "
                          "_4a832557")

def go_to_connections(driver):
    # TODO: sprawdzenie, czy jesteśmy zalogowani, ew. przekierowanie do logowania
    try:
        driver.find_element(By.ID, "global-nav")
        # idziemy dalej
    except Exception as e:
        # nie idziemy dalej
        pass

    # przejście do strony z kontaktami
    if not driver.current_url.startswith("https://www.linkedin.com/mynetwork/invite-connect/connections"):
        print("Nie jesteśmy na stronie z kontaktami, przechodzimy tam...")
        driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")

    # #     # klikamy przycisk 'Load more'
    # click_load_more_button(driver)
    # sleep(1)
    # #     # klikamy przycisk 'Load more'
    # click_load_more_button(driver)
    # sleep(1)
    # #     # klikamy przycisk 'Load more'
    # click_load_more_button(driver)
    # sleep(1)
    # #     # klikamy przycisk 'Load more'
    # click_load_more_button(driver)
    # sleep(1)
    # #     # klikamy przycisk 'Load more'
    # click_load_more_button(driver)
    # sleep(1)

    # czekamy na załadowanie elementów z klasą CLASS_CONNECTION_BLOCK - zdjęć profilowych
    print("Czekam na załadowanie elementów z klasą CLASS_CONNECTION_BLOCK - zdjęć profilowych...")
    classes = CLASS_CONNECTION_BLOCK.split()
    css = "div." + ".".join(classes) + " img"
    try:
        web_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
        )
        print(f"Znaleziono {len(web_elements)} elementów z klasą CLASS_CONNECTION_BLOCK - zdjęcie profilowe.")
    except Exception as e:
        print("!!! Nie udało się załadować elementów z klasą CLASS_CONNECTION_BLOCK - zdjęcie profilowe. Sprawdź klasy CSS.")

    # pobranie źródła strony i sparsowanie BeautifulSoup
    print("Pobieram źródło strony i parsuję BeautifulSoup...")
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    connections = soup.find_all("div", class_=CLASS_CONNECTION_BLOCK)
    number_of_connections = len(connections)

    print("****************************")
    print(f"{number_of_connections} connections found on page.")

    return connections
