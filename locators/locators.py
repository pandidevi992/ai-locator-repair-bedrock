from selenium.webdriver.common.by import By

# Deliberately broken locator to simulate failure
EMAILBOX_LOCATOR = (By.XPATH, "//input[@id='Email']")
MESSAGES_LOCATOR = (By.XPATH, "//textarea[@id='message']")
SEND_BUTTON_LOCATOR = (By.XPATH, "//span[contains(text(),'Send')]")
