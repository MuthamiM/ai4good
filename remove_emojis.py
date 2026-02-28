import os
import re

# Regex for emojis (covers most common ranges)
# This avoids stripping things like '—' (em-dash) or '' (box drawing) if they aren't in these ranges
# However, to be safe and thorough for "logs", we might want to target non-ASCII if they cause issues.
# But let's try a specific emoji regex first.
EMOJI_PATTERN = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map symbols
    "\U0001f1e6-\U0001f1ff"  # flags (iOS)
    "\U00002702-\U000027b0"  # dingbats
    "\U000024c2-\U0001f251"
    "\U0001f900-\U0001f9ff"  # supplemental symbols and pictographs
    "\U0001fa70-\U0001faff"  # symbols and pictographs extended-a
    "\U00002600-\U000026ff"  # miscellaneous symbols
    "]+", flags=re.UNICODE
)

EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', '.wrangler', 'static/uploads'}
EXCLUDE_FILES = {'finai.db'}

def remove_emojis_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = EMOJI_PATTERN.sub('', content)
        
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Removed emojis from: {filepath}")
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def walk_and_clean(root_dir):
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file in EXCLUDE_FILES:
                continue
            if file.endswith(('.py', '.md', '.html', '.js', '.css', '.txt')):
                remove_emojis_from_file(os.path.join(root, file))

if __name__ == "__main__":
    print("--- Starting Emoji Removal ---")
    walk_and_clean('.')
    print("--- Emoji Removal Finished ---")
