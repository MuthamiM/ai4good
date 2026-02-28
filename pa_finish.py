import requests

USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
DOMAIN = f"{USERNAME.lower()}.pythonanywhere.com"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

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
    configure_wsgi()
    reload_app()
    print(f"--- SUCCESS! Live at https://{DOMAIN} ---")
