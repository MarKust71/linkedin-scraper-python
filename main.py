# %%
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os, pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from time import sleep

from dotenv import load_dotenv
load_dotenv(override=True)

from typing import List, Tuple, Dict, Any
def parse_contact_info_sections(contact_info_sections: List) -> Tuple[Dict[str, Any], List[str]]:
    """
    Parsuje listę sekcji kontaktowych i zwraca:
      - contact_info: słownik z kluczami 'profile', 'phone', 'email', 'address', 'connected_on'
      - unhandled: lista nagłówków, których nie obsłużyliśmy
    """
    # mapowanie nagłówka -> (klucz w wyniku, funkcja ekstrakcji wartości)
    extractors = {
        "Profile":   ("profile",     lambda sec: sec.find("a").text.strip()),
        "Phone":     ("phone",       lambda sec: sec.find(
            "span", class_="t-14 t-black t-normal").text.strip().split("\n")),
        "Website":   ("website",      lambda sec: sec.find(
            "a", class_="pv-contact-info__contact-link link-without-visited-state")["href"].strip()),
        "Email":     ("email",       lambda sec: sec.find("a").text.strip()),
        "Address":   ("address",     lambda sec: sec.find("a").text.strip()),
        "Connected": ("connected_on",lambda sec: sec.find("span").text.strip()),
    }

    contact_info: Dict[str, Any] = {}
    unhandled: List[str] = []

    for section in contact_info_sections:
        header = section.find("h3").text.strip()
        if header in extractors:
            key, extractor = extractors[header]
            try:
                value = extractor(section)
            except Exception as e:
                # w razie błędu ekstrakcji, zachowaj pustą wartość
                value = ""
                print(f"Warning: nie udało się wyciągnąć '{header}': {e}")
            contact_info[key] = value
            pprint.pprint(f"{key}: {value}")
        else:
            unhandled.append(header)

    pprint.pprint(f"Contact info: {contact_info}")
    pprint.pprint(f"Unhandled sections: {unhandled}")
    return contact_info, unhandled

# --- Przykład użycia ---
# contact_info_dict, leftover = parse_contact_info_sections(contact_info_sections)

driver = webdriver.Chrome()

# %%
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
            member_profile_block = driver.find_element(By.XPATH, "//div[@class='error-for-password']")
            raise SystemExit
        except Exception as e:
            pass

driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")

# %%
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")

page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
connections = soup.find_all("div", class_="_023b52d4 c8178b77 debf13c3 _16eb4e30 d2ea9f58 _5de01902 be803eea befb15ce _8e4257fb _47345da6")
number_of_connections = len(connections)

print("****************************")
print(f"{number_of_connections} connections found.")

connections_list = []
for connection in connections:
    connection_dict = {}

    name = connection.find("a", class_="_70f3535c _5c6933d6").text.strip()
    profile_url = connection.find("a", class_="_70f3535c _5c6933d6")["href"]
    occupation = connection.find("p", class_="_45a369a4 _6c195815 _49d9b2aa _849fd8c5 _5e09317b _6b659a00 a48e68ea _067d51df _4e504a32 f7d05a6d _0734b5bd d2b1b593 d52a30d7 _002999fd").text.strip()
    connected_on = connection.find("p", class_="_45a369a4 _6c195815 _067d51df _4e504a32 f7d05a6d _0734b5bd d2b1b593 _2ddeb6fe _002999fd").text.strip().replace("connected on ", "")

    connection_dict['name'] = name
    connection_dict['profile_url'] = profile_url
    connection_dict['occupation'] = occupation
    connection_dict['connected_on'] = connected_on

    connections_list.append(connection_dict.copy())

print(f"Connections:")
pprint.pprint(connections_list)
print("****************************")

# %%
for connection in connections_list:
# connection = connections_list[0]
    profile_url = connection["profile_url"]
    # tworzy nową kartę
    driver.switch_to.new_window("tab")
    # ładuje URL w tej karcie
    driver.get(profile_url)

    # ########
    link_contact_info = driver.find_element(By.XPATH, "//a[@id='top-card-text-details-contact-info']")
    # kliknij w link do kontaktów
    link_contact_info.click()

    sleep(2)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    contact_info_sections = soup.find_all("section", class_="pv-contact-info__contact-type")

    contact_info_dict, leftover = parse_contact_info_sections(contact_info_sections)
    connection["contact_info"] = contact_info_dict

    # zamknij zakładkę
    driver.close()
    # wróć na pierwszą kartę:
    driver.switch_to.window(driver.window_handles[0])

print("****************************")
print(f"Connections:")
pprint.pprint(connections_list)
print("****************************")

# %%
try:
    button_load_more = driver.find_element(By.XPATH, "//button[@class='c9f1aa60 _6defb001 _6b3820bb _70f3535c _0734b5bd f1d72004 _9e7f7493 dc268ea9 _2f964dfd befb15ce _5b782f55 _584ac2dd']")
    button_load_more.click()
except Exception as e:
    pass
