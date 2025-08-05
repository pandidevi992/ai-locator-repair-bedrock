from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from locators.locators import EMAILBOX_LOCATOR, MESSAGES_LOCATOR, SEND_BUTTON_LOCATOR
from locator_repair.ai_locator_fix import ai_suggest_locator_fix
from locator_repair.locator_updater import update_locator_file, commit_and_push_changes
from locator_repair.github_pr import create_pull_request

def validate_and_repair(driver, locator, description, value=None, is_click=False):
    new_locator = None
    try:
        element = driver.find_element(*locator)
        if is_click:
            element.click()
        else:
            element.send_keys(value)
        print(f"✅ {description} locator works.")
    except NoSuchElementException:
        print(f"⚠️ {description} locator broken: {locator}")
        try:
            new_locator = ai_suggest_locator_fix(
                old_locator=str(locator),
                driver=driver,
                description=description
            )
            print(f"🔁 New locator for {description}: {new_locator}")
            element = driver.find_element(*new_locator)
            if is_click:
                element.click()
            else:
                element.send_keys(value)
            print(f"✅ New locator for {description} works.")
        except Exception as e:
            print(f"❌ Failed to use AI-suggested locator for {description}.")
            print("Error:", str(e))
            with open("error_log.txt", "a") as f:
                f.write(f"Broken locator: {locator}\nError: {str(e)}\n")
    return new_locator

def run_test_case():
    driver = webdriver.Chrome()
    driver.get("https://leafground.com/")
    
    updated_locators = {}

    updated_locators["EMAILBOX_LOCATOR"] = validate_and_repair(
        driver, EMAILBOX_LOCATOR, "Email input box", value="devi@gmail.com"
    )
    updated_locators["MESSAGES"] = validate_and_repair(
        driver, MESSAGES_LOCATOR, "Messages input box", value="Hi, How are you?"
    )
    updated_locators["SEND_BUTTON_LOCATOR"] = validate_and_repair(
        driver, SEND_BUTTON_LOCATOR, "Send button", is_click=True
    )

    driver.quit()

    # Update only if at least one locator was fixed
    if any(updated_locators.values()):
        for old_name, new_locator in updated_locators.items():
            if new_locator:
                update_locator_file(old_name, new_locator)
        commit_and_push_changes()
        create_pull_request()
