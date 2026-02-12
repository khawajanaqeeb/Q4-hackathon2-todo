#!/usr/bin/env python3
"""
Quick test to verify chat endpoints work with the new auth system
"""

import httpx
import time

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = f"test_user_{int(time.time())}"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPass123!"

def test_chat_endpoints():
    print("Starting chat endpoints authentication test...")

    # Create a client with cookie support
    client = httpx.Client(timeout=30.0)

    # Step 1: Register a test user
    print("\n1. Registering test user...")
    register_resp = client.post(f"{BASE_URL}/auth/register", data={
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    if register_resp.status_code != 200:
        print(f"   X Registration failed: {register_resp.text}")
        return False

    print(f"   OK Registration successful")

    # Step 2: Try to access a chat endpoint without auth (should fail)
    print("\n2. Testing chat endpoint without authentication...")
    chat_resp = client.post(f"{BASE_URL}/chat/completions", json={
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "gpt-4"
    })

    print(f"   Chat endpoint without auth: {chat_resp.status_code}")
    if chat_resp.status_code == 401:
        print("   OK Correctly rejected unauthorized access")
    else:
        print(f"   ? Unexpected response: {chat_resp.status_code}")

    # Step 3: Login to get auth token
    print("\n3. Logging in to get authentication...")
    login_resp = client.post(f"{BASE_URL}/auth/login", data={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })

    if login_resp.status_code != 200:
        print(f"   X Login failed: {login_resp.text}")
        return False

    print("   OK Login successful")

    # Step 4: Try to access chat endpoint with auth (should succeed)
    print("\n4. Testing chat endpoint with authentication...")
    # The chat endpoint might not be fully implemented, so we expect various responses
    # but it should not return 401 if auth is working
    chat_resp_with_auth = client.post(f"{BASE_URL}/chat/completions", json={
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "gpt-4"
    })

    print(f"   Chat endpoint with auth: {chat_resp_with_auth.status_code}")
    if chat_resp_with_auth.status_code == 401:
        print("   X Still rejecting with valid auth - auth system broken")
        return False
    else:
        print("   OK Authenticated request processed (expected various responses)")

    # Step 5: Test another protected endpoint (like verify)
    print("\n5. Testing verify endpoint with authentication...")
    verify_resp = client.post(f"{BASE_URL}/auth/verify")

    if verify_resp.status_code == 200:
        print("   OK Verify endpoint working with auth")
    else:
        print(f"   X Verify endpoint failed: {verify_resp.status_code}")
        return False

    print("\nOK All chat endpoint authentication tests passed!")
    return True

if __name__ == "__main__":
    success = test_chat_endpoints()
    if success:
        print("\nSuccess! Chat endpoints authentication test completed successfully!")
    else:
        print("\nX Chat endpoints authentication test failed!")
        exit(1)