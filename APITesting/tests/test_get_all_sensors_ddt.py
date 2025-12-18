import json
from pathlib import Path

import pytest
import requests

from tests.test_auth import api_request  # reuse your existing helper


# ---------- Local JSON loader (same style as other DDT tests) ----------

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename: str):
    """Load a JSON file from the data/ folder."""
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Test data ----------

DDT_CASES = load_json_file("get_all_sensors_ddt.json")

BASE_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com"
    "/api/sensor/aravind.m@gndsolutions.in/thinxfresh/view-all-sensors"
)


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_get_all_sensors_ddt(case):
    """
    DDT tests for:
    GET /api/sensor/{email}/thinxfresh/view-all-sensors?page=&per_page=
    """

    params = case.get("query_params", {}) or {}

    # With auth → use common api_request helper (adds Bearer token)
    if case.get("include_auth", True):
        response = api_request(
            method="GET",
            url=BASE_URL,
            params=params,
        )
    else:
        response = requests.get(
            BASE_URL,
            params=params,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

    print("Status:", response.status_code)
    print("Body:", response.text)

    assert response.status_code == case["expected_status"], \
        f"Unexpected status {response.status_code}"
