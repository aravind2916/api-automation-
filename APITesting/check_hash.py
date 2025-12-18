import hashlib

passwords = ["Aravind@123", "Aravind@1234", "Aravind@12345"]

print("Checking password hashes:\n")
for pwd in passwords:
    h = hashlib.sha256(pwd.encode()).hexdigest()
    print(f"Password: {pwd}")
    print(f"Hash: {h}")
    print()

# The hash from api_client.py
api_client_hash = "dfaa43cb4002f53d61e9a36b3353bd79820f42337a7adccdce69d04fc076"
print(f"Hash in api_client.py: {api_client_hash}")
print(f"Length: {len(api_client_hash)} chars")

# SHA256 should be 64 chars
aravind123_hash = hashlib.sha256("Aravind@123".encode()).hexdigest()
print(f"\nAravind@123 SHA256 hash: {aravind123_hash}")
print(f"Length: {len(aravind123_hash)} chars")
