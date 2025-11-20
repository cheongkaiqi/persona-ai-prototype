import os
from openai import OpenAI

def experiment_with_llm():
    """
    Interactive LLM experimentation tool for learning prompt engineering.
    Experiment with temperature, max_tokens, and system messages.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Default configuration
    config = {
        # controls response randomness, 0.7 is balanced
        "temperature": 0.7,
        # limits response length
        "max_tokens": 1024,
        # defines the LLM behavior/personality
        "system_message": "You are a helpful assistant."
    }

    print("=== LLM Parameter Experimentation Tool ===\n")
    print("Commands:")
    print("  'set temp <value>' - Set temperature (0.0-2.0)")
    print("  'set tokens <value>' - Set max tokens")
    print("  'set system <message>' - Set system message")
    print("  'config' - Show current configuration")
    print("  'ask <question>' - Ask the LLM a question")
    print("  'quit' - Exit\n")

    while True:
        # Gets user command and removes whitespace
        user_input = input(">>> ").strip()

        if user_input.lower() == "quit":
            print("Exiting...")
            break

        elif user_input.lower() == "config":
            print("\nCurrent Configuration:")
            print(f"  Temperature: {config['temperature']}")
            print(f"  Max Tokens: {config['max_tokens']}")
            print(f"  System Message: {config['system_message']}\n")

        elif user_input.lower().startswith("set temp "):
            try:
                temp = float(user_input.split(" ", 2)[2])
                if 0.0 <= temp <= 2.0:
                    config["temperature"] = temp
                    print(f"Temperature set to {temp}\n")
                else:
                    print("Temperature must be between 0.0 and 2.0\n")
            except (ValueError, IndexError):
                print("Invalid format. Use: set temp <value>\n")

        elif user_input.lower().startswith("set tokens "):
            try:
                tokens = int(user_input.split(" ", 2)[2])
                if tokens > 0:
                    config["max_tokens"] = tokens
                    print(f"Max tokens set to {tokens}\n")
                else:
                    print("Max tokens must be greater than 0\n")
            except (ValueError, IndexError):
                print("Invalid format. Use: set tokens <value>\n")

        elif user_input.lower().startswith("set system "):
            message = user_input[11:].strip()
            config["system_message"] = message
            print(f"System message set to: {message}\n")

        # Sends question to GPT-4O Mini
        elif user_input.lower().startswith("ask "):
            question = user_input[4:].strip()
            if question:
                try:
                    # Makes an API request to OpenAI
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        max_tokens=config["max_tokens"],
                        temperature=config["temperature"],
                        messages=[
                            {"role": "system", "content": config["system_message"]},
                            {"role": "user", "content": question}
                        ]
                    )
                    print(f"\nResponse:\n{response.choices[0].message.content}\n")
                except Exception as e:
                    print(f"Error: {e}\n")
            else:
                print("Please provide a question. Use: ask <question>\n")

        else:
            print("Unknown command. Try 'config', 'set temp/tokens/system', 'ask', or 'quit'\n")

if __name__ == "__main__":
    experiment_with_llm()
