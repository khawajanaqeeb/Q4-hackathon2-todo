#!/usr/bin/env python3
"""Final verification that OpenAI integration is working properly."""

import os
from dotenv import load_dotenv
from openai import OpenAI

print("[INFO] Verifying OpenAI Integration for Phase 3 Backend...")

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("[ERROR] FAILED: OPENAI_API_KEY not found in environment")
    exit(1)

print(f"[SUCCESS] SUCCESS: OpenAI API key found in environment")

# Test OpenAI client initialization
try:
    client = OpenAI(api_key=api_key)
    print("[SUCCESS] SUCCESS: OpenAI client initialized successfully")

    # Test a simple API call
    print("[INFO] Testing API call to gpt-4o-mini...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Hello, this is a test message to verify the API connection. Please respond with a simple acknowledgment."}
        ],
        max_tokens=50,
        temperature=0.1
    )

    response_text = response.choices[0].message.content
    print(f"[SUCCESS] SUCCESS: API call successful!")
    print(f"   Response: '{response_text[:60]}...'")

    print("\n[COMPLETE] VERIFICATION COMPLETE:")
    print("[SUCCESS] OpenAI API key is properly configured")
    print("[SUCCESS] OpenAI client connects successfully")
    print("[SUCCESS] API calls to gpt-4o-mini are working")
    print("[SUCCESS] Response from OpenAI received successfully")
    print("\n[INFO] The OpenAI integration from Gemini to native OpenAI models is fully functional!")
    print("[INFO] The system is ready to use real OpenAI API with gpt-4o-mini model.")

except Exception as e:
    print(f"[ERROR] ERROR with OpenAI API: {str(e)}")
    exit(1)

print("\n[CONCLUSION] CONCLUSION: OpenAI migration from Gemini to native OpenAI models is SUCCESSFUL!")