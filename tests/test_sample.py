from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from locators.locators import SAMPLE_LOCATOR
from locator_repair.ai_locator_fix import ai_suggest_locator_fix
from locator_repair.locator_updater import update_locator_file, commit_and_push_changes
from locator_repair.github_pr import create_pull_request

def run_test_case():
    driver = webdriver.Chrome()
    driver.get("https://leafground.com/")

    try:
        driver.find_element(*SAMPLE_LOCATOR)
        print("✅ Locator works.")
    except NoSuchElementException:
        print(f"⚠️ Locator broken: {SAMPLE_LOCATOR}")
        new_locator = ai_suggest_locator_fix(SAMPLE_LOCATOR)
        update_locator_file(SAMPLE_LOCATOR, new_locator)
        commit_and_push_changes()
        create_pull_request()

    driver.quit()
