"""
=== Exercise: Prompt Engineering with Roles and Few-Shot Examples ===

Purpose:
  Learn advanced prompt engineering techniques to improve LLM response quality
  and consistency.

Techniques covered:
  1. Role Assignment - Define what the model should act as
  2. Few-Shot Learning - Provide input-output examples before the actual task
  3. Combining roles with examples for optimal results

How to experiment:
  - Change the system role to different professions (doctor, lawyer, teacher)
  - Modify the few-shot examples to guide different outputs
  - Add more examples to see if quality improves
  - Compare responses with and without examples
  - Test how specific vs. vague examples affect results
"""

from openai import OpenAI

client = OpenAI()

# ============================================================================
# Technique 1: Role Assignment
# ============================================================================
print("1. ROLE ASSIGNMENT - Different roles produce different responses\n")

roles = [
    "You are a professional Python developer.",
    "You are a beginner programmer learning Python.",
    "You are a sarcastic Python expert who loves jokes.",
]

question = "How do you read a file in Python?"

for i, role in enumerate(roles, 1):
    print(f"Role {i}: {role}")
    print("-" * 50)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": question}
        ]
    )

    print(completion.choices[0].message.content)
    print("\n")

# ============================================================================
# Technique 2: Few-Shot Examples (Teaching by Example)
# ============================================================================
print("\n2. FEW-SHOT EXAMPLES - Providing examples guides the model\n")

# Example 1: Without few-shot examples
print("WITHOUT Few-Shot Examples:")
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Convert this sentence to past tense: 'I eat an apple'"}
    ]
)

print(completion.choices[0].message.content)
print("\n")

# Example 2: With few-shot examples
print("WITH Few-Shot Examples:")
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Convert this sentence to past tense: 'I run fast'"},
        {"role": "assistant", "content": "I ran fast"},
        {"role": "user", "content": "Convert this sentence to past tense: 'She reads a book'"},
        {"role": "assistant", "content": "She read a book"},
        {"role": "user", "content": "Convert this sentence to past tense: 'I eat an apple'"}
    ]
)

print(completion.choices[0].message.content)
print("\n")

# ============================================================================
# Technique 3: Role + Few-Shot Combined
# ============================================================================
print("\n3. COMBINING ROLE + FEW-SHOT EXAMPLES\n")

print("Task: Generate JSON responses in a specific format")
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a JSON formatter assistant. Always respond with valid JSON."
        },
        {
            "role": "user",
            "content": "Convert to JSON: Name is John, Age is 30"
        },
        {
            "role": "assistant",
            "content": '{"name": "John", "age": 30}'
        },
        {
            "role": "user",
            "content": "Convert to JSON: City is Paris, Country is France"
        },
        {
            "role": "assistant",
            "content": '{"city": "Paris", "country": "France"}'
        },
        {
            "role": "user",
            "content": "Convert to JSON: Product is Laptop, Price is 999"
        }
    ]
)

print(completion.choices[0].message.content)
print("\n")

# ============================================================================
# Technique 4: Custom Role with Domain-Specific Few-Shot
# ============================================================================
print("\n4. DOMAIN-SPECIFIC ROLE + FEW-SHOT\n")

print("Task: Code review assistant")
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a strict code review expert. Identify issues and suggest improvements."
        },
        {
            "role": "user",
            "content": "Review: x=1;y=2;z=x+y;print(z)"
        },
        {
            "role": "assistant",
            "content": "Issues: 1) Poor variable names (x, y, z) - use descriptive names. 2) No spaces around operators. 3) Missing comments. Suggestion: num1 = 1; num2 = 2; sum_result = num1 + num2; print(sum_result)"
        },
        {
            "role": "user",
            "content": "Review: def f(a,b){return a+b}"
        }
    ]
)

print(completion.choices[0].message.content)
print("\n")
