import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://authentication.thinxview.com/api/auth/login/"

print("Testing with verify=True...")
try:
    requests.post(URL, verify=True, timeout=5)
    print("Success with verify=True")
except Exception as e:
    print(f"Failed with verify=True: {e}")

print("\nTesting with verify=False...")
try:
    requests.post(URL, verify=False, timeout=5)
    print("Success with verify=False")
except Exception as e:
    print(f"Failed with verify=False: {e}")
