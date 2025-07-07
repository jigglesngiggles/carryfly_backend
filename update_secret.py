import base64
import requests
import subprocess
import os

# === CONFIGURATION ===
GITHUB_REPO = "jigglesngiggles/carryfly_backend"
SECRET_NAME = "SESSION_JSON_B64"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Step 1: Regenerate session.json using Playwright codegen
subprocess.run(["playwright", "codegen", "--save-storage", "session.json", "https://www.amazon.com"], check=True)

# Step 2: Encode session.json to base64
with open("session.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

# Step 3: GitHub API call to set the secret
url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{SECRET_NAME}"

# Get the repo’s public key (required for encrypting the secret)
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
resp = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key", headers=headers)
resp.raise_for_status()
key_info = resp.json()

# Encrypt the secret using the public key (GitHub expects this)
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization, hashes
from nacl import encoding, public

public_key = key_info["key"]
key_id = key_info["key_id"]

sealed_box = public.SealedBox(public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder()))
encrypted = sealed_box.encrypt(encoded.encode("utf-8"), encoder=encoding.Base64Encoder()).decode("utf-8")

# Update the secret
res = requests.put(url, headers=headers, json={
    "encrypted_value": encrypted,
    "key_id": key_id
})
res.raise_for_status()
print(f"✅ Secret '{SECRET_NAME}' updated successfully.")
