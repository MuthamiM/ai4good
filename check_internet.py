import requests
import json
import time

USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

def run_internet_check():
    print("Checking internet access...")
    res = requests.post(f"{API_BASE}/consoles/", headers=HEADERS, json={"executable": "bash"})
    if res.status_code != 201:
        print("Failed to start console:", res.text)
        return
    console_id = res.json()["id"]
    time.sleep(5)
    
    # Send curl command
    cmd = "curl -I https://www.google.com"
    requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": f"{cmd}\n"})
    
    time.sleep(10)
    out = requests.get(f"{API_BASE}/consoles/{console_id}/get_latest_output/", headers=HEADERS)
    print("CURL OUTPUT:\n", out.json().get('output', ''))
    
    requests.delete(f"{API_BASE}/consoles/{console_id}/", headers=HEADERS)

if __name__ == "__main__":
    run_internet_check()
