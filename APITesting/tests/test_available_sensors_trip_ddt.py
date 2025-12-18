import pytest
import json
import os
import requests
import urllib3
from utils.auth_token import get_token

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AVAILABLE_TRIP_SENSOR_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/sensor/aravind.m@gndsolutions.in/thinxfresh/available-sensors-trip"
)

def load_test_cases(filename):
    # load data from ../data folder
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent_dir, "data", filename)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TEST_CASES = load_test_cases("available_sensors_trip_cases.json")

@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_available_sensors_trip(case):
    headers = {"Content-Type": "application/json"}

    if case.get("include_auth", True):
        token = get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            # Login failed → you can log a warning, but still hit the API
            print("WARNING: Login failed, proceeding without Authorization header")

    response = requests.get(
        AVAILABLE_TRIP_SENSOR_URL,
        headers=headers,
        verify=False
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    assert response.status_code == case["expected_status"]
