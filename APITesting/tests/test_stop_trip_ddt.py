import os
import json
import pytest
import requests
from utils.api_client import api_request

# … other imports …

def load_ddt_cases(filename: str):
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent_dir, "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

DDT_CASES = load_ddt_cases("stop_trip_ddt.json")



# Base URL for stop-trip API
STOP_TRIP_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/trip/aravind.m@gndsolutions.in/thinxfresh/stop-trip"
)


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])

def test_stop_trip_ddt(case):

    """
    Data-driven tests for the stop-trip API.

    JSON fields in each case:
      - name: identifier for the test
      - description: human readable
      - payload: request JSON body
      - include_auth: whether to send Authorization header
      - expected_status: expected HTTP status code
    """

    payload = case.get("payload", {})
    include_auth = case.get("include_auth", True)
    expected_status = case.get("expected_status", 200)

    headers = {"Content-Type": "application/json"}

    # ---- Perform request ----
    if include_auth:
        # Use shared api_request helper which:
        #  1) logs in
        #  2) attaches Bearer access token
        response = api_request(
            "POST",
            STOP_TRIP_URL,
            headers=headers,
            json=payload,
        )
    else:
        # No auth header on purpose (for negative tests)
        response = requests.post(
            STOP_TRIP_URL,
            headers=headers,
            json=payload,
            verify=False,
            timeout=20,
        )

    # ---- Status code assertion ----
    assert response.status_code == expected_status, (
        f"[{case['name']}] {case.get('description', '')} - "
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response body: {response.text}"
    )

    # For non-200 statuses, we won't enforce body structure
    if expected_status != 200:
        return

    # ---- Optional body checks for 200 responses ----
    # Your backend might return:
    #   - plain text: "deleted successfully"
    #   - or JSON: { "data": "deleted successfully" }
    #
    # We'll try to parse JSON, but not fail if it's plain text.
    try:
        body = response.json()
    except ValueError:
        body = None

    # If JSON, do a very light assertion
    if isinstance(body, dict):
        # If there is a "data" field, just ensure it is not empty
        if "data" in body:
            assert body["data"], f"[{case['name']}] 'data' field is empty"
