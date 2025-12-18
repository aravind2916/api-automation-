import requests
import hashlib
import urllib3
import json

urllib3.disable_warnings()

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"
EMAIL = "aravind.m@gndsolutions.in"

passwords = ["Aravind@123", "Aravind@1234"]

print("Testing passwords...")
print("-" * 50)

for pwd in passwords:
    pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
    payload = {
        "email": EMAIL,
        "authMethod": "PASSWORD",
        "password": pwd_hash,
        "remember_me": True
    }
    
    try:
        resp = requests.post(LOGIN_URL, json=payload, headers={"Content-Type": "application/json"}, verify=False, timeout=10)
        status = resp.status_code
        
        print(f"\nPassword: {pwd}")
        print(f"Hash: {pwd_hash}")
        print(f"Status: {status}")
        
        if status == 200:
            print(f"WORKS! This is the correct password.")
            with open("working_password.txt", "w") as f:
                f.write(f"Password: {pwd}\nHash: {pwd_hash}\n")
        else:
            print(f"Failed. Response: {resp.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "-" * 50)
print("Test complete. Check working_password.txt if successful.")
