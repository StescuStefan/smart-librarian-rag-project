from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env file where your OPENAI_API_KEY is stored
load_dotenv()

# Initialize the client with your API key (automatically pulled from env)
client = OpenAI()

# Create a chat completion using the gpt-4o-mini model
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful book recommendation assistant."},
        {"role": "user", "content": "I want a book about freedom and surveillance."}
    ],
    temperature=0.7,
    max_tokens=300
)

# Print the assistant's reply
print(response.choices[0].message.content)
# Ensure you have the OPENAI_API_KEY set in your environment variables
# or in the .env file for this to work correctly.