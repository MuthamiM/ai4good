import os
import requests

USERNAME = "Mussa21"
TOKEN = "39f50dc9520994221f32ea0c96da060d5929c0ba"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path/home/{USERNAME}/ai4good"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Local directory to upload
LOCAL_DIR = r"c:\Users\Admin\Desktop\aiforgood"

# Files and folders to EXCLUDE
EXCLUDE = {".git", ".wrangler", "node_modules", "__pycache__", "venv", "pa_dir_list.txt", "pa_flowledger_list.txt", "pa_flowledger_reqs.txt", "pa_user_info.txt", "get_logs.py", "pa_deploy.py", "pa_test.py", "test_clone.py", "check_internet.py", "debug_pa.py", "debug_clone.py", "cleanup_consoles.py", "pa_upload.py", "pa_finish.py", "remove_emojis.py"}

def upload_file(local_path, remote_path):
    print(f"Uploading: {remote_path}")
    with open(local_path, 'rb') as f:
        r = requests.post(f"{API_BASE}/{remote_path}", headers=HEADERS, files={"content": f})
        if r.status_code not in [200, 201]:
            print(f"FAILED {remote_path}: {r.status_code} {r.text}")

def upload_recursive(current_local_dir, current_remote_rel_path=""):
    for item in os.listdir(current_local_dir):
        if item in EXCLUDE:
            continue
            
        local_path = os.path.join(current_local_dir, item)
        remote_rel_path = os.path.join(current_remote_rel_path, item).replace("\\", "/")
        
        if os.path.isfile(local_path):
            upload_file(local_path, remote_rel_path)
        elif os.path.isdir(local_path):
            upload_recursive(local_path, remote_rel_path)

if __name__ == "__main__":
    print("--- Starting Direct File Upload ---")
    upload_recursive(LOCAL_DIR)
    print("--- Upload Finished ---")
