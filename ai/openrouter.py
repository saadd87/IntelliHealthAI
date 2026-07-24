from openai import OpenAI
from decouple import config
import json
import re

client = OpenAI(
    api_key=config("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "deepseek/deepseek-chat-v3-0324"


# ===========================================
# AI CHAT (Returns Plain Text)
# ===========================================

def ask_chat(prompt):

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
You are IntelliHealth AI.

You are a professional AI Health Assistant.

Give clear, friendly and easy-to-understand health guidance.

Never prescribe medicines.

Recommend consulting a doctor for serious concerns.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        print("OPENROUTER CHAT ERROR:", e)

        return f"⚠ AI Error: {e}"


# ===========================================
# AI REPORT (Returns JSON)
# ===========================================

def ask_report(prompt):

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
You are IntelliHealth AI.

Return ONLY valid JSON.

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

Do not use markdown.

Do not explain anything.

Only return JSON.
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

        print("\n===== RAW AI REPORT =====\n")
        print(content)
        print("\n=========================\n")

        content = re.sub(r"```json|```", "", content).strip()

        return json.loads(content)

    except Exception as e:

        print("OPENROUTER REPORT ERROR:", e)

        return {
            "summary": "Unable to generate AI report.",
            "risk": "-",
            "diet": "-",
            "exercise": "-",
            "sleep": "-",
            "hydration": "-",
            "followup": "-",
            "disclaimer": str(e)
        }