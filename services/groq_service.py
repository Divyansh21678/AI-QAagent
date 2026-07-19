# services/groq_service.py

import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Local (.env) -> Cloud (Secrets)
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Configure it in .env or Streamlit Secrets.")

client = Groq(api_key=api_key)


def ask_groq(prompt: str) -> str:
    try:
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
        return f"⚠️ Groq API Error: {e}"