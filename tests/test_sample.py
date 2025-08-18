import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from locator_repair.config import LOCATOR_FILE_PATH
from locators.locators import USERNAME_LOCATOR, NEXT_LOCATOR, PASSWORD_LOCATOR, SUBMIT_LOCATOR
from locator_repair.ai_locator_fix import ai_suggest_locator_fix
from locator_repair.locator_updater import update_locator_by_variable, commit_and_push_changes
from locator_repair.github_pr import create_pull_request
from locator_repair.helpers.waitForElement import wait_for_element

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
            print(f"❌ Failed to use AI-suggested locator for {description}. Retrying....")
            print("Error:", str(e))
            try:
                new_locator = ai_suggest_locator_fix(
                old_locator=str(locator),
                driver=driver,
                description=description
            )
                print(f"🔁 New locator for {description} in the retry: {new_locator}")
                element = driver.find_element(*new_locator)
                if is_click:
                    element.click()
                else:
                    element.send_keys(value)
                print(f"✅ New locator for {description} works in the retry.")
            except Exception as e:
                print(f"❌ Failed to use AI-suggested locator for {description} in the retry.")
                print("Error:", str(e))
                with open("error_log.txt", "a") as f:
                    f.write(f"Broken locator: {locator}\nError: {str(e)}\n")
        return new_locator

def run_test_case():
    driver = webdriver.Chrome()
    driver.get("https://devint.emadev.emoneyadvisor.com/ema/UserManagement/Users")
    
    updated_locators = {}

    updated_locators["USERNAME_LOCATOR"] = validate_and_repair(
        driver, USERNAME_LOCATOR, "Username input box", value="test_adv"
    )
    updated_locators["NEXT_LOCATOR"] = validate_and_repair(
        driver, NEXT_LOCATOR, "Next button", is_click=True
    )
    
    #wait_for_element(driver, *PASSWORD_LOCATOR, timeout=20)  # Ensure the page is loaded before proceeding

    time.sleep(5)  # Wait for the next page to load
    updated_locators["PASSWORD_LOCATOR"] = validate_and_repair(
        driver, PASSWORD_LOCATOR, "Password input box", value="Password@123"
    )
    updated_locators["SUBMIT_LOCATOR"] = validate_and_repair(
        driver, SUBMIT_LOCATOR, "Submit button", is_click=True
    )
    #waitForPageLoad(driver, 10)  # Ensure page is loaded before proceeding

    driver.quit()

    # Update only if at least one locator was fixed
    if any(v for v in updated_locators.values()):
        for locator_name, new_locator in updated_locators.items():
            if new_locator:
                update_locator_by_variable(
                    locator_file_path=LOCATOR_FILE_PATH,
                    locator_name=locator_name,
                    new_locator=new_locator
                )
        commit_and_push_changes()
        create_pull_request()

