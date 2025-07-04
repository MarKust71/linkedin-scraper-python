from pprint import pprint
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from contact_utils import parse_contact_info_sections
from utils import wait


def extend_connections_list(driver, connections_list, classes):
    """
    Extend the connection list with additional information from LinkedIn profiles.
    :param driver:
    :param connections_list:
    :param classes:
    :return:
    """
    CLASS_LOCATION, CLASS_CONTACT_INFO_SECTION, ID_LINK_CONTACT_INFO = (
        classes["CLASS_LOCATION"],
        classes["CLASS_CONTACT_INFO_SECTION"],
        classes["ID_LINK_CONTACT_INFO"],
    )

    for connection in connections_list:
        profile_url = connection["profile_url"]
        full_name = connection["full_name"]
        # tworzy nową kartę
        wait()
        driver.switch_to.new_window("tab")
        # ładuje URL w tej karcie
        driver.get(profile_url)

        wait()
        try:
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            # szuka elementu z lokalizacją
            location = soup.find("span", class_=CLASS_LOCATION).text.strip()
            connection["location"] = location
        except Exception as e:
            print("!!! Błąd podczas odczytywania 'location' lub błąd:", e)

        link_contact_info = driver.find_element(By.XPATH, f"//a[@id='{ID_LINK_CONTACT_INFO}']")
        # klika w link do kontaktów
        link_contact_info.click()

        wait()
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        contact_info_sections = soup.find_all("section", class_=CLASS_CONTACT_INFO_SECTION)

        contact_info_dict = parse_contact_info_sections(contact_info_sections, full_name)
        connection["contact_info"] = contact_info_dict

        # zamknij zakładkę
        wait()
        driver.close()
        # wróć na pierwszą kartę:
        wait()
        driver.switch_to.window(driver.window_handles[0])

    print("****************************")
    pprint(connections_list)
    print(f"Zebrano informacje o {len(connections_list)} kontaktach.")

    wait()

    return connections_list
