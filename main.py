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

    connection_dict['full_name'] = full_name
    connection_dict['first_name'] = first_name
    connection_dict['last_name'] = last_name
    connection_dict['profile_url'] = profile_url
    connection_dict['occupation'] = occupation
    connection_dict['connected_on'] = connected_on
    connection_dict['profile_photo'] = dict(src=profile_photo_src, alt=profile_photo_alt)

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
try:
    button_load_more = driver.find_element(By.XPATH, "//button[@class='c9f1aa60 _6defb001 _6b3820bb _70f3535c _0734b5bd f1d72004 _9e7f7493 dc268ea9 _2f964dfd befb15ce _5b782f55 _584ac2dd']")
    button_load_more.click()
except Exception as e:
    pass
