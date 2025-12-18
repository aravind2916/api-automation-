import requests
import hashlib
import json
import urllib3
import sys

urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8')

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"
UPDATE_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/profile/aravind.m@gndsolutions.in/thinxfresh/update-password"

def get_token(password):
    h = hashlib.sha256(password.encode()).hexdigest()
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
            return resp.json()["token"]
        print(f"Login failed for {password}: {resp.status_code} - {resp.text}")
        return None
    except Exception as e:
        print(f"Login exception for {password}: {e}")
        return None

def update_password(token, new_pwd, confirm_pwd):
    try:
        resp = requests.put(
            UPDATE_URL,
            headers={"Authorization": f"Bearer {json.dumps(token)}", "Content-Type": "application/json"},
            json={"newPassword": new_pwd, "confirmPassword": confirm_pwd},
            verify=False,
            timeout=10
        )
        print(f"Update to {new_pwd}: Status {resp.status_code} - {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Update exception: {e}")
        return False

# 1. Login with current
current_pwd = "Aravind@123"
print(f"Logging in with {current_pwd}...")
token = get_token(current_pwd)

if not token:
    print("Initial login failed. Aborting.")
    sys.exit(1)

# 2. Try to update to something that should work
test_pwd = "Aravind@1234"
print(f"Attempting update to {test_pwd}...")
success = update_password(token, test_pwd, test_pwd)

if success:
    print("Update successful. Now reverting...")
    
    # 3. Login with NEW password
    token_new = get_token(test_pwd)
    if not token_new:
        print("CRITICAL: Could not login with NEW password. Account might be locked or password mismatch.")
        sys.exit(1)
        
    # 4. Revert
    revert_success = update_password(token_new, current_pwd, current_pwd)
    if revert_success:
        print("Revert success! Back to normal.")
    else:
        print("CRITICAL: Revert failed. Password is currently:", test_pwd)
else:
    print("Update failed. Password remains:", current_pwd)
