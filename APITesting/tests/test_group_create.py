import pytest
import time
import json
from utils import config
from utils.data_loader import load_test_data
from jsonschema import validate


# ============================================================
# 🔹 Load test data dynamically
# ============================================================
test_cases = load_test_data("testdata_group_create.json")


# ============================================================
# 🔹 Helper: Bearer token formatter
# ============================================================
def get_bearer_token(auth_token):
    """Return properly formatted Bearer header string."""
    if isinstance(auth_token, dict) and "access" in auth_token and "refresh" in auth_token:
        return f"Bearer {json.dumps(auth_token)}"
    elif "token" in auth_token and "access" in auth_token["token"]:
        return f"Bearer {json.dumps(auth_token['token'])}"
    else:
        raise ValueError("Invalid auth_token structure for Bearer header.")


# ============================================================
# 🔹 Parametrized Test: Create Group API
# ============================================================
@pytest.mark.parametrize("case", test_cases)
def test_create_group_api(api_client, auth_token, case):
    """Data-driven testing for Create Group POST API"""
    print(f"\n🔹 Running: {case['description']}")

    # Build URL
    url = f"{config.BASE_API_URL}{case['endpoint'].format(email=config.EMAIL)}"

    # Handle authorization
    auth_type = case.get("auth_type", "valid")
    if auth_type == "valid":
        headers = {"Authorization": get_bearer_token(auth_token), "Content-Type": "application/json"}
    elif auth_type == "invalid":
        invalid_token = {"access": "invalid", "refresh": "invalid"}
        headers = {"Authorization": f"Bearer {json.dumps(invalid_token)}", "Content-Type": "application/json"}
    else:  # No authorization
        headers = {"Content-Type": "application/json"}

    # Prepare request body
    payload = case.get("payload", {})
    response = None

    # Handle raw_body for malformed JSON case
    start = time.time()
    if "raw_body" in case:
        response = api_client.post(url, headers=headers, data=case["raw_body"], verify=False)
    else:
        response = api_client.post(url, headers=headers, json=payload, verify=False)
    duration = time.time() - start

    print(f"Status: {response.status_code} | Time: {duration:.2f}s")
    print("Response:", response.text[:400])

    # ✅ Expected status validation
    if "expected_status_list" in case:
        assert response.status_code in case["expected_status_list"], (
            f"Expected one of {case['expected_status_list']}, got {response.status_code}"
        )
    else:
        assert response.status_code == case["expected_status"], (
            f"Expected {case['expected_status']}, got {response.status_code}"
        )

    # Stop here for failed/invalid cases
    if response.status_code != 201:
        return

    # ✅ Parse JSON safely
    try:
        data = response.json()
    except json.JSONDecodeError:
        pytest.fail("Response is not valid JSON")

    # ✅ Validate top-level response structure
    for key in case.get("validate_response_keys", []):
        assert key in data, f"Missing key in response: {key}"

    # ✅ Check success message
    if "expected_message" in case:
        assert data.get("message") == case["expected_message"], (
            f"Expected message '{case['expected_message']}', got '{data.get('message')}'"
        )

    # ✅ Validate group object schema
    if "group" in data:
        group_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string"},
                "is_deleted": {"type": "boolean"},
                "solution": {"type": "string"},
                "registered_by": {"type": "string"},
                "_id": {"type": "string"}
            },
            "required": ["name", "description", "status", "solution"]
        }
        validate(instance=data["group"], schema=group_schema)

    # ✅ Performance check
    if case.get("check_performance"):
        max_duration = case.get("max_duration", 2)
        assert duration < max_duration, f"Response took {duration:.2f}s (> {max_duration}s)"
