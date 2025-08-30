from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def send_whatsapp_message(contact_name, message):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://web.whatsapp.com")

    print("Scan QR if not logged in...")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
    )
    print("WhatsApp loaded.")

    # 🔹 Wait for search box to be clickable
    search_box = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
    )
    search_box.clear()
    search_box.send_keys(contact_name)
    time.sleep(2)

    # 🔹 Click first result
    chat = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//span[contains(@title, '{contact_name}')]"))
    )
    chat.click()
    time.sleep(2)

    # 🔹 Wait for message box
    msg_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
    )
    msg_box.send_keys(message)

    # 🔹 Click send button
    send_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))
    )
    send_btn.click()

    print("Message sent successfully!")
    time.sleep(5)
    driver.quit()


# Test
send_whatsapp_message("Rumi", "Hello rumi")
