import requests
import json
import urllib3
import hashlib

urllib3.disable_warnings()

url = "https://authentication.thinxview.com/api/auth/login/"
pwd_raw = "Aravind@123"
pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()

print(f"DEBUG: Password: {pwd_raw}", file=__import__('sys').stderr)
print(f"DEBUG: Hash: {pwd_hash}", file=__import__('sys').stderr)

payload = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "password": pwd_hash,
    "remember_me": True
}

print(f"DEBUG: Payload: {json.dumps(payload, indent=2)}", file=__import__('sys').stderr)

try:
    resp = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=30
    )
    
    print(f"DEBUG: Status: {resp.status_code}", file=__import__('sys').stderr)
    print(f"DEBUG: Response: {resp.text[:200]}", file=__import__('sys').stderr)
    
    if resp.status_code == 200:
        print(json.dumps(resp.json()))
    else:
        msg = f"Login failed: Status {resp.status_code}. Response: {resp.text}"
        print(json.dumps({"error": msg}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
