import json
import pytest
import requests

from tests.test_auth import api_request

UPDATE_GROUP_URL = (
    "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/"
    "api/group/aravind.m@gndsolutions.in/thinxfresh/group/"
)

with open("data/update_group_ddt.json", "r") as f:
    DDT_CASES = json.load(f)


@pytest.mark.parametrize("case", DDT_CASES, ids=[c["name"] for c in DDT_CASES])
def test_update_group_ddt(case):
    params = {}
    if case.get("group_id") is not None:
        params["group_id"] = case["group_id"]

    payload = case["payload"]

    # send request
    if case.get("include_auth", True):
        response = api_request(
            method="PUT",
            url=UPDATE_GROUP_URL,
            params=params,
            json=payload,
        )
    else:
        response = requests.put(
            UPDATE_GROUP_URL,
            params=params,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

    print("Status:", response.status_code)
    print("Body:", response.text)

    assert response.status_code == case["expected_status"], \
        f"Unexpected status {response.status_code}"

    if case.get("expect_success_msg", False) and response.status_code == 200:
        body = response.json()
        assert "msg" in body, "Missing msg in response"
        assert "updated" in body["msg"].lower(), "Success message incorrect"
