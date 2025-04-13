# src/api/chatGPT.py
import os
import time
import json
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "xxx"
os.environ["OPENAI_BASE_URL"] = "https://api.yesapikey.com/v1"
client = OpenAI()

def get_chat_response(user_message):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        if getattr(completion.choices[0].message, 'content', None):
            return completion.choices[0].message.content
            
        else:
            return 'No response from API.'
    except Exception as e:
        print(f"Error: {e}")
        return 'Error occurred while fetching response.'
