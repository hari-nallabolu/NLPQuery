import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, are you GPT-3.5?"}]
    )
    print("Success! You have access to GPT-3.5.")
    print(response.choices[0].message.content)
except Exception as e:
    print("Error accessing GPT-3.5:")
    print(e) 