"""
Quick test to verify Claude API connection works.
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load API key from .env file
load_dotenv()

# Create the Anthropic client
client = Anthropic()

# Send a simple test message
print("Sending test message to Claude...\n")

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": "Say hello to Petros, who is testing his Anthropic API key for the first time. Keep it brief — 2 sentences max."
        }
    ]
)

# Print the response
print("Claude's response:")
print(message.content[0].text)
print(f"\nTokens used: {message.usage.input_tokens} input, {message.usage.output_tokens} output")