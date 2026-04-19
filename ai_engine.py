import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def generate_explanation(topic):
    prompt = f"Explain {topic} in simple terms with examples."

    res = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


def generate_quiz(topic, difficulty):
    prompt = f"""
Generate a multiple choice quiz on {topic}

Difficulty: {difficulty}

Rules:
- STRICTLY 10 questions
- 4 options each
- Return JSON

[
 {{
   "question": "...",
   "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
   "answer": "A"
 }}
]
"""

    res = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = res.choices[0].message.content

    try:
        return json.loads(content)
    except:
        content = content[content.find("["):content.rfind("]")+1]
        return json.loads(content)