#!/usr/bin/env python3
"""
Example usage of the Perplexity integration and prompt management system
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def example_company_research():
    """Example: Research a company using Perplexity"""
    print("🔍 Example: Company Research with Perplexity")
    print("-" * 50)
    
    company_name = "Stripe"
    
    # Get research from Perplexity
    response = requests.get(f"{BASE_URL}/api/research/company/{company_name}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Research completed for {company_name}")
        print(f"Model used: {result.get('model', 'unknown')}")
        print(f"Research length: {len(result.get('research', ''))} characters")
        
        # Show a preview of the research
        research = result.get('research', '')
        if research:
            print("\n📋 Research Preview (first 500 chars):")
            print("-" * 30)
            print(research[:500] + "..." if len(research) > 500 else research)
    else:
        print(f"❌ Research failed: {response.text}")

def example_prompt_management():
    """Example: Managing prompts"""
    print("\n📝 Example: Prompt Management")
    print("-" * 50)
    
    # List all prompts
    response = requests.get(f"{BASE_URL}/api/prompts")
    if response.status_code == 200:
        prompts = response.json()
        print(f"Available prompts: {len(prompts)}")
        for prompt in prompts:
            print(f"  - {prompt['name']}")
    
    # Get a specific prompt
    response = requests.get(f"{BASE_URL}/api/prompts/sales_research_prompt")
    if response.status_code == 200:
        prompt = response.json()
        print(f"\nSales research prompt length: {len(prompt.get('content', ''))} characters")
        
        # Check if it contains the placeholder
        content = prompt.get('content', '')
        if '[INSERT COMPANY NAME HERE]' in content:
            print("✅ Prompt contains the required placeholder")
        else:
            print("❌ Prompt missing required placeholder")

def example_scraping_workflow():
    """Example: Full scraping workflow with Perplexity research"""
    print("\n🌐 Example: Full Scraping Workflow")
    print("-" * 50)
    
    # Start a scraping job
    data = {
        "url": "https://www.notion.so",
        "company_name": "Notion"
    }
    
    print(f"Starting scrape for {data['company_name']}...")
    response = requests.post(f"{BASE_URL}/api/pitch/ingest/scrape", json=data)
    
    if response.status_code == 202:
        result = response.json()
        job_id = result.get('job_id')
        print(f"✅ Scrape job started: {job_id}")
        print(f"Status: {result.get('status')}")
        print(f"Company: {result.get('company_name')}")
        
        print("\n💡 This job will:")
        print("  1. Scrape the website using Firecrawl")
        print("  2. Research the company using Perplexity")
        print("  3. Combine both results into comprehensive data")
        print("  4. Store everything for later use")
        
        print(f"\n📊 Check job status: GET /api/pitch/ingest/scrape/{job_id}/status")
        print(f"📊 Get final results: GET /api/pitch/ingest/scrape/{job_id}/result")
        
    else:
        print(f"❌ Failed to start scrape: {response.text}")

def example_custom_prompt():
    """Example: Creating a custom prompt"""
    print("\n✏️  Example: Creating a Custom Prompt")
    print("-" * 50)
    
    # Create a new prompt for competitive analysis
    competitive_prompt = """Act as a competitive intelligence analyst. Research the competitive landscape for [COMPANY_NAME].

Focus on:
- Direct competitors
- Market positioning
- Competitive advantages
- Market share estimates
- Recent competitive moves

Provide actionable insights for sales and marketing teams.

Company: [COMPANY_NAME]"""
    
    # Save the new prompt
    data = {"content": competitive_prompt}
    response = requests.post(f"{BASE_URL}/api/prompts/competitive_analysis", json=data)
    
    if response.status_code == 200:
        print("✅ Custom prompt created successfully")
        print("Prompt name: competitive_analysis")
        
        # Verify it was saved
        response = requests.get(f"{BASE_URL}/api/prompts/competitive_analysis")
        if response.status_code == 200:
            prompt = response.json()
            print(f"Prompt length: {len(prompt.get('content', ''))} characters")
            print("✅ Prompt saved and retrievable")
    else:
        print(f"❌ Failed to create prompt: {response.text}")

def main():
    """Run all examples"""
    print("🚀 Perplexity Integration Examples")
    print("=" * 60)
    
    examples = [
        ("Company Research", example_company_research),
        ("Prompt Management", example_prompt_management),
        ("Scraping Workflow", example_scraping_workflow),
        ("Custom Prompt Creation", example_custom_prompt)
    ]
    
    for example_name, example_func in examples:
        try:
            example_func()
            print("\n" + "=" * 60)
        except Exception as e:
            print(f"❌ {example_name} failed: {e}")
            print("\n" + "=" * 60)
    
    print("\n🎯 Next Steps:")
    print("1. Start the API server: python api/api.py")
    print("2. Run the test script: python test_perplexity_integration.py")
    print("3. Try the examples above")
    print("4. Customize prompts for your specific needs")

if __name__ == "__main__":
    main() 