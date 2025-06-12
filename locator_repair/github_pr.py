from github import Github
from locator_repair.config import GITHUB_TOKEN, GITHUB_REPO, BRANCH_NAME

def create_pull_request():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    pr = repo.create_pull(
        title="🤖 Auto-Fix: Broken Locator",
        body="Automatically fixed a broken locator using AI.",
        head=BRANCH_NAME,
        base="main"
    )
    print(f"Pull request created: {pr.html_url}")
