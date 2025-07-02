
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

    new_locator = None  # Ensure it's always defined

    try:
        driver.find_element(*SAMPLE_LOCATOR).send_keys("devi@gmail.com")
        print("✅ Locator works.")
    except NoSuchElementException:
        print(f"⚠️ Locator broken: {SAMPLE_LOCATOR}")

        try:
            new_locator = ai_suggest_locator_fix(
                old_locator=str(SAMPLE_LOCATOR),
                driver=driver,
                description="Email input box"
            )
            print(f"🔁 New locator: {new_locator}")
            driver.find_element(*new_locator).send_keys("devi@gmail.com")
            print("✅ New locator works.")
        except Exception as e:
            print("❌ Failed to use AI-suggested locator.")
            print("Error:", str(e))
            with open("error_log.txt", "w") as f:
                f.write(f"Broken locator: {SAMPLE_LOCATOR}\nError: {str(e)}\n")
    finally:
        driver.quit()

    # Optional: update file if fix worked
    if new_locator:
        update_locator_file(SAMPLE_LOCATOR, new_locator)
        commit_and_push_changes()
        create_pull_request()