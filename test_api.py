#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.ok
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_firecrawl():
    """Test Firecrawl connectivity"""
    print("\nTesting Firecrawl API...")
    try:
        response = requests.get(f"{BASE_URL}/api/test/firecrawl")
        print(f"Firecrawl test: {response.status_code} - {response.json()}")
        return response.ok
    except Exception as e:
        print(f"Firecrawl test failed: {e}")
        return False

def test_manual_pitch():
    """Test manual pitch ingestion"""
    print("\nTesting manual pitch ingestion...")
    try:
        data = {
            "company_name": "Test Company",
            "industry": "Technology",
            "content": "This is a test pitch content for testing purposes."
        }
        response = requests.post(f"{BASE_URL}/api/pitch/ingest/manual", json=data)
        print(f"Manual pitch: {response.status_code} - {response.json()}")
        return response.ok
    except Exception as e:
        print(f"Manual pitch failed: {e}")
        return False

def test_scrape_start():
    """Test starting a scrape job"""
    print("\nTesting scrape job start...")
    try:
        data = {
            "url": "https://httpbin.org/html",
            "company_name": "Test Company"
        }
        response = requests.post(f"{BASE_URL}/api/pitch/ingest/scrape", json=data)
        print(f"Scrape start: {response.status_code} - {response.json()}")
        
        if response.ok:
            result = response.json()
            job_id = result.get('job_id')
            if job_id:
                print(f"Job ID: {job_id}")
                return job_id
        return None
    except Exception as e:
        print(f"Scrape start failed: {e}")
        return None

def test_scrape_status(job_id):
    """Test checking scrape job status"""
    print(f"\nTesting scrape status for job {job_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/pitch/ingest/scrape/{job_id}/status")
        print(f"Scrape status: {response.status_code} - {response.json()}")
        return response.ok
    except Exception as e:
        print(f"Scrape status failed: {e}")
        return False

def test_companies():
    """Test getting companies"""
    print("\nTesting companies endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/pitch/companies")
        print(f"Companies: {response.status_code} - {response.json()}")
        return response.ok
    except Exception as e:
        print(f"Companies failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting API tests...")
    
    # Test basic connectivity
    if not test_health():
        print("❌ Health check failed - API may not be running")
        return
    
    print("✅ Health check passed")
    
    # Test Firecrawl connectivity
    if not test_firecrawl():
        print("❌ Firecrawl test failed - check API key and connectivity")
    else:
        print("✅ Firecrawl test passed")
    
    # Test manual pitch
    if test_manual_pitch():
        print("✅ Manual pitch test passed")
    else:
        print("❌ Manual pitch test failed")
    
    # Test scrape functionality
    job_id = test_scrape_start()
    if job_id:
        print("✅ Scrape start test passed")
        
        # Wait a bit and check status
        print("Waiting 5 seconds before checking status...")
        time.sleep(5)
        
        if test_scrape_status(job_id):
            print("✅ Scrape status test passed")
        else:
            print("❌ Scrape status test failed")
    else:
        print("❌ Scrape start test failed")
    
    # Test companies endpoint
    if test_companies():
        print("✅ Companies test passed")
    else:
        print("❌ Companies test failed")
    
    print("\nTest suite completed!")

if __name__ == "__main__":
    main() 