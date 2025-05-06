import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": "Hello, are you GPT-4?"}]
    )
    print("Success! You have access to GPT-4.")
    print(response.choices[0].message.content)
except Exception as e:
    print("Error accessing GPT-4:")
    print(e) 