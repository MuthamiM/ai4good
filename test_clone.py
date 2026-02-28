import requests
import time

USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

def run_simple_clone():
    print("Starting clean clone...")
    # Start a console
    res = requests.post(f"{API_BASE}/consoles/", headers=HEADERS, json={"executable": "bash"})
    if res.status_code != 201:
        print("Failed to start console:", res.text)
        return
    console_id = res.json()["id"]
    time.sleep(5)
    
    # Send clone command
    cmd = "rm -rf ai4project && git clone https://github.com/MuthamiM/ai4good.git ai4project"
    requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": f"{cmd}\n"})
    
    # Wait for 60 seconds for git to finish
    print("Waiting 60s for clone...")
    time.sleep(60)
    
    # Check if folder exists via Files API
    r = requests.get(f"{API_BASE}/files/path/home/{USERNAME}/ai4project/", headers=HEADERS)
    if r.status_code == 200:
        print("SUCCESS: Folder exists!")
    else:
        print(f"FAILED: Folder not found. Status: {r.status_code}")
        print(r.text)
    
    # Cleanup console
    requests.delete(f"{API_BASE}/consoles/{console_id}/", headers=HEADERS)

if __name__ == "__main__":
    run_simple_clone()
