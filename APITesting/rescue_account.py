import requests
import hashlib
import json
import urllib3
import sys

urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8')

# P@sswørd123
passwords_to_try = [
    "Aravind@123", 
    "Aravind@1234", 
    "Aravind@12345",
    "ThinxView@2025",
    "P@ssw\u00F8rd123", # unicode ø
    "P@sswørd123",     # literal ø
    "P@sswrd123",      # maybe char was dropped?
    "LongPassword123!@#$%"
]

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"
UPDATE_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/profile/aravind.m@gndsolutions.in/thinxfresh/update-password"

def get_token(password):
    print(f"Trying to login with: {password}")
    # try utf-8 encoding for hash
    h = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    try:
        resp = requests.post(
            LOGIN_URL,
            json={
                "email": "aravind.m@gndsolutions.in", 
                "authMethod": "PASSWORD", 
                "password": h, 
                "remember_me": True,
                "isSuperAdmin": False
            },
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=10
        )
        if resp.status_code == 200:
            print(f"LOGIN SUCCESS with {password}")
            return resp.json()["token"]
    except Exception as e:
        print(f"Error checking '{password}': {e}")
    return None

def reset_password(token, new_pwd):
    print(f"Resetting password to {new_pwd}...")
    try:
        resp = requests.put(
            UPDATE_URL,
            headers={"Authorization": f"Bearer {json.dumps(token)}", "Content-Type": "application/json"},
            json={"newPassword": new_pwd, "confirmPassword": new_pwd},
            verify=False,
            timeout=10
        )
        if resp.status_code == 200:
            print("RESET SUCCESSFUL.")
            return True
        else:
            print(f"RESET FAILED: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"Reset exception: {e}")
        return False

# Main rescue loop
for pwd in passwords_to_try:
    token = get_token(pwd)
    if token:
        # We found the working password! 
        # Now reset it to standard
        if pwd != "Aravind@123":
            reset_password(token, "Aravind@123")
        else:
            print("Password is already Aravind@123. No reset needed.")
        break
else:
    print("FATAL: Could not match any password. Account lost?")
