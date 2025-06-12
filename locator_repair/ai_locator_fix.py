import openai
from locator_repair.config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

def ai_suggest_locator_fix(old_locator):
    prompt = f"""Broken Selenium locator: {old_locator}.
Suggest a corrected XPath or CSS selector.
Return as: (By.XPATH, \"new_xpath\")"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return eval(response.choices[0].message.content.strip())
