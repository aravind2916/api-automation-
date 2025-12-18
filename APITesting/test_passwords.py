import requests
import hashlib
import urllib3

urllib3.disable_warnings()

url = "https://authentication.thinxview.com/api/auth/login/"
email = "aravind.m@gndsolutions.in"

# List of common passwords to try based on your test data
passwords_to_try = [
    "Aravind@123",      # Current password in get_token_cli.py
    "Aravind@1234",     # From test data
    "Password123!",     # Common pattern
    "C0mpl3x!Password", # From test data
    "Valid1@!",         # From test data
    "LongPassword123!@#$%",  # From test data
]

print(f"Testing login for: {email}\n")

for pwd_raw in passwords_to_try:
    pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()
    
    try:
        resp = requests.post(
            url,
            json={
                "email": email,
                "authMethod": "PASSWORD",
                "password": pwd_hash,
                "remember_me": True
            },
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=30
        )
        
        print(f"Password: {pwd_raw}")
        print(f"  Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"  ✓ SUCCESS! This password works!")
            print(f"  Response: {resp.json()}")
            break
        else:
            print(f"  ✗ Failed: {resp.text[:100]}")
        print()
        
    except Exception as e:
        print(f"Password: {pwd_raw}")
        print(f"  ✗ Error: {e}\n")
