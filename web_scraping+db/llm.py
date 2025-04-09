from groq import Groq

client = Groq(
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
    stream=False,
)

print(chat_completion.choices[0].message.content)