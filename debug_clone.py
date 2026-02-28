import requests
import time
USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

def run_debug_clone():
    # 1. Start a console
    res = requests.post(f"{API_BASE}/consoles/", headers=HEADERS, json={"executable": "bash"})
    if res.status_code != 201:
        print("Failed to start console:", res.text)
        return
    console_id = res.json()["id"]
    time.sleep(3)
    
    # 2. Try the clone and capture everything
    cmd = "git clone https://github.com/MuthamiM/ai4good.git ai4good 2>&1"
    requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": f"{cmd}\n"})
    
    # 3. Wait and read
    time.sleep(15)
    out = requests.get(f"{API_BASE}/consoles/{console_id}/get_latest_output/", headers=HEADERS)
    print("CLONE OUTPUT:\n", out.json().get('output', ''))
    
    # 4. Cleanup
    requests.delete(f"{API_BASE}/consoles/{console_id}/", headers=HEADERS)

run_debug_clone()
