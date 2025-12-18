import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Login details from utils/api_client.py
LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"
LOGIN_PAYLOAD = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "isSuperAdmin": False,
    "password": "3a640839e1ccd43a2b13d53da9c99774d1913aa498ab97201ddc90c9a3e31b0c",
    "remember_me": True
}

# Target URL from tests/test_update_password_ddt.py
TARGET_URL = (
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/"
    "api/profile/aravind.m@gndsolutions.in/thinxfresh/update-password"
)

def get_tokens():
    print(f"Logging in to {LOGIN_URL}...")
    resp = requests.post(
        LOGIN_URL,
        json=LOGIN_PAYLOAD,
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} {resp.text}")
        return None, None
    
    data = resp.json()
    token_obj = data.get("token")
    access_token = token_obj.get("access") if token_obj else None
    
    return access_token, token_obj


def log(msg):
    print(msg)
    with open("debug_output.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def test_header(name, header_value):
    log(f"\nTesting Header Format: {name}")
    log(f"Value: {header_value[:50]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": header_value
    }
    
    try:
        # Empty json to trigger 400 (Bad Request) if auth works, or 401 if auth fails
        resp = requests.put(TARGET_URL, headers=headers, json={}, verify=False, timeout=10)
        log(f"Status: {resp.status_code}")
        log(f"Response: {resp.text}")
        return resp.status_code
    except Exception as e:
        log(f"Error: {e}")
        return -1

def main():
    with open("debug_output.txt", "w") as f:
        f.write("Starting Debug Session\n")

    access_token, token_obj = get_tokens()
    if not access_token:
        log("Failed to get tokens")
        return

    # Scenario 1: Bearer <token_string> (Standard)
    test_header("Standard Bearer", f"Bearer {access_token}")

    # Scenario 2: aBearer<json_object> (fixtures/auth.py style)
    test_header("aBearer JSON", f"aBearer{json.dumps(token_obj)}")

    # Scenario 3: Bearer <json_object>
    test_header("Bearer JSON", f"Bearer {json.dumps(token_obj)}")
    
    # Scenario 4: aBearer<token_string> (Old utils/api_client.py style)
    test_header("aBearer String", f"aBearer{access_token}")

if __name__ == "__main__":
    main()
