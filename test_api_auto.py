import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.environ.get('OPENROUTER_API_KEY')
url = 'https://openrouter.ai/api/v1/chat/completions'
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://mussa21.pythonanywhere.com',
    'X-Title': 'FinWise AI',
}
data = {
    'model': 'openrouter/auto',
    'messages': [{'role': 'user', 'content': 'Is the capital of France Paris?'}]
}

try:
    r = requests.post(url, headers=headers, json=data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
