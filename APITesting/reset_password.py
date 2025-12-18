
import requests
import hashlib
import json
import urllib3

urllib3.disable_warnings()

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"
UPDATE_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/profile/aravind.m@gndsolutions.in/thinxfresh/update-password"

EMAIL = "aravind.m@gndsolutions.in"
CURRENT_PASS = "Aravind@1234"
NEW_PASS = "Aravind@123"

def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def run():
    # 1. Login
    print(f"Logging in with {CURRENT_PASS}...")
    login_payload = {
        "email": EMAIL,
        "password": hash_pwd(CURRENT_PASS),
        "authMethod": "PASSWORD",
        "remember_me": True
    }
    resp = requests.post(LOGIN_URL, json=login_payload, headers={"Content-Type": "application/json"}, verify=False)
    print(f"Login Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Login Response: {resp.text}")
        return

    token = resp.json().get("token")
    print("Logged in. Token acquired.")

    # 2. Update Password
    print(f"Updating password to {NEW_PASS}...")
    update_payload = {
        "newPassword": NEW_PASS,
        "confirmPassword": NEW_PASS
    }
    headers = {
        "Authorization": f"Bearer {json.dumps(token)}",
        "Content-Type": "application/json"
    }
    resp2 = requests.put(UPDATE_URL, json=update_payload, headers=headers, verify=False)
    print(f"Update Status: {resp2.status_code}")
    print(f"Update Response: {resp2.text}")

if __name__ == "__main__":
    run()
