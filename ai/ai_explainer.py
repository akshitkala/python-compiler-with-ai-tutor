import os
from groq import Groq
from config import Config

# Initialize Groq client
# Ensure GROQ_API_KEY is set in .env
client = Groq(api_key=Config.GROQ_API_KEY)

def generate_ai_explanation(prompt):
    """
    Calls Groq API to get explanation.
    """
    if not Config.GROQ_API_KEY:
        return "[System] Groq API Key not found. Please add GROQ_API_KEY to your .env file."

    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant"
,
            temperature=0.6,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[System] AI Connection Error: {str(e)}"
