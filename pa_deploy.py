import requests
import json
import time

USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
DOMAIN = f"{USERNAME.lower()}.pythonanywhere.com"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

def run_console_command(command, wait_time=20):
    print(f"Running console command: {command}")
    res = requests.post(f"{API_BASE}/consoles/", headers=HEADERS, json={"executable": "bash"})
    if res.status_code != 201:
        print("Failed to start console:", res.text)
        return ""
    console_id = res.json()["id"]
    time.sleep(5)
    requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": f"{command}\n"})
    time.sleep(wait_time)
    out = requests.get(f"{API_BASE}/consoles/{console_id}/get_latest_output/", headers=HEADERS)
    output = out.json().get('output', '')
    print("Output:", output)
    requests.delete(f"{API_BASE}/consoles/{console_id}/", headers=HEADERS)
    return output

def setup_app_and_db():
    # 0. Check disk space and folder structure
    print("Checking remote environment...")
    run_console_command("df -h && ls -F", wait_time=10)

    # 1. Clone Repo
    print("Attempting to clone repository...")
    output = run_console_command("rm -rf ai4good && git clone https://github.com/MuthamiM/ai4good.git ai4good", wait_time=45)
    if "Cloning into 'ai4good'..." not in output and "ai4good/" not in run_console_command("ls -F", wait_time=5):
        print("ERROR: Git clone failed or folder missing.")
        # Sometimes git needs credentials if public status is weird, but it should be public
        return False
    
    # 2. Init DB on server
    print("Initializing database...")
    db_script = """import sqlite3, os;
db_path = os.path.expanduser('~/ai4good/finai.db')
schema_path = os.path.expanduser('~/ai4good/schema.sql')
if os.path.exists(schema_path):
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.close()
    print('DATABASE INITIALIZED')
else:
    print(f'SCHEMA MISSING AT {schema_path}')
"""
    run_console_command(f'python3 -c "{db_script}"', wait_time=10)
    return True

def configure_wsgi():
    print("Updating WSGI...")
    wsgi_content = f"""
import sys
import os

path = '/home/{USERNAME}/ai4good'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)

from app import app as application
"""
    filename = f"{USERNAME.lower()}_pythonanywhere_com_wsgi.py"
    r = requests.post(
        f"{API_BASE}/files/path/var/www/{filename}",
        headers=HEADERS,
        files={"content": wsgi_content}
    )
    print("WSGI Update:", r.status_code)

def reload_app():
    print("Reloading WebApp...")
    r = requests.post(f"{API_BASE}/webapps/{DOMAIN}/reload/", headers=HEADERS)
    print("Reload Status:", r.status_code)

if __name__ == "__main__":
    if setup_app_and_db():
        configure_wsgi()
        reload_app()
        print(f"--- SUCCESS! Live at https://{DOMAIN} ---")
    else:
        print("--- DEPLOYMENT FAILED ---")
