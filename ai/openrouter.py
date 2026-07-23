from openai import OpenAI
from decouple import config
import json
import re

client = OpenAI(
    api_key=config("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def ask_ai(prompt):

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324",
        messages=[
            {
                "role": "system",
                "content": """
You are IntelliHealth AI.

Always return ONLY valid JSON.

Format:

{
"summary":"",
"risk":"",
"diet":"",
"exercise":"",
"sleep":"",
"hydration":"",
"followup":"",
"disclaimer":""
}

Do not return markdown.
Do not return explanation.
Only JSON.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content.strip()

    print("\n========== AI RAW RESPONSE ==========\n")
    print(content)
    print("\n=====================================\n")

    # Remove markdown if present
    content = re.sub(r"```json|```", "", content).strip()

    try:
        return json.loads(content)

    except Exception:

        return {
            "summary": content,
            "risk": "Unable to analyze.",
            "diet": "-",
            "exercise": "-",
            "sleep": "-",
            "hydration": "-",
            "followup": "-",
            "disclaimer": "AI response could not be structured properly."
        }