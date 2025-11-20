"""
=== Exercise: Basic Completion Requests with Different Prompts ===

Purpose:
  Learn how different prompts affect LLM responses and output quality.

How to experiment:
  - Modify existing prompts to be more/less specific
  - Add new prompts to test different scenarios
  - Change the system message to see different assistant behaviors
  - Compare responses across multiple runs
  - Note which prompts produce better results

"""

from openai import OpenAI

# import os
# from dotenv import load_dotenv
# load_dotenv()

client = OpenAI()

# inside openAI() we can put api_key = os.getenv("OPEN_API_KEY")

# Test different prompts to see how they affect responses
prompts = [
    "Write a simple Java code that prints 1 to 10.",
    "Write a Python function that adds two numbers.",
    "Explain what machine learning is in one sentence.",
    "Create a SQL query to select all users from a table.",
]

print("=== Testing Different Prompts ===\n")

for i, prompt in enumerate(prompts, 1):
    print(f"Prompt {i}: {prompt}")
    print("-" * 50)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    print(completion.choices[0].message.content)
    print("\n")

