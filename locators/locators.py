from selenium.webdriver.common.by import By

# Deliberately broken locator to simulate failure
USERNAME_LOCATOR = (By.XPATH, "//input[@id='Username']")
NEXT_LOCATOR = (By.XPATH, "//button[@id='next-submit']")
PASSWORD_LOCATOR = (By.XPATH, "//input[@name='credentials.passcode']")
SUBMIT_LOCATOR = (By.XPATH, "//input[@type='submit' and @value='Login']")
