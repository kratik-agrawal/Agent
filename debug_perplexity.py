#!/usr/bin/env python3
"""
Debug script for Perplexity API issues
"""

import requests
import json


def test_perplexity_api():
    """Test Perplexity API with different configurations"""
    
    # Test 1: Basic API call
    print("🧪 Test 1: Basic API call")
    print("=" * 50)
    
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try with the correct model name
    data = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you tell me about Microsoft?"
            }
        ],
        "max_tokens": 100
    }
    
    print(f"Request URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Try with online model
    print("🧪 Test 2: Try with online model")
    print("=" * 50)
    
    data_online = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you tell me about Microsoft?"
            }
        ],
        "max_tokens": 100
    }
    
    print(f"Online model request data: {json.dumps(data_online, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data_online, timeout=30)
        print(f"\nOnline model response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success with online model! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Online model error: {response.text}")
            
    except Exception as e:
        print(f"❌ Online model exception: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Try with different model
    print("🧪 Test 3: Try with different model")
    print("=" * 50)
    
    # Try with a different model name
    data_alt = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you tell me about Microsoft?"
            }
        ],
        "max_tokens": 100
    }
    
    print(f"Alternative request data: {json.dumps(data_alt, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data_alt, timeout=30)
        print(f"\nAlternative response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success with alternative model! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Alternative model error: {response.text}")
            
    except Exception as e:
        print(f"❌ Alternative model exception: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Test 4: Try with minimal parameters
    print("🧪 Test 4: Try with minimal parameters")
    print("=" * 50)
    
    data_minimal = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": "Hi"
            }
        ]
    }
    
    print(f"Minimal request data: {json.dumps(data_minimal, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data_minimal, timeout=30)
        print(f"\nMinimal response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success with minimal params! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Minimal params error: {response.text}")
            
    except Exception as e:
        print(f"❌ Minimal params exception: {str(e)}")

def test_api_key():
    """Test if the API key is valid"""
    print("🔑 Testing API Key")
    print("=" * 50)
    
    # Try to get account info or models
    url = "https://api.perplexity.ai/models"
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"API Key test response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Key appears to be valid")
        elif response.status_code == 401:
            print("❌ API Key is invalid or expired")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API Key test exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Perplexity API Debug Script")
    print("=" * 60)
    
    test_api_key()
    print()
    test_perplexity_api()
    
    print("\n🎯 Debug Summary:")
    print("1. Check if API key is valid")
    print("2. Verify model names are correct")
    print("3. Check request format and parameters")
    print("4. Review API documentation for latest changes") 