import json
import os
from pathlib import Path

import pytest
import requests

from tests.test_auth import api_request  # your existing helper


# ---- Local JSON loader (avoids utils.data_loader import issues) ----

BASE_DIR = Path(__file__).resolve().parent.parent  # project root (APITesting)
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename: str):
    """Load a JSON file from the data/ folder."""
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---- Test data ----

TEST_CASES = load_json_file("delete_sensor_group_ddt.json")

# Base URL without the group id
BASE_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com"
    "/api/group/aravind.m@gndsolutions.in/thinxfresh"
)


@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_delete_sensor_group_ddt(case):
    """
    DDT tests for:
    DELETE /api/group/{accountEmail}/thinxfresh/{group_id}/delete-sensor-group
    Body: { "device_ids": [ ... ] }
    """

    # Build URL based on presence of group_id
    if case.get("group_id") is None:
        # No group id in path → .../thinxfresh/delete-sensor-group
        url = f"{BASE_URL}/delete-sensor-group"
    else:
        url = f"{BASE_URL}/{case['group_id']}/delete-sensor-group"

    payload = case["payload"]

    # Send request with or without Authorization header
    if case.get("include_auth", True):
        response = api_request(
            method="DELETE",
            url=url,
            json=payload,
        )
    else:
        response = requests.delete(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

    print("Status:", response.status_code)
    print("Body:", response.text)

    assert response.status_code == case["expected_status"], \
        f"Unexpected status {response.status_code}"
