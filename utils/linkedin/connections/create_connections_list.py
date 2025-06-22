from name_utils import split_name

CLASS_CONNECTION_NAME = "d2075618 _8ba1fc3a"
CLASS_CONNECTION_OCCUPATION = ("c3135742 e4709ff1 b15431b0 _99465215 _2b2c6cff fcbad3a4 _0620198f _92decd7d bf1f8d3e "
                               "_88268f11 d04644ed _28b6abf7 _8a814f8c aad4e596")
CLASS_CONNECTION_CONNECTED = "c3135742 e4709ff1 _92decd7d bf1f8d3e _88268f11 d04644ed _28b6abf7 _184b7550 aad4e596"

def create_connections_list(connections, seen_connections):
    print("tworzenie listy do przechowywania informacji o kontaktach...")

    connections_list = []
    for connection in connections:
        connection_dict = {}

        try:
            full_name = connection.find("a", class_=CLASS_CONNECTION_NAME).text.strip()
            first_name, last_name = split_name(full_name)

            profile_url = connection.find("a", class_=CLASS_CONNECTION_NAME)["href"]
        except Exception as e:
            print("!!! Błąd podczas pobierania imienia i nazwiska lub URL profilu:", e)
            full_name = None
            first_name, last_name = None, None
            profile_url = None

        if profile_url in seen_connections:
            continue

        try:
            occupation = connection.find("p", class_=CLASS_CONNECTION_OCCUPATION).text.strip()
        except Exception as e:
            print("!!! Błąd podczas pobierania zawodu:", e)
            occupation = None

        try:
            connected_on = (connection.find("p", class_=CLASS_CONNECTION_CONNECTED)
                            .text
                            .strip()
                            .replace("connected on ", ""))
        except Exception as e:
            print("!!! Błąd podczas pobierania daty połączenia:", e)
            connected_on = None

        try:
            profile_photo_src = connection.find("img")["src"]
            profile_photo_alt = connection.find("img")["alt"]
        except Exception as e:
            print(f"!!! {full_name} - Błąd podczas pobierania zdjęcia profilowego lub imienia i nazwiska:", e)
            profile_photo_src = None
            profile_photo_alt = None

        connection_dict.update({
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "profile_url": profile_url,
            "occupation": occupation,
            "connected_on": connected_on,
            "profile_photo": {"src": profile_photo_src, "alt": profile_photo_alt},
        })

        connections_list.append(connection_dict.copy())

    print("****************************")
    print(f"{len(connections_list)} connections to process.")

    return connections_list
