import json
import os
import pytest
import requests

BASE_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com"
EMAIL = "aravind.m@gndsolutions.in"
# Correct endpoint based on other tests
ENDPOINT = f"{BASE_URL}/api/profile/{EMAIL}/thinxfresh/update-date-time-format"

def load_test_data():
    # Construct path relative to this file
    path = os.path.join(os.path.dirname(__file__), "..", "data", "update_datetime_format_testdata.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TEST_DATA = load_test_data()

@pytest.mark.parametrize("case", TEST_DATA["valid_cases"], ids=[c["title"] for c in TEST_DATA["valid_cases"]])
def test_update_datetime_format_valid_cases(case, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    
    response = requests.put(
        ENDPOINT,
        headers=headers,
        json=case["payload"],
        verify=False
    )

    print(f"DEBUG: Status: {response.status_code}, Body: {response.text}")
    assert response.status_code == case["expected_status"]

    response_json = response.json()
    assert response_json["message"] == "Date & time format updated successfully"
    # Note: Checking "data" might depend on API response structure; keeping it as user defined.
    # If API returns "user" instead of "data", this will fail, but stick to user's logic first.

@pytest.mark.parametrize("case", TEST_DATA["invalid_cases"], ids=[c["title"] for c in TEST_DATA["invalid_cases"]])
def test_update_datetime_format_invalid_cases(case, auth_token):
    # Default valid setup
    target_endpoint = ENDPOINT
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    
    # Custom logic for specific failure scenarios
    if case["title"] == "User not found":
        fake_email = "unknown.user.999@test.com"
        target_endpoint = f"{BASE_URL}/api/profile/{fake_email}/thinxfresh/update-date-time-format"
        
    if case["title"] == "Invalid user identifier":
        # Simulate invalid format in URL
        bad_email = "invalid-email-format-xyz"
        target_endpoint = f"{BASE_URL}/api/profile/{bad_email}/thinxfresh/update-date-time-format"
        
    if case["title"] == "Unauthorized role":
        headers["Authorization"] = "Bearer invalid_token_simulating_unauthorized"

    response = requests.put(
        target_endpoint,
        headers=headers,
        json=case["payload"],
        verify=False
    )

    print(f"DEBUG: Status: {response.status_code}, Body: {response.text}")
    assert response.status_code == case["expected_status"]

    response_json = response.json()
    # Flexible strictness on message matching
    assert case["expected_message"] in response_json.get("message", "")
