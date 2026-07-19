# services/gemini_service.py
import os
from google import genai
from google.genai.errors import ClientError
from dotenv import load_dotenv

load_dotenv()

# Client initialize karein
client = genai.Client()

def ask_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Update to 2.5-flash if needed, or keep 2.0-flash
            contents=prompt
        )
        return response.text
    except ClientError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "⚠️ **API Limit Reached (Error 429):** Aapka Gemini API free tier quota abhi khatam ho gaya hai. Kripya 20 seconds baad fir se try karein ya naya API key configure karein."
        return f"⚠️ **Gemini API Error:** {str(e)}"
    except Exception as e:
        return f"⚠️ **An unexpected error occurred:** {str(e)}"