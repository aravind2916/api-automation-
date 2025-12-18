import os
import json
import pytest
import requests

# Import the helper that always calls login API before making the request
from .test_auth import api_request

# Base URL for the completed trip API (without sensorId and name)
COMPLETED_TRIP_BASE_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/trip/aravind.m@gndsolutions.in/thinxfresh/completed"
)

# Path to your DDT JSON
DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "view_completed_trip_testdata.json"
)


def load_test_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


DDT_CASES = load_test_data()


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_view_completed_trip_ddt(case):
    """
    Data-driven tests for the 'view completed trip' API.

    JSON fields supported:

      Core:
        - sensor_id: path param (e.g. "TF60000052")
        - query_params: dict (includes "name": trip_name)
        - include_auth: bool
        - expected_status: int

      Data expectations:
        - expect_data: bool            # True if we expect non-empty data array
        - expect_empty_data: bool      # True if we expect empty data or no trip

      Validation flags (True/False):
        - validate_history: bool       # validate 'tripHistory'
        - validate_logs: bool          # validate 'tripLogs'
        - validate_alerts: bool        # validate 'alerts'
        - validate_avg_data: bool      # validate 'averagedData'

      Stronger requirements:
        - require_non_empty_history: bool
        - require_non_empty_logs: bool
        - require_non_empty_alerts: bool
    """

    sensor_id = case["sensor_id"]
    query_params = case.get("query_params", {})
    expected_status = case.get("expected_status", 200)
    include_auth = case.get("include_auth", True)

    expect_data = case.get("expect_data", False)
    expect_empty_data = case.get("expect_empty_data", False)

    validate_history = case.get("validate_history", False)
    validate_logs = case.get("validate_logs", False)
    validate_alerts = case.get("validate_alerts", False)
    validate_avg_data = case.get("validate_avg_data", False)

    require_non_empty_history = case.get("require_non_empty_history", False)
    require_non_empty_logs = case.get("require_non_empty_logs", False)
    require_non_empty_alerts = case.get("require_non_empty_alerts", False)

    # Build full URL with sensorId
    url = f"{COMPLETED_TRIP_BASE_URL}/{sensor_id}"

    # Common headers (we'll add Authorization only when include_auth is True)
    headers = {"Content-Type": "application/json"}

    # ---- Actual API call ----
    if include_auth:
        # Use api_request -> this will:
        #   1) call login API
        #   2) attach fresh Bearer token
        response = api_request(
            "GET",
            url,
            headers=headers,
            params=query_params,
        )
    else:
        # For missing_authorization test: NO auth header at all
        response = requests.get(
            url,
            headers=headers,
            params=query_params,
            verify=False,
            timeout=20,
        )

    # 1) HTTP status validation
    assert response.status_code == expected_status, (
        f"[{case['name']}] Expected status {expected_status}, "
        f"got {response.status_code}. Response: {response.text}"
    )

    # If we expect an error / empty body, don't try to parse JSON deeply
    if response.status_code >= 400:
        return

    # 2) Basic JSON structure
    body = response.json()

    # Some backends wrap everything under "data"
    assert "data" in body, f"[{case['name']}] 'data' key missing in response: {body}"
    data = body["data"]

    if expect_empty_data:
        # Usually either [] or missing/empty list
        assert isinstance(data, list) or isinstance(
            data, dict
        ), f"[{case['name']}] Unexpected 'data' type: {type(data)}"

        # Most of your completed trip API examples return a list with trip blocks
        if isinstance(data, list):
            assert len(data) == 0, (
                f"[{case['name']}] Expected empty data list, "
                f"got {len(data)} items: {data}"
            )
        return

    if expect_data:
        # For your real example, 'data' is a list with one element
        assert isinstance(data, list), (
            f"[{case['name']}] Expected 'data' to be a list, got {type(data)}"
        )
        assert len(data) > 0, f"[{case['name']}] Expected non-empty data list."

        trip_block = data[0]
        assert "tripDetails" in trip_block, (
            f"[{case['name']}] 'tripDetails' missing in first data element"
        )

        trip_details = trip_block["tripDetails"]
        # Basic sanity on tripDetails
        for field in ["tripname", "tripId", "sensorId", "source", "destination"]:
            assert field in trip_details, (
                f"[{case['name']}] tripDetails missing '{field}' field"
            )

        # 3) Optional deep validations

        # 3.a) Trip history
        if validate_history:
            assert "tripHistory" in trip_block, (
                f"[{case['name']}] 'tripHistory' missing in response"
            )
            history = trip_block["tripHistory"]
            assert isinstance(history, list), (
                f"[{case['name']}] tripHistory is not a list"
            )
            if require_non_empty_history:
                assert len(history) > 0, (
                    f"[{case['name']}] tripHistory should not be empty"
                )

            # Example: timestamps ascending
            timestamps = [h["timestamp"] for h in history if "timestamp" in h]
            assert timestamps == sorted(timestamps), (
                f"[{case['name']}] tripHistory timestamps are not ascending"
            )

        # 3.b) Trip logs
        if validate_logs:
            assert "tripLogs" in trip_block, (
                f"[{case['name']}] 'tripLogs' missing in response"
            )
            logs = trip_block["tripLogs"]
            assert isinstance(logs, list), (
                f"[{case['name']}] tripLogs is not a list"
            )
            if require_non_empty_logs:
                assert len(logs) > 0, (
                    f"[{case['name']}] tripLogs should not be empty"
                )

            # Example: battery 0..100 and movement 0/1
            for entry in logs:
                if "battery" in entry:
                    assert 0 <= entry["battery"] <= 100, (
                        f"[{case['name']}] battery out of range: {entry['battery']}"
                    )
                if "movement" in entry:
                    assert entry["movement"] in (0, 1), (
                        f"[{case['name']}] invalid movement value: {entry['movement']}"
                    )

        # 3.c) Alerts structure
        if validate_alerts:
            assert "alerts" in trip_block, (
                f"[{case['name']}] 'alerts' missing in response"
            )
            alerts = trip_block["alerts"]
            assert "pages" in alerts and "data" in alerts, (
                f"[{case['name']}] alerts missing 'pages' or 'data'"
            )
            if require_non_empty_alerts:
                assert len(alerts["data"]) > 0, (
                    f"[{case['name']}] alerts.data should not be empty"
                )

            for alert in alerts["data"]:
                # Each alert must have temperature, humidity, payload
                for key in ["temperature", "humidity", "payload"]:
                    assert key in alert, (
                        f"[{case['name']}] alert missing '{key}' field: {alert}"
                    )

        # 3.d) Averaged data
        if validate_avg_data:
            assert "averagedData" in trip_block, (
                f"[{case['name']}] 'averagedData' missing in response"
            )
            avg_list = trip_block["averagedData"]
            assert isinstance(avg_list, list), (
                f"[{case['name']}] averagedData is not a list"
            )
            for entry in avg_list:
                for key in ["temperature", "humidity", "latitude", "longitude", "timestamp"]:
                    assert key in entry, (
                        f"[{case['name']}] averagedData entry missing '{key}': {entry}"
                    )
