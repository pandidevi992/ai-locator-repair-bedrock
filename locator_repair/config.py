import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO_PATH = os.getenv("REPO_PATH")
BRANCH_NAME = "fix-broken-locator"
LOCATOR_FILE_PATH = "locators/locators.py"
