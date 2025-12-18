import pytest
import json
import requests

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login"
AVAILABLE_SENSOR_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/sensor/aravind.m@gndsolutions.in/thinxfresh/available-sensor-group"

# ----------------------- LOGIN FUNCTION -----------------------
def get_token():
    payload = {
        "email": "aravind.m@gndsolutions.in",
        "password": "Admin@123"
    }
    response = requests.post(LOGIN_URL, json=payload, verify=False)
    print("LOGIN status:", response.status_code, "| body:", response.text)

    if response.status_code == 200:
        return response.json()["token"]["access"]
    else:
        return None

# ----------------------- LOAD JSON TEST DATA -----------------------
def load_cases():
    with open("data/available_sensor_group_cases.json", "r") as file:
        return json.load(file)

TEST_CASES = load_cases()


# ----------------------- EXECUTE TEST_CASES -----------------------
@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_available_sensor_group(case):
    headers = {"Content-Type": "application/json"}

    # Normal valid auth token
    if case.get("include_auth", True) and not case.get("invalid_token", False):
        token = get_token()
        headers["Authorization"] = f"Bearer {token}"

    # Invalid token intentionally
    if case.get("invalid_token", False):
        headers["Authorization"] = "Bearer INVALID_TOKEN"

    method = case.get("method", "GET")

    response = requests.request(
        method=method,
        url=AVAILABLE_SENSOR_URL,
        headers=headers,
        verify=False
    )

    print("Status:", response.status_code)
    print("Body:", response.text)

    assert response.status_code == case["expected_status"], f"Unexpected status {response.status_code}"

    # Validate correct response body for success
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list), "Expected a list response"
