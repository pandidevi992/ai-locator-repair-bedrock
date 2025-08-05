import re
from locator_repair.config import LOCATOR_FILE_PATH, REPO_PATH, BRANCH_NAME
from git import Repo

def update_locator_by_variable(locator_file_path, locator_name, new_locator):
    """
    Updates the given locator variable in the locator file with the new locator.

    Args:
        locator_file_path (str): Path to the Python locator file.
        locator_name (str): Variable name of the locator (e.g., 'EMAILBOX_LOCATOR').
        new_locator (tuple): New locator tuple, e.g., ('xpath', '//input[@id="email"]')
    """

    strategy, selector = new_locator
    strategy = strategy.upper()  # Convert 'xpath' to 'XPATH'

    updated_line = f"{locator_name} = (By.{strategy}, \"{selector}\")\n"

    pattern = re.compile(rf"^{locator_name}\s*=\s*\(By\.\w+,\s*['\"].*?['\"]\)")

    updated = False
    with open(locator_file_path, 'r') as file:
        lines = file.readlines()

    with open(locator_file_path, 'w') as file:
        for line in lines:
            if pattern.match(line):
                file.write(updated_line)
                print(f"🔁 Updated: {locator_name} → {updated_line.strip()}")
                updated = True
            else:
                file.write(line)

    if not updated:
        print(f"⚠️ Locator variable '{locator_name}' not found in {locator_file_path}")

def commit_and_push_changes():
    """
    Creates a new branch, commits updated locator file, and pushes to origin.
    """
    repo = Repo(REPO_PATH)

    # Ensure repo is clean
    assert not repo.is_dirty(untracked_files=True), "❌ Repo has uncommitted changes. Please commit/stash first."

    # Sync with main
    repo.git.checkout('main')
    repo.git.pull()

    # Create new branch and commit
    repo.git.checkout('-b', BRANCH_NAME)
    repo.git.add(LOCATOR_FILE_PATH)
    repo.index.commit("AI Fix: Broken locator updated")
    repo.git.push('--set-upstream', 'origin', BRANCH_NAME)

    print(f"🚀 Changes pushed to branch '{BRANCH_NAME}'")
