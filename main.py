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

# os.environ["EMAIL"], os.environ["PASSWORD"]

driver = webdriver.Chrome()

# %%
driver.get("https://www.linkedin.com/login/pl")

if driver.current_url == "https://www.linkedin.com/login/pl":
    try:
        member_profile_block = driver.find_element(By.XPATH, "//div[@class='member-profile-block']")
        member_profile_block.click()
        # driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")
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

connections = soup.find_all("div", class_="b76b9936 _0851ab0a _3e3fee64 dcc34198 c9d1147d _600179e5 f0cc5b9e _3b4ac106 d5b92317 _20e28694")
number_of_connections = len(connections)
print(f"{number_of_connections} connections found.")

connections_list = []
for connection in connections:
    connection_dict = {}

    name = connection.find("p", class_="_0541da3d _2d70cf55 a70fc434 _07e8f447 f7bf264b _14d9d282 a693b3b8 c53b5656 _66ce3f32 _03c05728").text.strip()
    profile_link = connection.find("a", class_="fb862af6 _17d1b836")["href"]
    occupation = connection.find("p", class_="_0541da3d _0794129a bc279ba5 ee91b557 _8938a15c _35fc986b _8827c7f1 _07e8f447 f7bf264b d2350752 a693b3b8 c53b5656 _66ce3f32 _03c05728").text.strip()
    connected_on = connection.find("p", class_="_0541da3d _0794129a _07e8f447 f7bf264b d2350752 a693b3b8 c53b5656 _43f09794 _03c05728").text.strip().replace("connected on ", "")

    connection_dict['name'] = name
    connection_dict['profile_link'] = profile_link
    connection_dict['occupation'] = occupation
    connection_dict['connected_on'] = connected_on

    connections_list.append(connection_dict.copy())

print(f"Connections:")
pprint.pprint(connections_list)

button_load_more = driver.find_element(By.XPATH, "//button[@class='_8d0bd381 _6421bf17 _4e62e86f fb862af6 a693b3b8 _730644b3 _55bb4f0b _634316b1 _5d8fda3e _3b4ac106 _67a67a26 b7342f7c']")
button_load_more.click()

