# first_call_apikey.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("Set GOOGLE_API_KEY in your .env")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")
resp = model.generate_content("Say hello to NovaOS in one short sentence.")
print(resp.text.strip())
