import os
import uuid
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO_PATH = os.getenv("REPO_PATH")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")  
AWS_REGION = "us-east-1"  # Bedrock-supported region
BRANCH_NAME = f"fix-broken-locator-{uuid.uuid4().hex[:6]}"
LOCATOR_FILE_PATH = "locators/locators.py"
ERROR_LOG_FILE_PATH = "logs/error_log.txt"
