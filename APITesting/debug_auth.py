import requests
from utils.api_client import get_token, api_request, LOGIN_URL, LOGIN_PAYLOAD

print(f"Using Login URL: {LOGIN_URL}")
print(f"Using Login Payload: {LOGIN_PAYLOAD}")

try:
    token = get_token()
    print(f"Token obtained: {token[:20]}...")
except Exception as e:
    print(f"Failed to get token: {e}")
    exit(1)

# Try a simple authenticated request (e.g., to the update password URL or any other protected endpoint)
# We'll use the URL from the test file
UPDATE_PASSWORD_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/"
    "api/profile/aravind.m@gndsolutions.in/thinxfresh/update-password"
)

print(f"Testing URL: {UPDATE_PASSWORD_URL}")
headers = {"Content-Type": "application/json"}
# Just checking if we get 401 or something else. 400 is expected for empty payload, which means Auth passed.
try:
    response = api_request("PUT", UPDATE_PASSWORD_URL, headers=headers, json={})
    print(f"Response Status: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
