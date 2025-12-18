import requests
import hashlib
import urllib3

urllib3.disable_warnings()

url = "https://authentication.thinxview.com/api/auth/login/"
email = "aravind.m@gndsolutions.in"
pwd = "Aravind@123"

# Try different approaches
print("Testing different authentication methods:\n")

# Test 1: Plain password (no hash)
print("1. Plain password (no hash)")
resp = requests.post(url, json={"email": email, "authMethod": "PASSWORD", "password": pwd, "remember_me": True}, verify=False)
print(f"   Status: {resp.status_code}, Response: {resp.text[:80]}\n")

# Test 2: SHA256 hash
print("2. SHA256 hash")
pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
resp = requests.post(url, json={"email": email, "authMethod": "PASSWORD", "password": pwd_hash, "remember_me": True}, verify=False)
print(f"   Status: {resp.status_code}, Response: {resp.text[:80]}\n")

# Test 3: Different password Aravind@1234
print("3. Password: Aravind@1234 (SHA256)")
pwd2_hash = hashlib.sha256("Aravind@1234".encode()).hexdigest()
resp = requests.post(url, json={"email": email, "authMethod": "PASSWORD", "password": pwd2_hash, "remember_me": True}, verify=False)
print(f"   Status: {resp.status_code}, Response: {resp.text[:80]}\n")

# Test 4: Different password Aravind@1234 (plain)
print("4. Password: Aravind@1234 (plain)")
resp = requests.post(url, json={"email": email, "authMethod": "PASSWORD", "password": "Aravind@1234", "remember_me": True}, verify=False)
print(f"Status: {resp.status_code}, Response: {resp.text[:80]}\n")
