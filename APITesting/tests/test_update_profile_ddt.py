import json
import os
import pytest
import requests

BASE_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com"
UPDATE_PROFILE_URL = f"{BASE_URL}/api/profile/aravind.m@gndsolutions.in/thinxfresh/update-profile"


def load_test_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "update_profile_ddt.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


TEST_CASES = load_test_data()


import random
import string
import copy

@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_update_profile_ddt(case, auth_token):

    # deepcopy to avoid modifying the original test data across iterations
    payload = copy.deepcopy(case["payload"])
    
    # Handle Dynamic Data Generation
    if payload.get("name") == "DYNAMIC_NAME":
        random_suffix = ''.join(random.choices(string.ascii_uppercase, k=4))
        payload["name"] = f"Aravind{random_suffix}"
        
    if payload.get("phone") == "DYNAMIC_PHONE":
         # Generate random 10 digit number starting with 9
        random_digits = ''.join(random.choices(string.digits, k=9))
        payload["phone"] = f"9{random_digits}"

    headers = {"Content-Type": "application/json"}
    if case.get("include_auth", True):
        headers["Authorization"] = f"Bearer {auth_token}"

    response = requests.put(
        UPDATE_PROFILE_URL,
        json=payload,
        headers=headers,
        timeout=30,
        verify=False
    )

    print("Status:", response.status_code)
    print("Body:", response.text)

    expected = case["expected_status"]
    if isinstance(expected, list):
        assert response.status_code in expected, f"Expected one of {expected}, got {response.status_code}. Body: {response.text}"
    else:
        assert response.status_code == expected, f"Expected {expected}, got {response.status_code}. Body: {response.text}"
