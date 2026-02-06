import requests
import json

def test_auth_flow():
    """Test the authentication flow."""
    base_url = "http://127.0.0.1:8000"

    print("Testing Authentication Flow...")

    # Test the auth verification endpoint (this is what the proxy uses)
    try:
        # This simulates what happens when the frontend calls /api/auth/verify
        verify_resp = requests.post(f"{base_url}/auth/verify",
                                   headers={"Authorization": "Bearer invalid_token"})
        print(f"Verify with invalid token: {verify_resp.status_code}")

        # Try without token
        verify_no_token = requests.post(f"{base_url}/auth/verify")
        print(f"Verify without token: {verify_no_token.status_code}")

    except Exception as e:
        print(f"Auth verification test failed: {e}")

    # Check the actual route structure
    try:
        # Test that the todos route exists at /api/todos (as per the todos.py router)
        print("\nExpected routes:")
        print("- /auth/verify (for auth verification)")
        print("- /api/todos/ (for todo operations)")
        print("- /chat/{user_id} (for chat operations)")

        # Test if we can reach the openapi spec
        openapi_resp = requests.get(f"{base_url}/openapi.json")
        print(f"\nOpenAPI spec: {openapi_resp.status_code}")

        if openapi_resp.ok:
            data = openapi_resp.json()
            paths = list(data.get('paths', {}).keys())
            print(f"Available paths ({len(paths)}):")
            for path in sorted(paths)[:10]:  # Show first 10 paths
                print(f"  {path}")

    except Exception as e:
        print(f"Route discovery failed: {e}")

if __name__ == "__main__":
    test_auth_flow()