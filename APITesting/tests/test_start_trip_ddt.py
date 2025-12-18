import json
import os
import pytest
import requests

START_TRIP_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/trip/aravind.m@gndsolutions.in/thinxfresh/start-trip"
)


def load_test_data():
    current_dir = os.path.dirname(__file__)  # .../APITesting/tests
    project_root = os.path.dirname(current_dir)
    data_file_path = os.path.join(project_root, "data", "start_trip_testdata.json")

    with open(data_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


DDT_CASES = load_test_data()


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_start_trip_ddt(case, auth_token):
    payload = case.get("payload", {})
    expected_status = case.get("expected_status")
    expected_message = case.get("expected_message")
    include_auth = case.get("include_auth", True)

    headers = {"Content-Type": "application/json"}

    if include_auth:
        headers["Authorization"] = f"Bearer {auth_token}"

    response = requests.post(START_TRIP_URL, json=payload, headers=headers)

    assert response.status_code == expected_status, (
        f"[{case['name']}] Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
    )

    if expected_message:
        body = response.json()
        assert body.get("data") == expected_message, (
            f"[{case['name']}] Expected message '{expected_message}', got '{body.get('data')}'"
        )
