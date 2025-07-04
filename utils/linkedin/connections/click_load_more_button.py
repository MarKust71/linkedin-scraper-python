from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.wait import WebDriverWait

CLASS_BUTTON_LOAD_MORE = ("_65f106a7 d9081127 fbba024a d2075618 d04644ed c48a48b2 dee56120 d9dc1def _5a2214ac "
                          "_22150fc8 _31c9ed19 b2684152")

def click_load_more_button(driver):
    """
    Kliknij przycisk 'Load more' na stronie z kontaktami.
    """
    classes = CLASS_BUTTON_LOAD_MORE.split()
    css = "button." + ".".join(classes)

    # czekamy na załadowanie przycisku 'Load more'
    print("Czekam na załadowanie przycisku 'Load more'...")
    try:
        web_elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
        )
        print(f"Znaleziono {len(web_elements)} elementów z klasą CLASS_BUTTON_LOAD_MORE.")

        try:
            button_load_more = driver.find_element(By.XPATH, f"//button[@class='{CLASS_BUTTON_LOAD_MORE}']")
            button_load_more.click()
            print("Kliknięto przycisk 'Load more'.")
        except Exception as e:
            print("Nie znaleziono przycisku 'Load more' lub wystąpił błąd:", e)

    except Exception as e:
        print("!!! Nie udało się załadować elementów z klasą CLASS_BUTTON_LOAD_MORE. Sprawdź klasy CSS.")
        exit()
