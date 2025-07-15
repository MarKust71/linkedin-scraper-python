# %%
# INIT
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from selenium import webdriver
driver = webdriver.Chrome()

from dotenv import load_dotenv
load_dotenv(override=True)


# %%
# LOGOWANIE DO LINKEDIN
from utils.linkedin import login_to_linkedin, go_to_connections
from utils.linkedin.connections import create_connections_list, extend_connection, extend_connections_list

if login_to_linkedin(driver):
    print("Zalogowano do LinkedIn.")
else:
    print("Logowanie do LinkedIn nie powiodło się.")



# ================================================================================
# ================================================================================


# %%
# POBIERANIE ZAPISANYCH KONTAKTÓW
# pobranie kontaktów z bazy danych, aby uniknąć duplikatów
from utils.db import db_get_seen_connections, db_add_connections, db_get_connection_with_empty_contact_info, \
    db_update_connection

seen_connections = db_get_seen_connections()


# %%
# PRZEJŚCIE DO STRONY Z KONTAKTAMI
classes = {
    "CLASS_CONNECTION_BLOCK": "_6df3b7c2 _91fe83fe _0a79f01b _59a6ea63 f93e5492 _67fc2051 _83b7f5b6 _0a654781 "
                              "_78bfd5e6 a51d95de"
}
connections = go_to_connections(driver, classes)


## %%
# tworzymy listę do przechowywania informacji o kontaktach
classes = {
    "CLASS_CONNECTION_NAME": "df72ad54 cd1d52c1",
    "CLASS_CONNECTION_OCCUPATION": "_5afcfec1 _5018d784 _21eebf2f b40789c1 cea183d6 a02ddb28 _529ba546 _08f6ef57 "
                                   "_25253058 eac83152 e4a85902 _76097c90 b1f89b43 c7dbebbf",
    "CLASS_CONNECTION_CONNECTED": "_5afcfec1 _5018d784 _08f6ef57 _25253058 eac83152 e4a85902 _76097c90 _8a5f468c "
                                  "c7dbebbf"
}
connections_list = create_connections_list(connections, seen_connections, classes)


# %%
classes_contact_info = {
    "CLASS_CONTACT_INFO_BIRTHDAY": "wPCmWMUAafwDSWNLlrZvkXAYgnYzmGBJE t-14 t-black t-normal",
    "CLASS_CONTACT_INFO_WEBSITE": "pv-contact-info__contact-link link-without-visited-state",
    "CLASS_CONTACT_INFO_PHONE": "t-14 t-black t-normal",
    "CLASS_CONTACT_INFO_IM": "XRpFiHajaNzYjdCILtAPWTVclloyI t-14"
}


# %%
# PRZEJŚCIE DO PROFILI KONTAKTÓW I POBRANIE INFORMACJI KONTAKTOWYCH
classes = {
    "CLASS_LOCATION": "text-body-small inline t-black--light break-words",
    "CLASS_CONTACT_INFO_SECTION": "pv-contact-info__contact-type",
    "ID_LINK_CONTACT_INFO": "top-card-text-details-contact-info"
}
extend_connections_list(driver, connections_list, classes, classes_contact_info)


# %%
# ——— ZAPIS DO BAZY POSTGRES ———
db_add_connections(connections_list)


# ================================================================================
# ================================================================================
# %%
connection = db_get_connection_with_empty_contact_info()

classes = {
    "CLASS_LOCATION": "text-body-small inline t-black--light break-words",
    "CLASS_CONTACT_INFO_SECTION": "pv-contact-info__contact-type",
}
extended_connection = extend_connection(driver, connection, classes, classes_contact_info)

from pprint import pprint
pprint(extended_connection)

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
