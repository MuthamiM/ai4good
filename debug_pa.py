import requests
import json
import time

USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

def run_debug_env():
    print("Checking remote environment...")
    res = requests.post(f"{API_BASE}/consoles/", headers=HEADERS, json={"executable": "bash"})
    if res.status_code != 201:
        print("Failed to start console:", res.text)
        return
    console_id = res.json()["id"]
    time.sleep(5)
    
    # 1. Check disk and list files
    requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": "df -h && ls -la\n"})
    time.sleep(10)
    
    # 2. Try the clone again with verbose output
    requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": "rm -rf ai4good && git clone --verbose https://github.com/MuthamiM/ai4good.git ai4good 2>&1\n"})
    time.sleep(40)
    
    # 3. List files again to see if ai4good exists
    requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": "ls -la && ls -R ai4good | head -n 20\n"})
    time.sleep(10)
    
    out = requests.get(f"{API_BASE}/consoles/{console_id}/get_latest_output/", headers=HEADERS)
    print("DEBUG OUTPUT:\n", out.json().get('output', ''))
    
    requests.delete(f"{API_BASE}/consoles/{console_id}/", headers=HEADERS)

if __name__ == "__main__":
    run_debug_env()
