import json
import os
import pytest
import requests

# Base URL without sensorId and query params
VIEW_ONGOING_BASE_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/trip/aravind.m@gndsolutions.in/thinxfresh/ongoing"
)


def load_test_data():
    """
    Load DDT JSON test cases for 'view ongoing trip' API.
    """
    current_dir = os.path.dirname(__file__)      # .../APITesting/tests
    project_root = os.path.dirname(current_dir)  # .../APITesting
    data_file_path = os.path.join(
        project_root, "data", "view_ongoing_trip_testdata.json"
    )

    with open(data_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


DDT_CASES = load_test_data()


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_view_ongoing_trip_ddt(case, auth_token):
    """
    Data-driven tests for the 'view ongoing trip' API.

    JSON fields:
      - sensor_id: path param
      - query_params: dict containing 'name'
      - include_auth: bool
      - expected_status: int
      - expect_data: bool (expect at least one item in data[])
      - expect_empty_data: bool (expect data[] to be empty)
      - validate_history: bool (validate tripHistory structure)
      - validate_logs: bool (validate tripLogs structure)
      - require_non_empty_history: bool
      - require_non_empty_logs: bool
      - check_current_config_range: bool (check temp/humidity within config range)
    """

    sensor_id = case["sensor_id"]
    query_params = case.get("query_params", {})
    expected_status = case.get("expected_status", 200)
    include_auth = case.get("include_auth", True)
    expect_data = case.get("expect_data", False)
    expect_empty_data = case.get("expect_empty_data", False)
    validate_history = case.get("validate_history", False)
    validate_logs = case.get("validate_logs", False)
    require_non_empty_history = case.get("require_non_empty_history", False)
    require_non_empty_logs = case.get("require_non_empty_logs", False)
    check_current_config_range = case.get("check_current_config_range", False)

    # Build full URL with sensorId
    url = f"{VIEW_ONGOING_BASE_URL}/{sensor_id}/"

    # Headers
    headers = {"Content-Type": "application/json"}
    if include_auth:
        headers["Authorization"] = f"Bearer {auth_token}"

    response = requests.get(
        url,
        headers=headers,
        params=query_params,
        verify=False,  # adjust if you want TLS verify
        timeout=20,
    )

    # 1) HTTP status check
    assert response.status_code == expected_status, (
        f"[{case['name']}] Expected status {expected_status}, "
        f"got {response.status_code}. Response body: {response.text}"
    )

    # For non-200 statuses, we don't enforce body structure
    if expected_status != 200:
        return

    # 2) Parse JSON
    try:
        body = response.json()
    except ValueError:
        pytest.fail(f"[{case['name']}] Response is not valid JSON: {response.text}")

    # Validate top-level keys
    for key in ["data", "tripHistory", "tripLogs", "failed_shadow_devices", "sensor_config"]:
        assert key in body, f"[{case['name']}] '{key}' key missing in response"

    data_items = body.get("data")
    trip_history = body.get("tripHistory")
    trip_logs = body.get("tripLogs")

    # Basic type checks
    assert isinstance(data_items, list), f"[{case['name']}] 'data' must be a list"
    assert isinstance(trip_history, list), f"[{case['name']}] 'tripHistory' must be a list"
    assert isinstance(trip_logs, list), f"[{case['name']}] 'tripLogs' must be a list"

    # 3) Expectations about data[]
    if expect_empty_data:
        assert len(data_items) == 0, (
            f"[{case['name']}] Expected empty 'data', got {len(data_items)} items"
        )
        return

    if expect_data:
        assert len(data_items) > 0, f"[{case['name']}] Expected at least one item in 'data', got 0"

    # If no items and no explicit expectation, nothing more to validate
    if not data_items:
        return

    query_name = query_params.get("name")

    # 4) Validate each trip header item
    for idx, item in enumerate(data_items):
        prefix = f"[{case['name']}] data[{idx}]"
        for field in [
            "tripName",
            "sensorId",
            "tripId",
            "tripStartedDate",
            "source",
            "destination",
            "configuration_params",
            "temperature",
            "humidity",
            "currentLocation",
            "battery",
            "movement",
            "last_update",
        ]:
            assert field in item, f"{prefix} missing '{field}'"

        # Sensor ID consistency
        assert item["sensorId"] == sensor_id, (
            f"{prefix} sensorId mismatch: expected '{sensor_id}', got '{item['sensorId']}'"
        )

        # Trip name consistency if provided
        if query_name is not None and isinstance(query_name, str):
            assert item["tripName"] == query_name, (
                f"{prefix} tripName mismatch: expected '{query_name}', got '{item['tripName']}'"
            )

        # Config structure
        cfg = item["configuration_params"]
        assert "temperature" in cfg and "humidity" in cfg, (
            f"{prefix} configuration_params must contain 'temperature' and 'humidity'"
        )

        # Simple location validation
        loc = item["currentLocation"]
        assert "latitude" in loc and "longitude" in loc, (
            f"{prefix} 'currentLocation' missing latitude/longitude"
        )

        # Optional range check for current temperature/humidity wrt config
        if check_current_config_range:
            temp_cfg = cfg.get("temperature", {})
            hum_cfg = cfg.get("humidity", {})
            t_min = temp_cfg.get("min")
            t_max = temp_cfg.get("max")
            h_min = hum_cfg.get("min")
            h_max = hum_cfg.get("max")

            current_temp = item.get("temperature")
            current_hum = item.get("humidity")

            if isinstance(current_temp, (int, float)) and isinstance(t_min, (int, float)) and isinstance(t_max, (int, float)):
                assert t_min <= current_temp <= t_max, (
                    f"{prefix} temperature {current_temp} not within config [{t_min}, {t_max}]"
                )

            if isinstance(current_hum, (int, float)) and isinstance(h_min, (int, float)) and isinstance(h_max, (int, float)):
                assert h_min <= current_hum <= h_max, (
                    f"{prefix} humidity {current_hum} not within config [{h_min}, {h_max}]"
                )

    # 5) Validate tripHistory structure if requested
    if validate_history:
        if require_non_empty_history:
            assert len(trip_history) > 0, (
                f"[{case['name']}] Expected non-empty 'tripHistory', got 0 items"
            )

        if trip_history:
            last_ts = None
            for idx, h in enumerate(trip_history):
                prefix = f"[{case['name']}] tripHistory[{idx}]"
                for field in [
                    "trip",
                    "temperature",
                    "humidity",
                    "latitude",
                    "longitude",
                    "movement",
                    "battery",
                    "power",
                    "loc_from",
                    "timestamp",
                ]:
                    assert field in h, f"{prefix} missing '{field}'"

                ts = h["timestamp"]
                if isinstance(ts, int) and last_ts is not None:
                    assert ts >= last_ts, (
                        f"{prefix} timestamps not sorted ascending: {ts} < {last_ts}"
                    )
                last_ts = ts

    # 6) Validate tripLogs structure if requested
    if validate_logs:
        if require_non_empty_logs:
            assert len(trip_logs) > 0, (
                f"[{case['name']}] Expected non-empty 'tripLogs', got 0 items"
            )

        if trip_logs:
            last_ts = None
            for idx, log in enumerate(trip_logs):
                prefix = f"[{case['name']}] tripLogs[{idx}]"
                for field in [
                    "trip",
                    "temperature",
                    "humidity",
                    "latitude",
                    "longitude",
                    "movement",
                    "battery",
                    "power",
                    "loc_from",
                    "timestamp",
                ]:
                    assert field in log, f"{prefix} missing '{field}'"

                ts = log["timestamp"]
                if isinstance(ts, int) and last_ts is not None:
                    assert ts >= last_ts, (
                        f"{prefix} log timestamps not sorted ascending: {ts} < {last_ts}"
                    )
                last_ts = ts
