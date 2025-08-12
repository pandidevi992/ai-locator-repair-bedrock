import boto3
import ast
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# ---- AWS Credentials ----
AWS_ACCESS_KEY = "ASIAZHPEO3KQUNTU2Q4M"
AWS_SECRET_KEY = "S7AL87oKbQgrFNR+8gFIkEslGrphnczdDozX47Og"
AWS_SESSION_TOKEN = "IQoJb3JpZ2luX2VjEMn//////////wEaCXVzLWVhc3QtMSJGMEQCIE8mzhJsiEbVpRfcbOMhcr613w2B/i049H5zxlC1hrsQAiBiIXaHbbXUUmo3H8NoztgCYK0dPoQJC/4ffl/IqCPA3CqVAwgSEAUaDDYzNDUyMzY3MTIwMSIM+wOipInVjP/h3zsWKvIC5QV4G9h8f5YEINgQz0rcf5Q7T+whDVPbZIlv89Nt0uwM0pIWZpiLjLwpXzvOG2jvR9iTSRxlYwgbb0J9pYqu3hUCmrjG8j2OZTYMeHSKtBchSUsUYGngnvnLS/MGaH0MLN6BUXVyF8/csyh+xgYAEu7X4NmTnlx9moWHCj+VVLNAs5Vd3G3gZoA2LBooU/shmKuzosOA9wPu9TtNbj7cCf2+jM48blnMt9bVBPQn/u64DfRLlJxnLksgP0izvf3fthPtnNdVSsd1CIlvtlF18Yn/LR4lz8q7KzXPFkJ8QfoXkjunvtJveE/Xpsv0SRU2hnDSK8ut5LNoi86wMoAc2snSYZMjV0KJ6q6GaD0WjbMIoGdNN3MDITThELYjHuO/8zNIyesfKq+20sFNxjjvPJlWd60oH8xTdo1BNMHuIOwY9wTkXVMW4869uUlGVdFi8X6FhdInP6nQ0J8qzcNajRUGZJF53Ah3QI9pATOglon6ZjC7++vEBjqnAdFYHyK82AGQCPuO8t05o9cTNLmhwPYVeIhSMyjg7eweI2R6s4DxQVLtO50ZBVE5NJADMei5KYxYBAG5wj/uCgvZsd2rx2q/FpYIuNqxpT03Z25GKXECUhDo1YyMLhEwehni7Z1+lZdO+cEXwXsjSqVMUZwF8s878iXl3Bhtx5p8mus5Mxq0G5eWmKM/5vQYDZJ6wH/sNQyXXO6ffyFopV1AzQak/VEA"  # Required for temporary creds; else None/""
AWS_REGION = "us-east-1"  # Bedrock-supported region

# ---- Bedrock Client ----
bedrock = boto3.client(
    "bedrock-runtime",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
)

# ---- Claude 3.7 Sonnet Model ----
BEDROCK_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# ---- Existing helper functions ----
def capture_dom(driver: WebDriver):
    return driver.page_source

def extract_relevant_html(dom: str, element_keyword: str) -> str:
    soup = BeautifulSoup(dom, 'html.parser')
    matches = []
    attr_keys = ["name", "id", "placeholder", "aria-label", "value"]

    for tag in soup.find_all(True):
        if tag.string and element_keyword.lower() in tag.string.lower():
            matches.append(tag)
            continue
        for attr in attr_keys:
            if tag.has_attr(attr) and element_keyword.lower() in tag[attr].lower():
                matches.append(tag)
                break

    if not matches:
        return dom[:10000]

    output_snippets = []
    for tag in matches:
        context_tag = tag.find_parent("div", class_=lambda c: c and ("grid" in c or "col-12" in c or "ui-input" in c))
        if not context_tag:
            context_tag = tag.find_parent(["form", "body"])
        if not context_tag:
            context_tag = tag.parent
        output_snippets.append(str(context_tag))

    combined = "\n<!-- match -->\n".join(output_snippets)
    return combined[:10000]

def normalize_locator(suggestion):
    """
    Normalize various LLM outputs into ('xpath', '//selector').
    Always lowercases the strategy and strips By. prefix if present.
    """
    # tuple form
    if isinstance(suggestion, tuple) and len(suggestion) == 2:
        strategy, value = suggestion
        strategy = str(strategy)
        if "." in strategy:  # handles By.XPATH or 'By.XPATH'
            strategy = strategy.split(".", 1)[1]
        return (strategy.lower(), str(value))

    # string form
    if isinstance(suggestion, str):
        s = suggestion.strip()

        # drop outer parentheses if present
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1].strip()

        if "," in s:
            strategy_part, selector_part = s.split(",", 1)
            strategy = strategy_part.strip().strip("'").strip('"')
            if strategy.lower().startswith("by."):
                strategy = strategy.split(".", 1)[1]
            selector = selector_part.strip().strip("'").strip('"')
            return (strategy.lower(), selector)

    raise ValueError(f"Invalid locator format from model: {suggestion!r}")


# ---- Bedrock-powered locator fix ----
def ai_suggest_locator_fix(old_locator: str, driver: WebDriver = None, description: str = "") -> tuple:
    dom = capture_dom(driver)
    html_snippet = extract_relevant_html(dom, "email")

    prompt = f"""You are a Selenium expert.
The following locator is broken: {old_locator}
{f'Element description: {description}' if description else ''}
{f'HTML snippet:\n{html_snippet}' if html_snippet else ''}
Return only the corrected Python tuple as output in this exact format:
(By.XPATH, "new_xpath") — nothing else, no explanation and By.Xpath don't require the single or double quotes.
"""

    response = bedrock.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=[{
            "role": "user",
            "content": [{"text": prompt}]
        }],
        inferenceConfig={
            "temperature": 0.2,
            "maxTokens": 150,
            "topP": 0.9
        }
    )

    content = response["output"]["message"]["content"]
    suggestion = "".join(part.get("text", "") for part in content).strip()
    print(f"[LLM Suggestion] {suggestion}")

    #llm_tuple = ast.literal_eval(suggestion)
    return normalize_locator(suggestion)
