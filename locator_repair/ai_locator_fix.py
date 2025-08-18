import boto3
import ast
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from locator_repair.config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN, AWS_REGION
from locator_repair.context_extractor import extract_relevant_html

# ---- Bedrock Client ----
bedrock = boto3.client(
    "bedrock-runtime",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
)

# ---- Claude 3.7 Sonnet Model ----
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

# ---- Existing helper functions ----
def capture_dom(driver: WebDriver):
    return driver.page_source

def extract_relevant_html_llm(dom: str, description: str, max_matches: int) -> str:
    
    user_prompt = f"""
You are an expert front-end tester. I will give you several HTML snippets from the same page and a short description of a target element.  

Your task:  
- Identify the **single HTML element tag** that directly matches the description (not its parent container or label).  
- If multiple elements could match, return only the most direct match (e.g. `<input>` not `<label>`).  
- Return ONLY the HTML of that element (not the surrounding container or sibling tags).  

OUTPUT RULES (IMPORTANT):  
- Wrap your output EXACTLY between these markers on their own lines:  
<<<RELEVANT_HTML_START>>>  
... your html here ...  
<<<RELEVANT_HTML_END>>>  

Description: {description}  
Give me the exact matching HTML element from the following: {max_matches}  

HTML SNIPPETS:  
{dom}
"""
    response = bedrock.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=[{
            "role": "user",
            "content": [{"text": user_prompt}]
        }],
        inferenceConfig={
            "temperature": 0.2,
            "maxTokens": 150,
            "topP": 0.9
        }
    )

    content = response["output"]["message"]["content"]
    relevantHtml = "".join(part.get("text", "") for part in content).strip()
    print(f"Extracted Html via llm {relevantHtml}")

    return relevantHtml

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
    # Call the external extractor (LLM-driven)
    html_snippet = extract_relevant_html_llm(
    dom=dom,
    description=description,   # "username input box"
    max_matches=5
)

    prompt = f"""You are a Selenium expert.
The following locator is broken: {old_locator}
{f'Element description: {description}' if description else ''}
{f'HTML snippet:\n{html_snippet}' if html_snippet else ''}
Return only the corrected Python tuple as output in this exact format:
(By.XPATH, "new_xpath") — nothing else, no explanation and By.Xpath don't require the single or double quotes.
Locator is case-sensitive, so ensure the case matches the original locator.
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
