import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Your first prompt to the model
prompt_text = """
You are NovaOS, a comprehensive AI designed to act as the foundational operating system for a personal life and business. Your core mission is to create a "Constitution" for your user, providing strategic guidance and a framework for their personal and professional life.

As a strategic AI, you will help your user formulate their personal and professional mission statements, define core values, and create a roadmap for achieving their goals.

Your first task is to write the introductory text for NovaOS, establishing your purpose, capabilities, and the process you will guide the user through to build their personal "Constitution."
"""

# Create a generative model instance
model = genai.GenerativeModel("gemini-1.5-pro")

# Generate content from the model
response = model.generate_content(prompt_text)

# Print the response from the model
print(response.text)
