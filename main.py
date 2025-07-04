# %%
# INIT
import pprint
import warnings

from utils.db import db_get_seen_connections, db_add_connections, db_get_connection_with_empty_contact_info, \
    db_update_connection
from utils.linkedin import login_to_linkedin, go_to_connections
from utils.linkedin.connections import create_connections_list, extend_connection, extend_connections_list

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



# ================================================================================
# ================================================================================


# %%
# POBIERANIE ZAPISANYCH KONTAKTÓW
# pobranie kontaktów z bazy danych, aby uniknąć duplikatów
seen_connections = db_get_seen_connections()


# %%
# PRZEJŚCIE DO STRONY Z KONTAKTAMI
classes = {
    "CLASS_CONNECTION_BLOCK": "_69b58b81 f2865a00 _3521e13b _4cfc03f4 _8cce9d30 _5b608b13 _32ae0e52 ca6f144b "
                              "_44c1d05b fab8c9e8"
}
connections = go_to_connections(driver, classes)


## %%
# tworzymy listę do przechowywania informacji o kontaktach
classes = {
    "CLASS_CONNECTION_NAME": "_7587260e _096a665d",
    "CLASS_CONNECTION_OCCUPATION": "_6280f893 _4217524f _163b424c _1800f1ec _472fd2a9 cb744a73 _78e48e06 "
                                    "_71e41417 be1ccd22 _84db77a9 _57b56f73 af3a1c87 c14301b7 _190823b7",
    "CLASS_CONNECTION_CONNECTED": "_6280f893 _4217524f _71e41417 be1ccd22 _84db77a9 _57b56f73 af3a1c87 _8b457770 "
                                  "_190823b7"
}
connections_list = create_connections_list(connections, seen_connections, classes)


# %%
# PRZEJŚCIE DO PROFILI KONTAKTÓW I POBRANIE INFORMACJI KONTAKTOWYCH
classes = {
    "CLASS_LOCATION": "text-body-small inline t-black--light break-words",
    "CLASS_CONTACT_INFO_SECTION": "pv-contact-info__contact-type",
    "ID_LINK_CONTACT_INFO": "top-card-text-details-contact-info"
}
extend_connections_list(driver, connections_list, classes)


# %%
# ——— ZAPIS DO BAZY POSTGRES ———
db_add_connections(connections_list)


# ================================================================================
# ================================================================================
# %%
connection = db_get_connection_with_empty_contact_info()
extended_connection = extend_connection(driver, connection)
pprint.pprint(extended_connection)

# ZAPIS DO BAZY POSTGRES
# Jeśli extended_connection zawiera informacje kontaktowe, aktualizujemy rekord w bazie danych
if extended_connection["contact_info"]:
    updated_count = db_update_connection(
        profile_url=extended_connection["profile_url"],
        contact_info=extended_connection["contact_info"],
        location=extended_connection["location"]
    )
    print(f"Zaktualizowano {updated_count} rekordów w bazie danych.")

    if updated_count == 0:
        print("Uwaga: nie zaktualizowano żadnych rekordów. Sprawdź, czy profil URL jest poprawny i czy rekord istnieje w bazie danych.")
