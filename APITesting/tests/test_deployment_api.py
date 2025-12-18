import pytest
import requests
import json
from utils.data_loader import load_test_data
from utils import config

BASE_URL = "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"


# ============================================================
#  SAME TOKEN FORMAT AS KPI TEST  (Fixes the 401 issue)
# ============================================================
def get_bearer_token(auth_token):
    """
    Convert auth token into JSON Bearer token (same format
    used in working KPI test cases).
    """
    return f"Bearer {json.dumps(auth_token)}"


# ============================================================
#  Load test data
# ============================================================
test_data = load_test_data("testdata_deployment.json")


# ============================================================
#  MAIN TEST FUNCTION
# ============================================================
@pytest.mark.parametrize("case", test_data, ids=[c["description"] for c in test_data])
def test_deployment_api(case, auth_token):
    """
    Deployment API tests using DDT + token from login (auth_token fixture).
    """

    email = case["email"]
    product = case["product"]
    method = case["method"]
    params = case.get("query_params") or {}
    desc = case["description"]

    # Start with any headers from JSON (for negative tests)
    headers = case.get("headers") or {}

    # =====================================================
    # Handle Authorization header based on test scenario
    # =====================================================
    if "Missing Authorization header" in desc:
        # Do NOT add any Authorization header
        pass

    elif "Invalid Authorization token" in desc:
        # Keep invalid header from JSON
        pass

    else:
        # ✅ Valid token (formatted same as KPI test)
        headers["Authorization"] = get_bearer_token(auth_token)

    # =====================================================
    # Build correct URL
    # =====================================================
    endpoint = f"api/dashboard/{email}/{product}/deployment"
    url = BASE_URL + endpoint

    # =====================================================
    # Make the HTTP request
    # =====================================================
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)

    elif method == "POST":
        response = requests.post(url, headers=headers, params=params)

    elif method == "PUT":
        response = requests.put(url, headers=headers, params=params)

    else:
        pytest.skip(f"Unsupported method: {method}")

    # =====================================================
    # Validate Response
    # =====================================================
    assert response.status_code == case["expected_status"], (
        f"FAILED: {desc} | "
        f"Expected {case['expected_status']} but got {response.status_code} | "
        f"URL={url}"
    )
