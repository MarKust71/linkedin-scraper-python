import pprint


from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from contact_utils import parse_contact_info_sections
from utils import wait


def extend_connections_list(driver, connections_list):
    for connection in connections_list:
        profile_url = connection["profile_url"]
        full_name = connection["full_name"]
        # tworzy nową kartę
        wait()
        driver.switch_to.new_window("tab")
        # ładuje URL w tej karcie
        driver.get(profile_url)

        link_contact_info = driver.find_element(By.XPATH, "//a[@id='top-card-text-details-contact-info']")
        # klika w link do kontaktów
        wait()
        link_contact_info.click()

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        contact_info_sections = soup.find_all("section", class_="pv-contact-info__contact-type")

        contact_info_dict = parse_contact_info_sections(contact_info_sections, full_name)
        connection["contact_info"] = contact_info_dict

        # zamknij zakładkę
        wait()
        driver.close()
        # wróć na pierwszą kartę:
        driver.switch_to.window(driver.window_handles[0])

    print("****************************")
    pprint.pprint(connections_list)
    print(f"Zebrano informacje o {len(connections_list)} kontaktach.")

    wait()

    return connections_list
