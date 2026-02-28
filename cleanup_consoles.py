import requests
USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Delete existing consoles
r = requests.get(f"{API_BASE}/consoles/", headers=HEADERS)
if r.status_code == 200:
    for console in r.json():
        print(f"Deleting ID: {console['id']}")
        requests.delete(f"{API_BASE}/consoles/{console['id']}/", headers=HEADERS)
else:
    print(f"Error: {r.status_code}")
