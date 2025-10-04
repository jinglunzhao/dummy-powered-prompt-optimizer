#!/usr/bin/env python3
"""
Test script for the comments API functionality
"""

import requests
import json
import time

def test_comments_api():
    """Test the comments API endpoints"""
    
    base_url = "http://localhost:5000"
    test_prompt_id = "test_prompt_123"
    
    print("🧪 Testing Comments API")
    print("=" * 50)
    
    # Test 1: Get comments for non-existent prompt
    print("\n1. Testing GET comments for non-existent prompt...")
    try:
        response = requests.get(f"{base_url}/api/comments/{test_prompt_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ GET successful: {data}")
        else:
            print(f"   ❌ GET failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ GET error: {e}")
    
    # Test 2: Save comments
    print("\n2. Testing POST comments...")
    test_comments = """
This is a test comment for the experiment.

Observations:
- The conversation flow seems natural
- AI responses are helpful and supportive  
- Some dummies showed significant improvement
- The assessment scores improved by an average of 0.47 points

Recommendations:
- Consider testing with more diverse personality profiles
- The conversation length seems optimal at 15 rounds
"""
    
    try:
        response = requests.post(
            f"{base_url}/api/comments/{test_prompt_id}",
            headers={'Content-Type': 'application/json'},
            json={
                'comments': test_comments,
                'prompt_id': test_prompt_id
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ POST successful: {data}")
        else:
            print(f"   ❌ POST failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ POST error: {e}")
    
    # Test 3: Get comments after saving
    print("\n3. Testing GET comments after saving...")
    try:
        response = requests.get(f"{base_url}/api/comments/{test_prompt_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ GET successful:")
            print(f"      Comments: {data.get('comments', '')[:100]}...")
            print(f"      Last modified: {data.get('last_modified')}")
        else:
            print(f"   ❌ GET failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ GET error: {e}")
    
    # Test 4: Update comments
    print("\n4. Testing POST comments update...")
    updated_comments = test_comments + "\n\nUPDATE: Additional testing revealed that the prompt works well with high-anxiety dummies."
    
    try:
        response = requests.post(
            f"{base_url}/api/comments/{test_prompt_id}",
            headers={'Content-Type': 'application/json'},
            json={
                'comments': updated_comments,
                'prompt_id': test_prompt_id
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ POST update successful: {data}")
        else:
            print(f"   ❌ POST update failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ POST update error: {e}")
    
    print("\n🎉 Comments API test completed!")

if __name__ == "__main__":
    # Wait a moment for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    test_comments_api()
