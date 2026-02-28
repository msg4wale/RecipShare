#!/usr/bin/env python3
"""Test authentication and recipe creation flow"""

import httpx
import json
import sys

API_BASE = "http://127.0.0.1:8000"

def test_auth_flow():
    print("=" * 60)
    print("Testing Authentication Flow")
    print("=" * 60)
    
    # 1. Register
    print("\n1. Testing Registration...")
    reg_data = {
        "username": "testuser_auth",
        "email": "testuser_auth@test.com",
        "password": "testpass123"
    }
    
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.post(
                f"{API_BASE}/auth/register/",
                json=reg_data,
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
            if response.status_code not in [201, 400]:
                print("   ERROR: Unexpected status code")
                return False
                
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # 2. Login
    print("\n2. Testing Login...")
    login_data = {
        "username": "testuser_auth",
        "password": "testpass123"
    }
    
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.post(
                f"{API_BASE}/auth/login/",
                json=login_data,
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ERROR: Login failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            response_data = response.json()
            token = response_data.get("access_token")
            
            if not token:
                print("   ERROR: No access_token in response")
                print(f"   Response: {response_data}")
                return False
            
            print(f"   ✓ Token received: {token[:30]}... (length: {len(token)})")
    
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Create Recipe with token
    print("\n3. Testing Recipe Creation with token...")
    recipe_data = {
        "title": "Test Pasta",
        "description": "A test recipe",
        "ingredients": [
            {"name": "pasta", "quantity": 200, "unit": "grams"},
            {"name": "olive oil", "quantity": 2, "unit": "tablespoons"}
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"   Auth header: Authorization: Bearer {token[:30]}...")
    
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.post(
                f"{API_BASE}/recipes/",
                json=recipe_data,
                headers=headers,
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 201:
                print("   ✓ Recipe created successfully!")
                return True
            else:
                print(f"   ERROR: Recipe creation failed with status {response.status_code}")
                
                # Try to get more details
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    pass
                
                return False
                
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auth_flow()
    sys.exit(0 if success else 1)
