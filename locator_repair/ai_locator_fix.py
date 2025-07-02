# from openai import OpenAI
# from locator_repair.config import OPENAI_API_KEY

# # Instantiate the client with your API key
# client = OpenAI(api_key=OPENAI_API_KEY)

# def ai_suggest_locator_fix(old_locator):
#     prompt = f"""Broken Selenium locator: {old_locator}.
# Suggest a corrected XPath or CSS selector.
# Return as: (By.XPATH, "new_xpath")"""

#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )

#     suggestion = response.choices[0].message.content.strip()
#     return eval(suggestion)

from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import ollama

def capture_dom(driver: WebDriver):
    """Returns the page source from Selenium driver."""
    return driver.page_source

def extract_relevant_html(dom: str, element_keyword: str) -> str:
    """Extracts relevant HTML snippets matching the keyword in text or attributes."""
    soup = BeautifulSoup(dom, 'html.parser')

    matches = []

    # Keywords to match in attributes
    attr_keys = ["name", "id", "placeholder", "aria-label", "value"]

    for tag in soup.find_all(True):
        # Check inner text
        if tag.string and element_keyword.lower() in tag.string.lower():
            matches.append(tag)
            continue

        # Check attribute values
        for attr in attr_keys:
            if tag.has_attr(attr) and element_keyword.lower() in tag[attr].lower():
                matches.append(tag)
                break

    if not matches:
        return dom[:10000]  # fallback

    output_snippets = []

    for tag in matches:
        # Try to find the context (parent div/form/body)
        context_tag = tag.find_parent("div", class_=lambda c: c and ("grid" in c or "col-12" in c or "ui-input" in c))
        if not context_tag:
            context_tag = tag.find_parent(["form", "body"])
        if not context_tag:
            context_tag = tag.parent

        output_snippets.append(str(context_tag))

    combined = "\n<!-- match -->\n".join(output_snippets)
    return combined[:10000]

def ai_suggest_locator_fix(old_locator: str, driver: WebDriver = None,
                            description: str = "") -> tuple:
    """
    Use Ollama to suggest a fixed Selenium locator tuple.

    Parameters:
    - old_locator: the original broken locator string.
    - driver: optional Selenium driver to extract the DOM.
    - tag, attr, value: optional for targeting the broken element in the DOM.
    - description: optional description to help LLM understand the element.
    Note: XPaths are case-sensitive — match attribute values exactly.

    Returns:
    - A tuple like (By.XPATH, "new_xpath")
    """
    html_snippet = ""
    dom = capture_dom(driver)
    html_snippet = extract_relevant_html(dom, "email")

    prompt = f"""You are a Selenium expert.
The following locator is broken: {old_locator}
{f'Element description: {description}' if description else ''}
{f'HTML snippet:\n{html_snippet}' if html_snippet else ''}
Return only the corrected Python tuple as output in this exact format:
(By.XPATH, "new_xpath") — nothing else, no explanation and By.Xpath don't require the single or double quotes.
"""

    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )

    suggestion = response['message']['content'].strip()
    print(f"[LLM Suggestion] {suggestion}")
    return eval(suggestion)