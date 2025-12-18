import os
import json
import pytest
import requests

from tests.test_auth import api_request  # your existing helper

# Base URL WITHOUT query string
COMPLETED_TRIPS_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com"
    "/api/trip/aravind.m@gndsolutions.in/thinxfresh/completed-trips"
)

# Build absolute path to ../data/completed_trips_ddt.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "data", "completed_trips_ddt.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    DDT_CASES = json.load(f)


def validate_pages(case_name: str, pages: dict) -> None:
    required = ["currentPage", "totalPages", "totalItems", "itemsPerPage"]
    for key in required:
        assert key in pages, f"[{case_name}] pages.{key} missing"

    assert isinstance(pages["currentPage"], int), f"[{case_name}] currentPage must be int"
    assert isinstance(pages["totalPages"], int), f"[{case_name}] totalPages must be int"
    assert isinstance(pages["totalItems"], int), f"[{case_name}] totalItems must be int"
    assert isinstance(pages["itemsPerPage"], int), f"[{case_name}] itemsPerPage must be int"

    assert pages["currentPage"] >= 1, f"[{case_name}] currentPage must be >= 1"
    assert pages["totalPages"] >= 0, f"[{case_name}] totalPages must be >= 0"
    assert pages["itemsPerPage"] > 0, f"[{case_name}] itemsPerPage must be > 0"


def validate_trip_item(case_name: str, item: dict) -> None:
    prefix = f"[{case_name}] item"

    for key in [
        "tripName",
        "sensorId",
        "tripEndedDate",
        "tripStartedDate",
        "temperature",
        "tripId",
        "totalAlert",
        "location_local",
    ]:
        assert key in item, f"{prefix} missing '{key}'"

    assert isinstance(item["tripName"], str), f"{prefix} tripName must be string"
    assert isinstance(item["sensorId"], str), f"{prefix} sensorId must be string"
    assert isinstance(item["tripId"], str), f"{prefix} tripId must be string"
    assert isinstance(item["tripEndedDate"], int), f"{prefix} tripEndedDate must be int"
    assert isinstance(item["tripStartedDate"], int), f"{prefix} tripStartedDate must be int"
    assert isinstance(item["totalAlert"], int), f"{prefix} totalAlert must be int"

    # basic sanity: ended >= started
    assert item["tripEndedDate"] >= item["tripStartedDate"], (
        f"{prefix} tripEndedDate < tripStartedDate"
    )

    temp_obj = item["temperature"]
    assert isinstance(temp_obj, dict), f"{prefix} temperature must be object"
    assert "min" in temp_obj and "max" in temp_obj, f"{prefix} temperature must have min/max"

    loc = item["location_local"]
    assert isinstance(loc, dict), f"{prefix} location_local must be object"
    for key in ["created", "started", "ended"]:
        assert key in loc, f"{prefix} location_local.{key} missing"
        block = loc[key]
        assert isinstance(block, dict), f"{prefix} location_local.{key} must be object"
        for sub in ["timezone", "epoch_sec", "local"]:
            assert sub in block, f"{prefix} location_local.{key}.{sub} missing"


def validate_sorted_items(case_name: str, items, field: str, order: str) -> None:
    # empty or single element is trivially sorted
    if len(items) < 2:
        return

    values = [item[field] for item in items]
    sorted_values = sorted(values, reverse=(order == "desc"))
    assert values == sorted_values, (
        f"[{case_name}] items not sorted by {field} {order}. "
        f"Got sequence: {values}"
    )


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_get_completed_trips_ddt(case):
    query_params = case.get("query_params", {})
    include_auth = case.get("include_auth", True)
    expected_status = case.get("expected_status", 200)

    headers = {"Content-Type": "application/json"}

    # ---- Request ----
    if include_auth:
        response = api_request(
            "GET",
            COMPLETED_TRIPS_URL,
            headers=headers,
            params=query_params,
        )
    else:
        response = requests.get(
            COMPLETED_TRIPS_URL,
            headers=headers,
            params=query_params,
            verify=False,
            timeout=20,
        )

    assert response.status_code == expected_status, (
        f"[{case['name']}] Expected status {expected_status}, "
        f"got {response.status_code}. Response: {response.text}"
    )

    # If not 200, don’t check body structure
    if expected_status != 200:
        return

    # ---- Parse JSON ----
    try:
        body = response.json()
    except ValueError:
        pytest.fail(f"[{case['name']}] Response is not valid JSON: {response.text}")

    assert "data" in body, f"[{case['name']}] 'data' key missing in response"
    data = body["data"]

    assert "pages" in data, f"[{case['name']}] 'pages' key missing in data"
    assert "items" in data, f"[{case['name']}] 'items' key missing in data"

    pages = data["pages"]
    items = data["items"]
    assert isinstance(items, list), f"[{case['name']}] 'items' must be a list"

    # ---- Pagination validation ----
    if case.get("validate_pagination", False):
        validate_pages(case["name"], pages)

        # optional: per_page should limit list length
        per_page = query_params.get("per_page")
        if isinstance(per_page, int) and per_page > 0:
            assert len(items) <= per_page, (
                f"[{case['name']}] items length {len(items)} exceeds per_page {per_page}"
            )

    # ---- Items expectations ----
    if case.get("expect_empty_items", False):
        assert len(items) == 0, (
            f"[{case['name']}] Expected empty items list, got {len(items)}"
        )
        return

    if case.get("expect_items", False):
        assert len(items) > 0, f"[{case['name']}] Expected items, got 0"

    if not items:
        return

    # ---- Item structure ----
    if case.get("validate_item_structure", False):
        for item in items:
            validate_trip_item(case["name"], item)

    # ---- Sort validation ----
    if case.get("validate_sort", False):
        sort_field = case.get("sort_field", "tripEndedDate")
        sort_order = case.get("sort_order", "desc")
        validate_sorted_items(case["name"], items, sort_field, sort_order)
