import re
from locator_repair.config import LOCATOR_FILE_PATH, REPO_PATH, BRANCH_NAME
from git import Repo

def update_locator_file(old_locator, new_locator):
    with open(LOCATOR_FILE_PATH, 'r') as f:
        content = f.read()

    # Extract just the XPath or CSS string (tuple's second item)
    old_locator_str = old_locator[1] if isinstance(old_locator, tuple) else str(old_locator)
    new_locator_str = new_locator[1] if isinstance(new_locator, tuple) else str(new_locator)

    # Escape special regex characters
    pattern = re.escape(old_locator_str)

    # Replace only the XPath or CSS portion
    updated = re.sub(pattern, new_locator_str, content)

    with open(LOCATOR_FILE_PATH, 'w') as f:
        f.write(updated)

    print(f"✅ Replaced XPath: {old_locator_str} → {new_locator_str}")

def commit_and_push_changes():
    repo = Repo(REPO_PATH)
    repo.git.checkout('main')
    repo.git.pull()
    repo.git.checkout('-b', BRANCH_NAME)
    repo.git.add(LOCATOR_FILE_PATH)
    repo.index.commit("AI Fix: Broken locator updated")
    repo.git.push('--set-upstream', 'origin', BRANCH_NAME)