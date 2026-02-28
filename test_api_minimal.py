import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.environ.get('OPENROUTER_API_KEY')
print(f"Key used: {key[:10]}...{key[-5:]}")

url = 'https://openrouter.ai/api/v1/chat/completions'
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'HTTP-Referer': 'http://localhost:3000',
    'X-Title': 'Test App'
}
data = {
    'model': 'openai/gpt-4o-mini',
    'messages': [{'role': 'user', 'content': 'Say hello'}]
}

try:
    r = requests.post(url, headers=headers, json=data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
