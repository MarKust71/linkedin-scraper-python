# This file is part of the LinkedIn Scraper project.
"""
# LinkedIn Scraper
"""
import os

from time import sleep

from selenium.webdriver.common.by import By

from utils import wait


def login_to_linkedin(driver) -> bool:
    """
    Login to LinkedIn using Selenium WebDriver.
    Args:
        driver: Selenium WebDriver instance.
    """

    LOGIN_PAGE_URL = "https://www.linkedin.com/login/pl"
    driver.get(LOGIN_PAGE_URL)

    if driver.current_url == LOGIN_PAGE_URL:
        try:
            member_profile_block = driver.find_element(By.XPATH, "//div[@class='member-profile-block']")
            member_profile_block.click()
        except Exception as e:
            email_input = driver.find_element(By.ID, "username")
            email_input.send_keys(os.environ["EMAIL"])

            password_input = driver.find_element(By.ID, "password")
            password_input.send_keys(os.environ["PASSWORD"])

            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            wait()
            login_button.click()

            try:
                sleep(3)
                element = driver.find_element(By.ID, "captcha-internal")
                print("Please complete the exercise to continue.")
                return False

            except Exception as e:
                pass

    # print("Login successful.")
    return True
