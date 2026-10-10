import ollama
from ollama import chat

messages = [
    {
        "role": "user",
        "content": "salut ca va"
    }
]


response = chat(model="depressed_qwen", messages=messages)


print(response.message.content)
