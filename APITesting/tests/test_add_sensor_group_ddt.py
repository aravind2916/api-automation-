import json
import pytest
import requests
from tests.test_auth import api_request

# Load DDT data
with open("data/add_sensor_group_ddt.json", "r") as f:
    TEST_CASES = json.load(f)

BASE_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/group/aravind.m@gndsolutions.in/thinxfresh"

@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_add_sensor_group_ddt(case):
    if case.get("group_id") is None:
        url = f"{BASE_URL}/add-sensor-group"
    else:
        url = f"{BASE_URL}/{case['group_id']}/add-sensor-group"

    payload = case["payload"]

    if case.get("include_auth", True):
        response = api_request(
            method="POST",
            url=url,
            json=payload
        )
    else:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

    print("Status:", response.status_code)
    print("Body:", response.text)

    assert response.status_code == case["expected_status"], \
        f"Unexpected status {response.status_code}"
