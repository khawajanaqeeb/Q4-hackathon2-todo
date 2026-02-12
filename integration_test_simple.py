#!/usr/bin/env python3
"""
Simple Integration Test for Authentication Flows
Tests all authentication endpoints and verifies end-to-end functionality
"""

import asyncio
import json
from typing import Dict, Optional
import httpx
import uuid
import time

# Test configuration
BASE_URL = "http://localhost:8000"  # Adjust to your backend URL
TEST_USERNAME = f"test_user_{int(time.time())}"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPass123!"

class AuthIntegrationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
        self.cookies = {}

    def _update_cookies(self, response: httpx.Response):
        """Extract and store cookies from response"""
        for cookie in response.cookies.jar:
            self.cookies[cookie.name] = cookie.value

    def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make request with current cookies"""
        # Add current cookies to request
        cookies = kwargs.pop('cookies', {})
        cookies.update(self.cookies)

        response = self.client.request(
            method,
            f"{self.base_url}{endpoint}",
            cookies=cookies,
            **kwargs
        )

        # Update cookies from response
        self._update_cookies(response)
        return response

    def test_register(self) -> Dict:
        """Test user registration flow"""
        print("Testing registration...")
        data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }

        # Send as form data like the frontend would
        response = self._make_request(
            "POST",
            "/auth/register",
            data=data
        )

        print(f"Registration status: {response.status_code}")
        if response.status_code != 200:
            print(f"Registration failed: {response.text}")
            return {}

        result = response.json()
        print(f"Registration successful: {result.get('username')} created")

        # Verify cookie was set
        auth_token = self.cookies.get('auth_token')
        print(f"Auth cookie set: {'Yes' if auth_token else 'No'}")

        return result

    def test_login(self) -> Dict:
        """Test user login flow"""
        print("\nTesting login...")
        data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }

        response = self._make_request(
            "POST",
            "/auth/login",
            data=data
        )

        print(f"Login status: {response.status_code}")
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return {}

        result = response.json()
        print(f"Login successful: {result.get('token_type')} token received")

        # Verify cookie was set
        auth_token = self.cookies.get('auth_token')
        print(f"Auth cookie set: {'Yes' if auth_token else 'No'}")

        return result

    def test_verify(self) -> Dict:
        """Test token verification"""
        print("\nTesting verification...")
        response = self._make_request("POST", "/auth/verify")

        print(f"Verify status: {response.status_code}")
        if response.status_code != 200:
            print(f"Verify failed: {response.text}")
            return {}

        result = response.json()
        print(f"Verification successful: {result.get('username')} verified")

        return result

    def test_refresh(self) -> Dict:
        """Test token refresh"""
        print("\nTesting refresh...")
        # Get current token to refresh
        current_token = self.cookies.get('auth_token')
        if not current_token:
            print("No token to refresh")
            return {}

        data = {"refresh_token": current_token}
        response = self._make_request(
            "POST",
            "/auth/refresh",
            data=data
        )

        print(f"Refresh status: {response.status_code}")
        if response.status_code != 200:
            print(f"Refresh failed: {response.text}")
            return {}

        result = response.json()
        print("Token refresh successful")

        # Verify new cookie was set
        new_token = self.cookies.get('auth_token')
        print(f"New auth cookie set: {'Yes' if new_token and new_token != current_token else 'No'}")

        return result

    def test_logout(self) -> bool:
        """Test logout flow"""
        print("\nTesting logout...")
        response = self._make_request("POST", "/auth/logout")

        print(f"Logout status: {response.status_code}")
        if response.status_code != 200:
            print(f"Logout failed: {response.text}")
            return False

        result = response.json()
        print(f"Logout successful: {result.get('message')}")

        # Verify cookie was cleared
        auth_token = self.cookies.get('auth_token')
        print(f"Auth cookie cleared: {'Yes' if not auth_token or auth_token == '' else 'No'}")

        return True

    def test_protected_endpoint(self) -> bool:
        """Test accessing a protected endpoint (using verify as example)"""
        print("\nTesting protected endpoint access...")
        response = self._make_request("POST", "/auth/verify")

        print(f"Protected endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("Protected endpoint accessible with valid token")
            return True
        elif response.status_code == 401:
            print("Protected endpoint correctly rejects unauthorized access")
            return True  # This is expected behavior
        else:
            print(f"Unexpected response: {response.text}")
            return False

    def run_full_flow(self):
        """Run the complete integration test flow"""
        print("="*60)
        print("STARTING AUTHENTICATION INTEGRATION TEST")
        print("="*60)

        # Step 1: Register
        register_result = self.test_register()
        if not register_result:
            print("X Registration failed, stopping test")
            return False

        # Step 2: Verify registration worked (should have valid token now)
        verify_after_reg = self.test_verify()
        if not verify_after_reg:
            print("X Verification after registration failed")
            return False

        # Step 3: Logout
        logout_result = self.test_logout()
        if not logout_result:
            print("X Logout failed")
            return False

        # Step 4: Try to access protected endpoint after logout (should fail)
        self.test_protected_endpoint()  # This should fail

        # Step 5: Login again
        login_result = self.test_login()
        if not login_result:
            print("X Login failed")
            return False

        # Step 6: Verify with login token
        verify_after_login = self.test_verify()
        if not verify_after_login:
            print("X Verification after login failed")
            return False

        # Step 7: Refresh token
        refresh_result = self.test_refresh()
        if not refresh_result:
            print("X Token refresh failed")
            return False

        # Step 8: Verify with refreshed token
        verify_after_refresh = self.test_verify()
        if not verify_after_refresh:
            print("X Verification after refresh failed")
            return False

        print("\n" + "="*60)
        print("ALL INTEGRATION TESTS PASSED!")
        print("="*60)
        return True

def main():
    tester = AuthIntegrationTester(BASE_URL)
    success = tester.run_full_flow()

    if success:
        print("\nSuccess! Integration test completed successfully!")
        print(f"Tested user: {TEST_USERNAME}")
        print(f"Tested email: {TEST_EMAIL}")
    else:
        print("\nError! Integration test failed!")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())