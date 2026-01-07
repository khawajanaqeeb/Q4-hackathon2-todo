import os
from datetime import timedelta
from jose import jwt

# Mock environment variables before importing the app
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_purposes_only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

from app.config import settings
from app.utils.security import create_refresh_token, decode_refresh_token

# Test creating and decoding a refresh token
print("Creating refresh token...")
token = create_refresh_token(data={"sub": 1, "email": "test@example.com"})
print(f"Created token: {token[:50]}...")

print("\nDecoding refresh token...")
decoded = decode_refresh_token(token)
print(f"Decoded: {decoded}")

if decoded:
    print(f"Token type: {decoded.get('type')}")
    print(f"Subject: {decoded.get('sub')}")
    print(f"Email: {decoded.get('email')}")
    print(f"Expiration: {decoded.get('exp')}")
else:
    print("Token decoding failed")