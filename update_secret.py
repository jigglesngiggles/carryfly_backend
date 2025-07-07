from playwright.sync_api import sync_playwright
import base64
import requests
import os
from nacl import encoding, public

# === CONFIGURATION ===
GITHUB_REPO = "jigglesngiggles/carryfly_backend"
SECRET_NAME = "SESSION_JSON_B64"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Step 1: Use Playwright to generate a headless session.json
def generate_session_file():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.amazon.com")
        page.wait_for_timeout(3000)  # Wait 3 seconds
        context.storage_state(path="session.json")
        browser.close()

generate_session_file()

# Step 2: Encode session.json to base64
with open("session.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

# Step 3: Fetch public key from GitHub
url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
resp = requests.get(url, headers=headers)
resp.raise_for_status()
key_info = resp.json()
public_key = key_info["key"]
key_id = key_info["key_id"]

# Step 4: Encrypt the secret using GitHub's public key
sealed_box = public.SealedBox(public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder()))
encrypted = sealed_box.encrypt(encoded.encode("utf-8"), encoder=encoding.Base64Encoder()).decode("utf-8")

# Step 5: Send encrypted value to GitHub
secret_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{SECRET_NAME}"
res = requests.put(secret_url, headers=headers, json={
    "encrypted_value": encrypted,
    "key_id": key_id
})
res.raise_for_status()
print(f"✅ Secret '{SECRET_NAME}' updated successfully.")
