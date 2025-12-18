import os
import json
import pytest
import requests
from utils.api_client import api_request

# … any other imports you already had …

def load_ddt_cases(filename: str):
    parent_dir = os.path.dirname(os.path.dirname(__file__))  # go up from tests/
    path = os.path.join(parent_dir, "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

DDT_CASES = load_ddt_cases("delete_trip_ddt.json")




# Base URL for delete-trip API
DELETE_TRIP_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/trip/aravind.m@gndsolutions.in/thinxfresh/delete-trip"
)
@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])


def test_delete_trip_ddt(case):
    """
    Data-driven tests for the delete-trip API.

    JSON fields in each case:

      - name: identifier for the test
      - description: human readable description
      - query_params: query params dict (must include trip_id for valid cases)
      - include_auth: whether to send Bearer token
      - expected_status: expected HTTP status code
      - validate_message: if True, check "message" in response
      - expected_message: optional exact message to compare with
    """

    query_params = case.get("query_params", {})
    include_auth = case.get("include_auth", True)
    expected_status = case.get("expected_status", 200)
    validate_message = case.get("validate_message", False)
    expected_message = case.get("expected_message")

    headers = {"Content-Type": "application/json"}

    # ---- Make request ----
    if include_auth:
        # use api_request -> this will:
        #   1) login
        #   2) attach fresh Bearer token
        response = api_request(
            "DELETE",
            DELETE_TRIP_URL,
            headers=headers,
            params=query_params,
        )
    else:
        # No Authorization header
        response = requests.delete(
            DELETE_TRIP_URL,
            headers=headers,
            params=query_params,
            verify=False,
            timeout=20,
        )

    # 1) HTTP status check
    assert response.status_code == expected_status, (
        f"[{case['name']}] Expected status {expected_status}, "
        f"got {response.status_code}. Response body: {response.text}"
    )

    # For non-200 statuses or when we don't want to validate message, we're done
    if response.status_code != 200 or not validate_message:
        return

    # 2) Validate JSON body & message
    try:
        body = response.json()
    except ValueError:
        pytest.fail(f"[{case['name']}] Response is not valid JSON: {response.text}")

    assert "message" in body, f"[{case['name']}] 'message' key missing in response"

    if expected_message is not None:
        assert body["message"] == expected_message, (
            f"[{case['name']}] Expected message '{expected_message}', "
            f"got '{body['message']}'"
        )
