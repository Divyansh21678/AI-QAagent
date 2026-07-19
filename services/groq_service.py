# services/groq_service.py
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_groq(prompt: str) -> str:
    try:
        # Llama 3.3 70b ya Mixtral testing ke liye best aur fast hain
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **Groq API Error:** {str(e)}"