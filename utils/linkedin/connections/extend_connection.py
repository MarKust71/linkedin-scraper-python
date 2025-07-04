from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import wait
from contact_utils import parse_contact_info_sections


def extend_connection(driver, connection, classes, classes_contact_info):
    """ Extend a single connection with additional information from LinkedIn profile.
    :param driver: Selenium WebDriver instance
    :param connection: Dictionary containing connection information
    :param classes: Dictionary containing class names for elements
    :return: Updated connection dictionary with additional information
    """
    CLASS_LOCATION, CLASS_CONTACT_INFO_SECTION = (
        classes["CLASS_LOCATION"],
        classes["CLASS_CONTACT_INFO_SECTION"]
    )

    profile_url = connection["profile_url"]
    full_name = connection["full_name"]

    wait()
    driver.get(profile_url)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    location = soup.find("span", class_=CLASS_LOCATION).text.strip() \
        if soup.find("span", class_=CLASS_LOCATION) else None
    connection["location"] = location

    link_contact_info = driver.find_element(By.XPATH, "//a[@id='top-card-text-details-contact-info']")
    # klika w link do kontaktów
    wait()
    link_contact_info.click()

    # czekamy na załadowanie wszystkich sekcji
    print("Czekam na załadowanie wszystkich sekcji kontaktów...")
    try:
        web_elements = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, CLASS_CONTACT_INFO_SECTION))
        )
        print(f"Znaleziono {len(web_elements)} elementów z klasą '{CLASS_CONTACT_INFO_SECTION}'.")

    except Exception as e:
        print("!!! Nie udało się załadować sekcji kontaktów lub wystąpił błąd:", e)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    contact_info_sections = soup.find_all("section", class_=CLASS_CONTACT_INFO_SECTION)

    contact_info_dict = parse_contact_info_sections(
        contact_info_sections,
        full_name,
        classes=classes_contact_info
    )
    connection["contact_info"] = contact_info_dict

    return connection
