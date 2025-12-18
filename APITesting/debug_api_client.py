from utils.api_client import get_token
import json

try:
    print("Attempting to get token from utils.api_client...")
    token_obj = get_token()
    print("Success!")
    print(json.dumps(token_obj, indent=2))
except Exception as e:
    print(f"Failed: {e}")
