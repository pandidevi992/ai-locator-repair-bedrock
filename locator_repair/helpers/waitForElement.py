from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )