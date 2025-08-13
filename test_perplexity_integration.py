#!/usr/bin/env python3
"""
Test script for Perplexity integration and prompt management
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test basic API health"""
    print("Testing API health...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_perplexity():
    """Test Perplexity API connectivity"""
    print("\nTesting Perplexity API...")
    response = requests.get(f"{BASE_URL}/api/test/perplexity")
    print(f"Perplexity test: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Perplexity API working")
        print(f"   Model: {result.get('model', 'unknown')}")
        print(f"   Test company: {result.get('test_company', 'unknown')}")
        print(f"   Content preview: {result.get('content_preview', 'N/A')}")
        return True
    else:
        print(f"❌ Perplexity API failed: {response.text}")
        return False

def test_prompts():
    """Test prompt management endpoints"""
    print("\nTesting prompt management...")
    
    # List prompts
    response = requests.get(f"{BASE_URL}/api/prompts")
    print(f"List prompts: {response.status_code}")
    if response.status_code == 200:
        prompts = response.json()
        print(f"   Found {len(prompts)} prompts:")
        for prompt in prompts:
            print(f"     - {prompt['name']}")
    
    # Get sales research prompt
    response = requests.get(f"{BASE_URL}/api/prompts/sales_research_prompt")
    print(f"Get sales research prompt: {response.status_code}")
    if response.status_code == 200:
        prompt = response.json()
        print(f"   Prompt length: {len(prompt.get('content', ''))} characters")
        print(f"   Contains placeholder: {'[INSERT COMPANY NAME HERE]' in prompt.get('content', '')}")
    
    return True

def test_company_research():
    """Test company research endpoint"""
    print("\nTesting company research...")
    response = requests.get(f"{BASE_URL}/api/research/company/Apple")
    print(f"Company research: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Company research successful")
        print(f"   Company: {result.get('company_name', 'unknown')}")
        print(f"   Model: {result.get('model', 'unknown')}")
        print(f"   Research length: {len(result.get('research', ''))} characters")
        return True
    else:
        print(f"❌ Company research failed: {response.text}")
        return False

def test_scrape_with_research():
    """Test the full scraping workflow with Perplexity research"""
    print("\nTesting full scraping workflow...")
    
    # Start a scrape job
    data = {
        "url": "https://www.apple.com",
        "company_name": "Apple Inc"
    }
    
    response = requests.post(f"{BASE_URL}/api/pitch/ingest/scrape", json=data)
    print(f"Start scrape: {response.status_code}")
    
    if response.status_code == 202:
        result = response.json()
        job_id = result.get('job_id')
        print(f"   Job started: {job_id}")
        
        # Poll for completion
        max_wait = 60  # Wait up to 60 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(f"{BASE_URL}/api/pitch/ingest/scrape/{job_id}/status")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                print(f"   Job status: {status}")
                
                if status == "completed":
                    print("✅ Scraping completed successfully!")
                    result_data = status_data.get('result', {})
                    if 'perplexity_research' in result_data:
                        perplexity_data = result_data['perplexity_research']
                        if perplexity_data.get('success'):
                            print(f"   Perplexity research: ✅ Success")
                            print(f"   Research length: {len(perplexity_data.get('content', ''))} characters")
                        else:
                            print(f"   Perplexity research: ❌ Failed - {perplexity_data.get('error', 'Unknown error')}")
                    return True
                elif status == "failed":
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ Scraping failed: {error}")
                    return False
                
                time.sleep(5)  # Wait 5 seconds before next check
            else:
                print(f"   Error checking status: {response.status_code}")
                time.sleep(5)
        
        print("❌ Scraping timed out")
        return False
    else:
        print(f"❌ Failed to start scrape: {response.text}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Perplexity Integration and Prompt Management")
    print("=" * 60)
    
    tests = [
        ("API Health", test_health),
        ("Perplexity API", test_perplexity),
        ("Prompt Management", test_prompts),
        ("Company Research", test_company_research),
        ("Full Scraping Workflow", test_scrape_with_research)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Perplexity integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 