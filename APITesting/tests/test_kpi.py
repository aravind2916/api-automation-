import pytest
import time
import json
from utils import config
from utils.data_loader import load_test_data
from jsonschema import validate

# ============================================================
# 🔹 Helper: Bearer token formatter
# ============================================================
def get_bearer_token(auth_token):
    if isinstance(auth_token, dict) and "access" in auth_token and "refresh" in auth_token:
        return f"Bearer {json.dumps(auth_token)}"
    elif "token" in auth_token and "access" in auth_token["token"]:
        return f"Bearer {json.dumps(auth_token['token'])}"
    else:
        raise ValueError("Invalid auth_token structure for Bearer header.")


# ============================================================
# 🔹 Load test data dynamically
# ============================================================
test_cases = load_test_data("testdata_kpi.json")


# ============================================================
# 🔹 DDT Test Function
# ============================================================
@pytest.mark.parametrize("case", test_cases)
def test_kpi_api(api_client, auth_token, case):
    """Data-driven KPI API validation"""
    print(f"\n🔹 Running: {case['description']}")

    url = f"{config.BASE_API_URL}{case['endpoint'].format(email=config.EMAIL)}"

    # Select auth type
    auth_type = case.get("auth_type", "valid")
    if auth_type == "valid":
        headers = {"Authorization": get_bearer_token(auth_token)}
    elif auth_type == "invalid":
        invalid_token = {"access": "invalid", "refresh": "invalid"}
        headers = {"Authorization": f"Bearer {json.dumps(invalid_token)}"}
    elif auth_type == "expired":
        expired_token = {"access": "expired_token", "refresh": "invalid"}
        headers = {"Authorization": f"Bearer {json.dumps(expired_token)}"}
    else:
        headers = {}

    # Request + timing
    start = time.time()
    response = api_client.get(url, headers=headers, verify=False)
    duration = time.time() - start

    print(f"Status: {response.status_code} | Time: {duration:.2f}s")

    # ✅ Validate expected status
    if "expected_status_list" in case:
        assert response.status_code in case["expected_status_list"], f"Expected {case['expected_status_list']}, got {response.status_code}"
    else:
        assert response.status_code == case["expected_status"], f"Expected {case['expected_status']}, got {response.status_code}"

    if response.status_code != 200:
        return

    # ✅ Parse response JSON
    data = response.json()

    # ✅ Schema validation
    if case.get("validate_schema"):
        schema = {
            "type": "object",
            "properties": {
                "total_trip_starting": {"type": "number"},
                "total_trip_ending": {"type": "number"},
                "trip_health": {"type": "object"},
                "totalSensors": {"type": "number"}
            },
            "required": ["trip_health", "total_trip_starting"]
        }
        validate(instance=data, schema=schema)

    # ✅ Check required keys
    if case.get("required_keys"):
        for key in case["required_keys"]:
            assert key in data, f"Missing key: {key}"

    # ✅ Subkey validation
    if case.get("required_subkeys"):
        for subkey in case["required_subkeys"]:
            assert subkey in data["trip_health"], f"Missing trip_health subkey: {subkey}"

    # ✅ Logical checks
    if case.get("logical_check") == "trip_health_consistency":
        trip_health = data["trip_health"]
        total_health = sum([
            trip_health.get("lowAlertTrips", 0),
            trip_health.get("moderateAlertTrips", 0),
            trip_health.get("highAlertTrips", 0)
        ])
        total_trips = data.get("total_trip_starting", 0)
        assert total_health <= total_trips, f"Trip health exceeds total trips ({total_health}>{total_trips})"

    if case.get("logical_check") == "non_negative_metrics":
        for key, value in data.items():
            if isinstance(value, (int, float)):
                assert value >= 0, f"Negative value found for {key}: {value}"

    # ✅ Performance check
    if case.get("check_performance"):
        max_dur = case.get("max_duration", 2)
        assert duration < max_dur, f"Response took {duration:.2f}s (> {max_dur}s)"
    # ✅ Additional logical checks
    if case.get("logical_check") == "alert_consistency":
        total_alert = data.get("total_alert_count", 0)
        sub_sum = data.get("humidity_alert_count", 0) + data.get("temperature_alert", 0)
        assert total_alert == sub_sum, f"Alert count mismatch: total={total_alert}, sum={sub_sum}"

    if case.get("logical_check") == "failed_shadow_devices_list":
        assert "failed_shadow_devices" in data, "Missing key: failed_shadow_devices"
        assert isinstance(data["failed_shadow_devices"], list), "failed_shadow_devices should be a list"

    if case.get("logical_check") == "trip_alert_balance":
        total_trips = data.get("total_trip_starting", 0)
        in_alert = data.get("trip_in_alert_count", 0)
        not_alert = data.get("trip_not_alert_count", 0)
        assert total_trips == in_alert + not_alert, f"Trip balance mismatch: total={total_trips}, in_alert={in_alert}, not_alert={not_alert}"

    if case.get("logical_check") == "sensor_allocation":
        total_sensors = data.get("totalSensors", 0)
        assigned = data.get("totalAssignedSensors", 0)
        assert total_sensors >= assigned, f"Invalid sensor allocation: {assigned} > {total_sensors}"

    if case.get("logical_check") == "no_negative_alerts":
        alert_keys = [k for k in data.keys() if "alert" in k]
        for key in alert_keys:
            assert data[key] >= 0, f"Negative alert value for {key}: {data[key]}"

    if case.get("logical_check") == "valid_json_structure":
        assert isinstance(data, dict), "Response is not valid JSON"
        assert "trip_health" in data, "Missing key: trip_health"
