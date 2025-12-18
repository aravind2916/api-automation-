import requests
import hashlib
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://authentication.thinxview.com/api/auth/login/"
EMAIL = "aravind.m@gndsolutions.in"

def check_password(pwd_plain):
    pwd_hash = hashlib.sha256(pwd_plain.encode()).hexdigest()
    payload = {
        "email": EMAIL,
        "password": pwd_hash,
        "authMethod": "PASSWORD",
        "remember_me": True
    }
    
    print(f"\nChecking password: {pwd_plain}")
    print(f"Hash: {pwd_hash}")
    
    try:
        # Mock request to inspect before sending
        req = requests.Request('POST', URL, json=payload, headers={"Content-Type": "application/json"}).prepare()
        print(f"DEBUG: URL: {req.url}")
        print(f"DEBUG: Body: {req.body}")
        print(f"DEBUG: Headers: {req.headers}")

        resp = requests.post(URL, json=payload, verify=False, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        if resp.status_code == 200:
            print(">>> SUCCESS! usage this password.")
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    if check_password("Aravind@123"):
        exit(0)
    if check_password("Aravind@1234"):
        exit(0)
    print("\n>>> BOTH FAILED. Account might be locked or password is different.")
