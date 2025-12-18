import json
import os
import pytest
import requests

ONGOING_TRIPS_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/trip/aravind.m@gndsolutions.in/thinxfresh/ongoing-trips"
)


def load_test_data():
    """
    Load DDT JSON test cases for ongoing trips API.
    """
    current_dir = os.path.dirname(__file__)           # .../APITesting/tests
    project_root = os.path.dirname(current_dir)       # .../APITesting
    data_file_path = os.path.join(
        project_root, "data", "ongoing_trips_testdata.json"
    )

    with open(data_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


DDT_CASES = load_test_data()


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_get_ongoing_trips_ddt(case, auth_token):
    """
    Data-driven tests for 'get all ongoing trips' API.

    JSON fields used:
    - query_params: dict (order, per_page, page)
    - include_auth: bool
    - expected_status: int
    - validate_ongoing_items: bool
    - expect_items: bool
    - expect_empty: bool
    - check_per_page_limit: bool
    - check_order_desc: bool
    """

    query_params = case.get("query_params", {})
    expected_status = case.get("expected_status", 200)
    include_auth = case.get("include_auth", True)
    validate_ongoing_items = case.get("validate_ongoing_items", False)
    expect_items = case.get("expect_items", False)
    expect_empty = case.get("expect_empty", False)
    check_per_page_limit = case.get("check_per_page_limit", False)
    check_order_desc = case.get("check_order_desc", False)

    # Headers
    headers = {"Content-Type": "application/json"}
    if include_auth:
        headers["Authorization"] = f"Bearer {auth_token}"

    response = requests.get(
        ONGOING_TRIPS_URL,
        headers=headers,
        params=query_params,
        verify=False,   # adjust if you want SSL verification
        timeout=20,
    )

    # 1) HTTP status code check
    assert response.status_code == expected_status, (
        f"[{case['name']}] Expected status {expected_status}, "
        f"got {response.status_code}. Response body: {response.text}"
    )

    # For non-200 responses, just ensure it returned something and stop there
    if expected_status != 200:
        return

    # 2) Parse JSON
    try:
        body = response.json()
    except ValueError:
        pytest.fail(f"[{case['name']}] Response is not valid JSON: {response.text}")

    assert "data" in body, f"[{case['name']}] 'data' key missing in response"
    data = body["data"]

    # 3) Validate pages object
    pages = data.get("pages")
    assert isinstance(pages, dict), f"[{case['name']}] 'pages' must be an object"
    for key in ["currentPage", "totalPages", "totalItems", "itemsPerPage"]:
        assert key in pages, f"[{case['name']}] 'pages.{key}' missing in response"

    # 4) Validate items type
    items = data.get("items")
    assert isinstance(items, list), f"[{case['name']}] 'items' must be a list"

    # Expectations about emptiness / non-emptiness
    if expect_empty:
        assert len(items) == 0, (
            f"[{case['name']}] Expected no items, but got {len(items)}"
        )
        return

    if expect_items:
        assert len(items) > 0, f"[{case['name']}] Expected some items, but got 0"

    # 5) per_page limit check
    if check_per_page_limit:
        per_page = query_params.get("per_page")
        if isinstance(per_page, int) and per_page > 0:
            assert len(items) <= per_page, (
                f"[{case['name']}] Expected at most {per_page} items, got {len(items)}"
            )

    # If no items, nothing more to validate
    if not items:
        return

    # 6) Validate ongoing-specific fields
    if validate_ongoing_items:
        for idx, item in enumerate(items):
            prefix = f"[{case['name']}] item[{idx}]"
            for field in ["tripName", "sensorId", "status", "tripStarted", "tripEnded"]:
                assert field in item, f"{prefix} missing '{field}'"

            assert item["status"] == "ONGOING", f"{prefix} status is not 'ONGOING'"
            assert item["tripStarted"] is True, f"{prefix} tripStarted is not True"
            assert item["tripEnded"] is False, f"{prefix} tripEnded is not False"

            # Light location check
            assert "currentLocation" in item, f"{prefix} missing 'currentLocation'"
            loc = item["currentLocation"]
            assert "latitude" in loc and "longitude" in loc, (
                f"{prefix} 'currentLocation' missing latitude/longitude"
            )

    # 7) Optional: check order by tripStartedDate if requested
    if check_order_desc:
        timestamps = [
            it.get("tripStartedDate") for it in items if isinstance(it.get("tripStartedDate"), int)
        ]
        if len(timestamps) > 1:
            sorted_desc = sorted(timestamps, reverse=True)
            assert timestamps == sorted_desc, (
                f"[{case['name']}] trips are not in descending order by 'tripStartedDate'"
            )
