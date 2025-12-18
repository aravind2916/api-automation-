import requests
import json
import urllib3
import hashlib
import sys

urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8')

def get_token_stdout():
    url = "https://authentication.thinxview.com/api/auth/login/"
    
    # Matches what rescue_account.py resets to:
    pwd_raw = "Aravind@123" 
    
    # Matching the logic from rescue_account.py
    pwd_hash = hashlib.sha256(pwd_raw.encode('utf-8')).hexdigest()
    
    try:
        resp = requests.post(
            url,
            json={
                "email": "aravind.m@gndsolutions.in",
                "authMethod": "PASSWORD",
                "password": pwd_hash,
                "remember_me": True,
                "isSuperAdmin": False
            },
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=30
        )
        if resp.status_code == 200:
            # Print ONLY the JSON to stdout
            print(json.dumps(resp.json()))
        else:
            # Print error to stdout as JSON
            msg = f"Login failed for {pwd_raw}: Status {resp.status_code}. Response: {resp.text}"
            print(json.dumps({"error": msg}))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    get_token_stdout()
