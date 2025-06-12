import re
from locator_repair.config import LOCATOR_FILE_PATH, REPO_PATH, BRANCH_NAME
from git import Repo

def update_locator_file(old_locator, new_locator):
    with open(LOCATOR_FILE_PATH, 'r') as f:
        content = f.read()
    updated = re.sub(re.escape(str(old_locator)), str(new_locator), content)
    with open(LOCATOR_FILE_PATH, 'w') as f:
        f.write(updated)

def commit_and_push_changes():
    repo = Repo(REPO_PATH)
    repo.git.checkout('main')
    repo.git.pull()
    repo.git.checkout('-b', BRANCH_NAME)
    repo.git.add(LOCATOR_FILE_PATH)
    repo.index.commit("AI Fix: Broken locator updated")
    repo.git.push('--set-upstream', 'origin', BRANCH_NAME)
