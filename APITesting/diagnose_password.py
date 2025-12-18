#!/usr/bin/env python3
"""
Comprehensive password diagnostic script.
Tests both Aravind@123 and Aravind@1234 with detailed output.
"""
import requests
import hashlib
import urllib3
import json

urllib3.disable_warnings()

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"
EMAIL = "aravind.m@gndsolutions.in"

def test_password(password_raw):
    """Test a single password and show detailed results."""
    print(f"\n{'='*60}")
    print(f"Testing Password: '{password_raw}'")
    print(f"{'='*60}")
    
    # Calculate hash
    pwd_hash = hashlib.sha256(password_raw.encode('utf-8')).hexdigest()
    print(f"SHA256 Hash: {pwd_hash}")
    
    # Build payload
    payload = {
        "email": EMAIL,
        "authMethod": "PASSWORD",
        "password": pwd_hash,
        "remember_me": True
    }
    
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    # Make request
    try:
        response = requests.post(
            LOGIN_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=10
        )
        
        print(f"\nHTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! This password works!")
            print(f"Response: {response.text[:200]}")
            return True
        else:
            print(f"❌ FAILED!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("="*60)
    print(" PASSWORD DIAGNOSTICS")
    print("="*60)
    print(f"Login URL: {LOGIN_URL}")
    print(f"Email: {EMAIL}")
    
    # Test both passwords
    passwords_to_test = [
        "Aravind@123",
        "Aravind@1234",
        # Also test with potential hidden characters
        "Aravind@123 ",  # trailing space
        " Aravind@123",  # leading space
        "Aravind@1234 ", # trailing space
        " Aravind@1234", # leading space
    ]
    
    success_count = 0
    for pwd in passwords_to_test:
        if test_password(pwd):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {success_count}/{len(passwords_to_test)} passwords worked")
    print(f"{'='*60}")
    
    if success_count == 0:
        print("\n⚠️  CRITICAL: None of the passwords worked!")
        print("\nPossible reasons:")
        print("1. Password was recently changed")
        print("2. Account is locked or disabled")
        print("3. Email address is incorrect")
        print("\nPlease verify:")
        print("- Can you log in via web UI with these credentials?")
        print("- Is the email 'aravind.m@gndsolutions.in' correct?")
        print("- Has the password been changed recently?")

if __name__ == "__main__":
    main()
