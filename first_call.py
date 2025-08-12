# Part 1: Your Contact List
# We import os to read the .env file for your API key.
import os

# Part 2: The Phone
# We import the tools needed to talk to me.
import vertexai
from vertexai.generative_models import GenerativeModel

# Part 3: The Message
# This is the message your Router Agent will give me.
# You can edit this message to be exactly what you want me to do.
first_task_prompt = (
    "Based on my project history and the core values of making a positive impact "
    "in the world, please help me write a formal mission statement and an "
    "ethical constitution for NovaOS. Also, suggest three high-level business "
    "strategies for pursuing market-interrupting tools in the areas of SaaS, "
    "blockchain, and VR/gaming."
)

# Part 4: The Call
# This line connects to my system, using your project and location.
# You MUST replace "your-project-id" with the ID from your Google Cloud project.
# You can find it on your dashboard, it looks something like "mystical-option-468822-a0".
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT_ID"), location="us-central1")

# This is the actual "phone call" to me, using the message you wrote.
model = GenerativeModel("gemini-1.5-pro")
response = model.generate_content(first_task_prompt)

# This prints my response to your terminal.
print(response.text)
