import requests
import hashlib
import urllib3

urllib3.disable_warnings()

url = "https://authentication.thinxview.com/api/auth/login/"
email = "aravind.m@gndsolutions.in"

# Passwords from the successful test run
passwords_to_try = [
    "Aravind@123",
    "LongPassword123!@#$%",  # from valid_max_length_20chars which PASSED
    "P@sswørd123",  # from unicode_characters which PASSED with 200
]

for pwd in passwords_to_try:
    pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
    
    payload = {
        "email": email,
        "authMethod": "PASSWORD",
        "password": pwd_hash,
        "remember_me": True,
        "isSuperAdmin": False
    }
    
    resp = requests.post(url, json=payload, verify=False, timeout=10)
    
    status_symbol = "✅" if resp.status_code == 200 else "❌"
    print(f"{status_symbol} Password: {pwd:30s} | Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print(f"   SUCCESS! Current password is: {pwd}")
        break
