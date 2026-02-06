import requests
import json

def test_todo_api():
    """Test the todo API endpoints directly."""
    base_url = "http://127.0.0.1:8000"

    print("Testing Todo API endpoints...")

    # Test health endpoint
    try:
        health_resp = requests.get(f"{base_url}/health")
        print(f"[OK] Health: {health_resp.status_code} - {health_resp.json()}")
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return

    # Test todos endpoint (without authentication - should return 401/403)
    try:
        todos_resp = requests.get(f"{base_url}/api/todos/")
        print(f"[OK] Todos (unauth): {todos_resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Todos endpoint failed: {e}")

    # Test creating a todo without auth (should fail)
    try:
        create_resp = requests.post(f"{base_url}/api/todos/",
                                 json={"title": "Test task"},
                                 headers={"Content-Type": "application/json"})
        print(f"[OK] Create todo (unauth): {create_resp.status_code}")

        # Print error details if there's an error
        if not create_resp.ok:
            try:
                error_data = create_resp.json()
                print(f"  Error details: {error_data}")
            except:
                print(f"  Error text: {create_resp.text}")

    except Exception as e:
        print(f"[ERROR] Create todo failed: {e}")

if __name__ == "__main__":
    test_todo_api()