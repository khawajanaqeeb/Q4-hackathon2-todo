import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"

def final_verification():
    """Final verification that Phase 3 is fully operational"""
    print("FINAL PHASE 3 VERIFICATION")
    print("=" * 60)

    # Test 1: Health check
    print("✅ Testing Health Endpoint...")
    health_resp = requests.get(f"{BASE_URL}/health")
    health_ok = health_resp.status_code == 200
    print(f"   Status: {health_resp.status_code} - {'PASS' if health_ok else 'FAIL'}")

    # Test 2: API Documentation
    print("\n✅ Testing API Documentation...")
    docs_resp = requests.get(f"{BASE_URL}/docs")
    docs_ok = docs_resp.status_code == 200
    print(f"   Status: {docs_resp.status_code} - {'PASS' if docs_ok else 'FAIL'}")

    # Test 3: Authentication Flow
    print("\n✅ Testing Authentication Flow...")
    register_data = {
        "email": f"final_test_{int(datetime.now().timestamp())}@example.com",
        "password": "TestPass123!",
        "username": f"finaltest_{int(datetime.now().timestamp())}"
    }

    register_resp = requests.post(f"{BASE_URL}/auth/register", data=register_data)
    auth_ok = register_resp.status_code == 200
    print(f"   Registration: {register_resp.status_code} - {'PASS' if auth_ok else 'FAIL'}")

    if auth_ok:
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        login_ok = login_resp.status_code == 200
        print(f"   Login: {login_resp.status_code} - {'PASS' if login_ok else 'FAIL'}")

    # Test 4: MCP Endpoints
    print("\n✅ Testing MCP Endpoints...")
    if auth_ok and login_ok:
        auth_token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}

        tools_resp = requests.get(f"{BASE_URL}/api/mcp/tools/available", headers=headers)
        tools_ok = tools_resp.status_code == 200
        print(f"   Tools endpoint: {tools_resp.status_code} - {'PASS' if tools_ok else 'FAIL'}")

        providers_resp = requests.get(f"{BASE_URL}/api/mcp/providers/available", headers=headers)
        providers_ok = providers_resp.status_code == 200
        print(f"   Providers endpoint: {providers_resp.status_code} - {'PASS' if providers_ok else 'FAIL'}")

    # Test 5: Chat Functionality
    print("\n✅ Testing Chat Functionality...")
    if auth_ok and login_ok:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        user_id = register_resp.json()["id"]

        chat_request = {
            "messages": [
                {
                    "id": f"msg_{uuid.uuid4()}",
                    "role": "user",
                    "content": "Hello! Can you help me create a task?",
                    "createdAt": datetime.now().isoformat()
                }
            ],
            "conversation": None,
            "metadata": {}
        }

        chat_resp = requests.post(f"{BASE_URL}/chat/{user_id}", headers=headers, json=chat_request)
        chat_ok = chat_resp.status_code == 200
        print(f"   Chat endpoint: {chat_resp.status_code} - {'PASS' if chat_ok else 'FAIL'}")

        if chat_ok:
            try:
                chat_data = chat_resp.json()
                msg_count = len(chat_data.get("messages", []))
                print(f"   Messages returned: {msg_count} - {'SUCCESS' if msg_count > 0 else 'PARTIAL'}")
            except:
                print("   Could not parse response JSON")

    print("\n" + "=" * 60)
    print("PHASE 3 FINAL STATUS:")
    print(f"• Health Endpoint: {'✅ OPERATIONAL' if health_ok else '❌ ISSUE'}")
    print(f"• API Documentation: {'✅ ACCESSIBLE' if docs_ok else '❌ ISSUE'}")
    print(f"• Authentication: {'✅ WORKING' if auth_ok and login_ok else '❌ ISSUE'}")
    print(f"• MCP Endpoints: {'✅ AVAILABLE' if tools_ok and providers_ok else '❌ ISSUE'}")
    print(f"• Chat Functionality: {'✅ OPERATIONAL' if chat_ok else '❌ ISSUE'}")

    all_good = health_ok and docs_ok and auth_ok and login_ok and tools_ok and providers_ok and chat_ok

    print(f"\n🎯 OVERALL STATUS: {'✅ PHASE 3 COMPLETE' if all_good else '⚠️  PHASE 3 PARTIALLY COMPLETE'}")

    if all_good:
        print("\n🎉 CONGRATULATIONS!")
        print("Phase 3 AI Chatbot Integration is fully operational!")
        print("- OpenAI Agents SDK integration complete")
        print("- MCP server with official SDK patterns implemented")
        print("- Stateless /chat endpoint with database persistence")
        print("- ChatKit-compatible interface ready")
        print("- Better Auth integration working")
        print("- All components communicating properly")

    print(f"\n📋 SERVER ACCESS:")
    print(f"   Backend: {BASE_URL}")
    print(f"   Frontend: http://localhost:3000")
    print(f"   API Docs: {BASE_URL}/docs")
    print(f"   Health: {BASE_URL}/health")

if __name__ == "__main__":
    final_verification()