# services/gemini_service.py

import os
import streamlit as st
from google import genai
from google.genai.errors import ClientError
from dotenv import load_dotenv

load_dotenv()

# Local (.env) -> Streamlit Cloud (Secrets)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Configure it in .env or Streamlit Secrets."
    )

# Initialize Gemini Client
client = genai.Client(api_key=api_key)


def ask_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    except ClientError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return (
                "⚠️ API Limit Reached. Please try again later "
                "or configure another API key."
            )
        return f"⚠️ Gemini API Error: {str(e)}"

    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}"