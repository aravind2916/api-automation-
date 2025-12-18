import requests
import hashlib
import urllib3

urllib3.disable_warnings()

url = "https://authentication.thinxview.com/api/auth/login/"
email = "aravind.m@gndsolutions.in"
pwd = "Aravind@123"

# Calculate the correct SHA256 hash
pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()

print(f"Testing login with:")
print(f"Email: {email}")
print(f"Password: {pwd}")
print(f"Hash: {pwd_hash}")
print()

payload = {
    "email": email,
    "authMethod": "PASSWORD",
    "password": pwd_hash,
    "remember_me": True
}

try:
    resp = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=30
    )
    
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
    
    if resp.status_code == 200:
        print("\n✅ SUCCESS! Authentication works!")
        token = resp.json().get("token")
        if token:
            print(f"Token received: {str(token)[:100]}...")
    else:
        print(f"\n❌ FAILED with status {resp.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
