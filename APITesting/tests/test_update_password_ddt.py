import os
import json
import pytest
import requests
UPDATE_PASSWORD_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/"
    "api/profile/aravind.m@gndsolutions.in/thinxfresh/update-password"
)
LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"

import hashlib

def get_temp_token(password):
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
            return resp.json().get("token")
    except Exception:
        pass
    return None

def reset_password(current_password, new_password_target="Aravind@123"):
    if current_password == new_password_target:
        return
    
    token = get_temp_token(current_password)
    if not token:
        print(f"Failed to get token for reset using {current_password}")
        return

    try:
        requests.put(
            UPDATE_PASSWORD_URL,
            headers={"Authorization": f"Bearer {json.dumps(token)}", "Content-Type": "application/json"},
            json={"newPassword": new_password_target, "confirmPassword": new_password_target},
            verify=False,
            timeout=10
        )
    except Exception as e:
        print(f"Failed to reset password: {e}")



def load_ddt_cases(filename):
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


DDT_CASES = load_ddt_cases("update_password_ddt.json")


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_update_password_ddt(case, auth_token):

    payload = case.get("payload")
    include_auth = case.get("include_auth", True)
    expected_status = case["expected_status"]

    headers = {"Content-Type": "application/json"}

    if include_auth:
        # Use auth_token fixture
        headers["Authorization"] = f"Bearer {auth_token}"
        response = requests.put(
            UPDATE_PASSWORD_URL,
            headers=headers,
            json=payload,
            verify=False,
            timeout=20,
        )
    else:
        response = requests.put(
            UPDATE_PASSWORD_URL,
            headers=headers,
            json=payload,
            verify=False,
            timeout=20,
        )

    try:
        assert response.status_code == expected_status, (
            f"[{case['name']}] Expected {expected_status}, "
            f"got {response.status_code}. Response: {response.text}"
        )
    finally:
        # Teardown: If we successfully changed the password, change it back
        if response.status_code == 200 and include_auth and "newPassword" in payload:
            new_pwd = payload["newPassword"]
            if new_pwd != "Aravind@123":
                 print(f"Resetting password from {new_pwd}...")
                 reset_password(new_pwd, "Aravind@123")

