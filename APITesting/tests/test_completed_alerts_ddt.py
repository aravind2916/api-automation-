import pytest
import json
import os
import requests
import urllib3
from utils.auth_token import get_token

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/alert/"
    "aravind.m@gndsolutions.in/thinxfresh/completed-alerts?order=asc&per_page=5&page=1"
)

def load_test_cases(filename):
    parent = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent, "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TEST_CASES = load_test_cases("completed_alerts_cases.json")


@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_completed_alerts(case):
    headers = {"Content-Type": "application/json"}

    if case.get("include_auth", True):
        token = get_token()
        if not token:
            pytest.skip("Login failed (no token), skipping authorized test case")
        headers["Authorization"] = f"Bearer {token}"

    url = BASE_URL
    if case.get("url_override"):
        url = (
            "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/alert/"
            "aravind.m@gndsolutions.in/thinxfresh/completed-alerts" + case["url_override"]
        )

    method = case.get("method", "GET")

    response = requests.request(method, url, headers=headers, verify=False)

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    assert response.status_code == case["expected_status"], (
        f"Expected {case['expected_status']} but got {response.status_code}"
    )

    if response.status_code == 200:
        body = response.json()
        assert "data" in body
        assert isinstance(body["data"], list)
