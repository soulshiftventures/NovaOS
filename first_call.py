import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationResponse

# Initialize Vertex AI with your project ID and location
# Replace 'mystical-option-468822-a0' with your actual Google Cloud Project ID
vertexai.init(project="mystical-option-468822-a0", location="us-central1")

model = GenerativeModel("gemini-1.5-pro")

# Your first prompt to the model
prompt_text = """
You are NovaOS, a comprehensive AI designed to act as the foundational operating system for a personal life and business. Your core mission is to create a "Constitution" for your user, providing strategic guidance and a framework for their personal and professional life.

As a strategic AI, you will help your user formulate their personal and professional mission statements, define core values, and create a roadmap for achieving their goals.

Your first task is to write the introductory text for NovaOS, establishing your purpose, capabilities, and the process you will guide the user through to build their personal "Constitution."
"""

# Generate content from the model
response = model.generate_content(
    prompt_text,
    generation_config={
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95
    }
)

# Print the response from the model
print(response.text)
