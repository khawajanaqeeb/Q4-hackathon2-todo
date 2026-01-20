#!/usr/bin/env python3
"""Test script to verify OpenAI API key and basic functionality."""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("[FAILED] OPENAI_API_KEY not found in environment")
    exit(1)

print(f"[SUCCESS] OpenAI API key found: {api_key[:10]}...")

# Test OpenAI client initialization
try:
    client = OpenAI(api_key=api_key)
    print("[SUCCESS] OpenAI client initialized successfully")

    # Test a simple API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Hello, this is a test message to verify the API connection."}
        ],
        max_tokens=10,
        temperature=0
    )

    print(f"[SUCCESS] API call successful: {response.choices[0].message.content[:50]}...")
    print("[SUCCESS] OpenAI API connection working properly!")

except Exception as e:
    print(f"[ERROR] Error with OpenAI API: {str(e)}")
    exit(1)

print("\n[COMPLETE] OpenAI API test completed successfully!")