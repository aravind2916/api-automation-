import pytest
import json
from tests.test_auth import api_request

VIEW_GROUP_BASE_URL = "https://nwsu54wyhc.execute-api.ap-south-1.amazonaws.com/api/group/aravind.m%40gndsolutions.in/thinxfresh/group"
import os

def load_test_cases(filename):
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent_dir, "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TEST_CASES = load_test_cases("view_group_ddt.json")



@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])

def test_view_group_ddt(case):
    url = f"{VIEW_GROUP_BASE_URL}/{case['group_id']}"
    response = api_request("GET", url, params=case["query_params"])

    print("API Response Status:", response.status_code)
    print("API Response Body:", response.text)

    assert response.status_code == case["expected_status"]
