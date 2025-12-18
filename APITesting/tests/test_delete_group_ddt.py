import json
import pytest
import requests
from tests.test_auth import api_request

# Updated base URL with correct account/email
DELETE_GROUP_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/"
    "api/group/aravind.m@gndsolutions.in/thinxfresh/group/"
)

with open("data/delete_group_cases.json", "r") as f:
    DELETE_CASES = json.load(f)


@pytest.mark.parametrize("case", DELETE_CASES, ids=[c["name"] for c in DELETE_CASES])
def test_delete_group_ddt(case):
    params = {}
    if case.get("group_id") is not None:
        params["group_id"] = case["group_id"]

    if case.get("include_auth", True):
        response = api_request(
            method="DELETE",
            url=DELETE_GROUP_URL,
            params=params,
        )
    else:
        response = requests.delete(
            DELETE_GROUP_URL,
            params=params,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

    print("Status:", response.status_code)
    print("Body:", response.text)

    assert response.status_code == case["expected_status"], f"Unexpected status {response.status_code}"

    if case.get("expect_success_msg", False):
        assert "successfully" in response.text.lower(), "Expected success message missing"
