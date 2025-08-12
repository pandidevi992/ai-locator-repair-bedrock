import boto3
import ast
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from locator_repair.config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN, AWS_REGION

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
