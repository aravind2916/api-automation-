import os
import json
import pytest
import requests
from utils.api_client import api_request

# … your other imports …

def load_ddt_cases(filename: str):
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent_dir, "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

DDT_CASES = load_ddt_cases("groups_list_ddt.json")


# Base URL for get-all-groups API
GROUPS_BASE_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/group/aravind.m@gndsolutions.in/thinxfresh/group"
)


def validate_pagination(case_name: str, pagination: dict, items: list):
    """Validate the pagination object against basic rules."""
    for key in ["page", "per_page", "total_result", "total_page"]:
        assert key in pagination, f"[{case_name}] '{key}' missing in pagination"

    page = pagination["page"]
    per_page = pagination["per_page"]
    total_result = pagination["total_result"]
    total_page = pagination["total_page"]

    assert isinstance(page, int), f"[{case_name}] 'page' must be int"
    assert isinstance(per_page, int), f"[{case_name}] 'per_page' must be int"
    assert isinstance(total_result, int), f"[{case_name}] 'total_result' must be int"
    assert isinstance(total_page, int), f"[{case_name}] 'total_page' must be int"

    # Basic sanity rules
    assert page >= 1, f"[{case_name}] page should be >= 1"
    assert per_page >= 1, f"[{case_name}] per_page should be >= 1"
    assert total_result >= 0, f"[{case_name}] total_result should be >= 0"
    assert total_page >= 1, f"[{case_name}] total_page should be >= 1"

    # Items length should not exceed per_page
    assert len(items) <= per_page, (
        f"[{case_name}] items length {len(items)} exceeds per_page {per_page}"
    )


def validate_group_item(case_name: str, item: dict):
    """Validate one group item structure."""
    required_fields = [
        "_id",
        "name",
        "description",
        "sort_index",
        "created_at",
        "solution",
        "parent",
        "user",
        "id",
    ]

    for field in required_fields:
        assert field in item, f"[{case_name}] field '{field}' missing in group item"

    # Basic type checks
    assert isinstance(item["_id"], str), f"[{case_name}] _id must be str"
    assert isinstance(item["id"], str), f"[{case_name}] id must be str"
    assert item["_id"] == item["id"], f"[{case_name}] _id and id must match"

    assert isinstance(item["name"], str) and item["name"], (
        f"[{case_name}] name must be non-empty string"
    )
    assert isinstance(item["description"], str), (
        f"[{case_name}] description must be string"
    )
    assert isinstance(item["sort_index"], int), (
        f"[{case_name}] sort_index must be int"
    )
    assert isinstance(item["created_at"], str), (
        f"[{case_name}] created_at must be ISO datetime string"
    )
    assert isinstance(item["solution"], str), f"[{case_name}] solution must be str"
    # For your specific solution
    assert item["solution"] == "thinxfresh", (
        f"[{case_name}] solution must be 'thinxfresh'"
    )

    # parent and user can be null or string – just check they exist (already done)


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_get_groups_ddt(case):
    """
    Data-driven tests for the 'get all groups' API.

    JSON fields in each case:
      - name: identifier for the test
      - description: human readable
      - query_params: dict of query params (page, per_page, etc.)
      - include_auth: bool (whether to send Authorization header)
      - expected_status: expected HTTP status code
      - expect_items: True if we expect non-empty items []
      - expect_empty_items: True if we expect items [] to be empty
      - validate_pagination: validate pagination structure
      - validate_item_structure: validate each group item structure
    """

    query_params = case.get("query_params", {})
    include_auth = case.get("include_auth", True)
    expected_status = case.get("expected_status", 200)

    expect_items = case.get("expect_items", False)
    expect_empty_items = case.get("expect_empty_items", False)
    validate_pagination_flag = case.get("validate_pagination", False)
    validate_item_structure_flag = case.get("validate_item_structure", False)

    headers = {"Content-Type": "application/json"}

    # ---- Request ----
    if include_auth:
        response = api_request(
            "GET",
            GROUPS_BASE_URL,
            headers=headers,
            params=query_params,
        )
    else:
        # No auth – direct call without Authorization header
        import requests

        response = requests.get(
            GROUPS_BASE_URL,
            headers=headers,
            params=query_params,
            verify=False,
            timeout=20,
        )

    # 1) Status code
    assert response.status_code == expected_status, (
        f"[{case['name']}] Expected status {expected_status}, "
        f"got {response.status_code}. Body: {response.text}"
    )

    # If not 200, we don't check body schema
    if expected_status != 200:
        return

    # 2) Parse JSON
    try:
        body = response.json()
    except ValueError:
        pytest.fail(f"[{case['name']}] Response is not valid JSON: {response.text}")

    # Top-level keys
    for key in ["pagination", "items", "current_page"]:
        assert key in body, f"[{case['name']}] '{key}' key missing in response"

    pagination = body["pagination"]
    items = body["items"]

    assert isinstance(pagination, dict), (
        f"[{case['name']}] 'pagination' must be an object"
    )
    assert isinstance(items, list), f"[{case['name']}] 'items' must be a list"

    # 3) Expectations about items[]
    if expect_empty_items:
        assert len(items) == 0, (
            f"[{case['name']}] Expected empty items, got {len(items)} items"
        )
    if expect_items:
        assert len(items) > 0, (
            f"[{case['name']}] Expected non-empty items, got 0"
        )

    # 4) Pagination validation
    if validate_pagination_flag:
        validate_pagination(case["name"], pagination, items)

        # current_page should match pagination.page
        assert body["current_page"] == pagination["page"], (
            f"[{case['name']}] current_page "
            f"{body['current_page']} does not match pagination.page "
            f"{pagination['page']}"
        )

    # 5) Group item validation
    if items and validate_item_structure_flag:
        for item in items:
            validate_group_item(case["name"], item)
