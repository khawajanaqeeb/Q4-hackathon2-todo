#!/usr/bin/env python3
"""
Simple test script to verify authentication endpoints work correctly.
"""
import requests
import time
import subprocess
import signal
import os
import sys

def test_auth_endpoints():
    """Test the authentication endpoints."""
    base_url = "http://localhost:3000/api/auth"
    
    print("Testing authentication endpoints...")
    
    # Test verify endpoint (should return 401 without token)
    try:
        response = requests.get(f"{base_url}/verify")
        print(f"Verify endpoint status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Verify endpoint correctly returns 401 without token")
        else:
            print(f"✗ Unexpected status for verify endpoint: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing verify endpoint: {e}")
    
    # Test login endpoint (should return 400 without credentials)
    try:
        response = requests.post(f"{base_url}/login", json={})
        print(f"Login endpoint status: {response.status_code}")
        if response.status_code in [400, 422]:  # 422 is validation error
            print("✓ Login endpoint correctly validates input")
        else:
            print(f"✗ Unexpected status for login endpoint: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing login endpoint: {e}")

if __name__ == "__main__":
    print("Running authentication test...")
    test_auth_endpoints()
    print("Test completed.")