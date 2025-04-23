from openai import OpenAI

# client = OpenAI(
#   api_key="sk-20cc6f0ad5964bd8b3afa3c45e5ebabc"
# )



client = OpenAI(api_key="sk-20cc6f0ad5964bd8b3afa3c45e5ebabc", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)