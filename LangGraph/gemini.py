from google import genai
import os

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in 500 words"
)
print(response.text)