import requests
import hashlib
import json
import urllib3

urllib3.disable_warnings()

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"
EMAIL = "aravind.m@gndsolutions.in"
# Full list from conftest.py
PASSWORDS = [
    "Aravind@123",
    "Aravind@1234",
    "Aravind@12345",
    "ThinxView@2025",
    "P@ssw\u00F8rd123",
    "P@sswørd123",
    "P@sswrd123",
    "LongPassword123!@#$%",
    "Pa$$w0rd!",
    "Valid123!",
]

def check_login(pwd, is_super_admin=False):
    pwd_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
    
    payload = {
        "email": EMAIL,
        "authMethod": "PASSWORD",
        "password": pwd_hash,
        "remember_me": True
    }
    # isSuperAdmin FALSE by default as per conftest
    if is_super_admin is not None:
         payload["isSuperAdmin"] = is_super_admin
    
    # print(f"Testing pass '{pwd}'...")
    try:
        r = requests.post(LOGIN_URL, json=payload, verify=False, timeout=10)
        if r.status_code == 200:
            print(f">>> SUCCESS with password: '{pwd}'")
            return True
        elif r.status_code == 404:
            # Check body
            if "User not found" in r.text:
                 print(f"FAILED '{pwd}': User not found (404)")
                 return "USER_NOT_FOUND" 
    except:
        pass
    print(f"FAILED '{pwd}': {r.status_code}")
    return False

if __name__ == "__main__":
    print(f"Checking {len(PASSWORDS)} passwords for {EMAIL}...")
    
    # Check if user exists first? (Any password checks existence if it returns 'User not found' vs 'Invalid password')
    # Assuming API reveals existence.
    
    for p in PASSWORDS:
        res = check_login(p, is_super_admin=False)
        if res == True:
            exit(0)
        if res == "USER_NOT_FOUND":
            print("!!! ABORTING: User definitely does not exist.")
            exit(1)
            
    print("All passwords failed (Invalid password or other error).")
