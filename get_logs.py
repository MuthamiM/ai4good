import requests
USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
DOMAIN = "mussa21.pythonanywhere.com"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Get a large chunk of the error log
r = requests.get(f"{API_BASE}/files/path/var/log/{DOMAIN}.error.log", headers=HEADERS)
if r.status_code == 200:
    print(r.text[-6000:]) # Get last 6000 chars
else:
    print(f"Error: {r.status_code}")
