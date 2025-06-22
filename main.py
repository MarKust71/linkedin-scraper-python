# %%
# INIT
import warnings

from utils.db import db_get_seen_connections, db_add_connections
from utils.linkedin import login_to_linkedin, go_to_connections
from utils.linkedin.connections import create_connections_list, extend_connections_list

warnings.filterwarnings("ignore", category=FutureWarning)

from selenium import webdriver

from dotenv import load_dotenv
load_dotenv(override=True)

driver = webdriver.Chrome()


# %%
# LOGOWANIE DO LINKEDIN
if login_to_linkedin(driver):
    print("Zalogowano do LinkedIn.")
else:
    print("Logowanie do LinkedIn nie powiodło się.")


# %%
# POBIERANIE ZAPISANYCH KONTAKTÓW
# pobranie kontaktów z bazy danych, aby uniknąć duplikatów
seen_connections = db_get_seen_connections()


# %%
# PRZEJŚCIE DO STRONY Z KONTAKTAMI
connections = go_to_connections(driver)


## %%
# tworzymy listę do przechowywania informacji o kontaktach
connections_list = create_connections_list(connections, seen_connections)


# %%
# PRZEJŚCIE DO PROFILI KONTAKTÓW I POBRANIE INFORMACJI KONTAKTOWYCH
extend_connections_list(driver, connections_list)


## %%
# ——— ZAPIS DO BAZY POSTGRES ———
db_add_connections(connections_list)
