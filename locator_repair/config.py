import os
import uuid
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO_PATH = os.getenv("REPO_PATH")
BRANCH_NAME = f"fix-broken-locator-{uuid.uuid4().hex[:6]}"
LOCATOR_FILE_PATH = "locators/locators.py"
