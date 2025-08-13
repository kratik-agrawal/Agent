from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import json
import os
from datetime import datetime, timedelta
import asyncio
from firecrawl import AsyncFirecrawlApp, ScrapeOptions
import threading
import time
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Data storage directory
DATA_DIR = "data"
COMPANIES_FILE = os.path.join(DATA_DIR, "companies.json")
SCRAPED_DIR = os.path.join(DATA_DIR, "scraped")
PROMPTS_DIR = "prompts"

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SCRAPED_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)

# API Keys from environment variables
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')

# Validate required API keys
if not PERPLEXITY_API_KEY:
    print("⚠️  WARNING: PERPLEXITY_API_KEY not found in environment variables")
    print("   Persona generation and AI research will not work")
    print("   Please set PERPLEXITY_API_KEY in your .env file")

if not FIRECRAWL_API_KEY:
    print("⚠️  WARNING: FIRECRAWL_API_KEY not found in environment variables")
    print("   Web scraping will not work")
    print("   Please set FIRECRAWL_API_KEY in your .env file")

# In-memory job tracking (simple for prototype)
crawl_jobs = {}

def load_companies():
    """Load companies data from file"""
    if os.path.exists(COMPANIES_FILE):
        with open(COMPANIES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_companies(companies):
    """Save companies data to file"""
    with open(COMPANIES_FILE, 'w') as f:
        json.dump(companies, f, indent=2)

def save_scraped_data(company_name, data):
    """Save scraped data for a company"""
    company_dir = os.path.join(SCRAPED_DIR, company_name.lower().replace(' ', '_'))
    os.makedirs(company_dir, exist_ok=True)
    
    file_path = os.path.join(company_dir, "scraped_data.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_prompt(prompt_name):
    """Load a prompt from the prompts directory"""
    prompt_path = os.path.join(PROMPTS_DIR, f"{prompt_name}.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r') as f:
            return f.read()
    return None

def save_prompt(prompt_name, content):
    """Save a prompt to the prompts directory"""
    prompt_path = os.path.join(PROMPTS_DIR, f"{prompt_name}.txt")
    with open(prompt_path, 'w') as f:
        f.write(content)

def get_perplexity_research(company_name):
    """Get company research from Perplexity API"""
    if not PERPLEXITY_API_KEY:
        return {
            "success": False,
            "content": "Perplexity API key not configured. Please set PERPLEXITY_API_KEY in your .env file.",
            "model": "unknown",
            "usage": {}
        }
    
    try:
        # Load the sales research prompt
        prompt_template = load_prompt("sales_research_prompt")
        if not prompt_template:
            raise Exception("Sales research prompt not found")
        
        # Replace placeholder with company name
        prompt = prompt_template.replace("[INSERT COMPANY NAME HERE]", company_name)
        
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return {
                "success": True,
                "content": content,
                "model": result['model'],
                "usage": result.get('usage', {})
            }
        else:
            return {
                "success": False,
                "content": f"API request failed with status {response.status_code}",
                "model": "unknown",
                "usage": {}
            }
            
    except Exception as e:
        return {
            "success": False,
            "content": f"Error: {str(e)}",
            "model": "unknown",
            "usage": {}
        }

def generate_buyer_personas(company_name, industry, scraped_content=None, ai_research=None):
    """Generate buyer personas using Perplexity API - simplified to return formatted text"""
    if not PERPLEXITY_API_KEY:
        return {
            "success": False,
            "content": "Perplexity API key not configured. Please set PERPLEXITY_API_KEY in your .env file.",
            "model": "unknown",
            "usage": {}
        }
    
    try:
        print(f"Generating personas for {company_name} in {industry}")
        
        # Load the persona generation prompt
        prompt_template = load_prompt("persona_generation_prompt")
        if not prompt_template:
            raise Exception("Persona generation prompt not found")
        
        # Replace placeholders with actual values, using defaults if not available
        prompt = prompt_template.replace("[COMPANY_NAME]", company_name or "Unknown Company")
        prompt = prompt_template.replace("[INDUSTRY]", industry or "Unknown Industry")
        prompt = prompt_template.replace("[SCRAPED_CONTENT]", scraped_content or "No scraped content available")
        prompt = prompt_template.replace("[AI_RESEARCH]", ai_research or "No AI research available")
        
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        print("Making request to Perplexity API...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"Perplexity API response received, content length: {len(content)}")
            
            # Just return the formatted text from Perplexity
            return {
                "success": True,
                "content": content,
                "model": result['model'],
                "usage": result.get('usage', {}),
                "confidence_score": 0.9
            }
        else:
            print(f"Perplexity API failed with status {response.status_code}")
            return {
                "success": False,
                "content": f"API request failed with status {response.status_code}",
                "model": "unknown",
                "usage": {}
            }
            
    except Exception as e:
        print(f"Error in generate_buyer_personas: {str(e)}")
        return {
            "success": False,
            "content": f"Error: {str(e)}",
            "model": "unknown",
            "usage": {}
        }

def generate_market_analysis(company_name, industry):
    """Generate market analysis using Perplexity API"""
    if not PERPLEXITY_API_KEY:
        return {
            "success": False,
            "content": "Perplexity API key not configured. Please set PERPLEXITY_API_KEY in your .env file.",
            "model": "unknown",
            "usage": {}
        }
    
    try:
        print(f"Generating market analysis for {company_name} in {industry}")
        
        # Load the market analysis prompt
        prompt_template = load_prompt("market_analysis_prompt")
        if not prompt_template:
            raise Exception("Market analysis prompt not found")
        
        # Replace placeholders
        prompt = prompt_template.replace("[COMPANY_NAME]", company_name or "Unknown Company")
        prompt = prompt_template.replace("[INDUSTRY]", industry or "Unknown Industry")
        
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        print("Making request to Perplexity API for market analysis...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"Market analysis response received, content length: {len(content)}")
            
            return {
                "success": True,
                "content": content,
                "model": result['model'],
                "usage": result.get('usage', {}),
                "confidence_score": 0.9
            }
        else:
            print(f"Perplexity API failed with status {response.status_code}")
            return {
                "success": False,
                "content": f"API request failed with status {response.status_code}",
                "model": "unknown",
                "usage": {}
            }
            
    except Exception as e:
        print(f"Error in generate_market_analysis: {str(e)}")
        return {
            "success": False,
            "content": f"Error: {str(e)}",
            "model": "unknown",
            "usage": {}
        }

def run_scrape_sync(job_id, url, company_name):
    """Run the actual scraping job in a separate thread"""
    try:
        crawl_jobs[job_id]["status"] = "running"
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize Firecrawl
        app = AsyncFirecrawlApp(api_key=FIRECRAWL_API_KEY)
        
        print(f"Starting concurrent scraping and research for {company_name}...")
        
        # Step 1: Start both Firecrawl and Perplexity concurrently
        import concurrent.futures
        
        def run_firecrawl():
            """Run Firecrawl scraping"""
            try:
                print(f"Starting Firecrawl crawl for {url}...")
                crawl_response = loop.run_until_complete(app.crawl_url(
                    url=url,
                    limit=2,
                    max_depth=1,
                    scrape_options=ScrapeOptions(
                        formats=['markdown', 'html'],
                        onlyMainContent=True,
                        parsePDF=False,
                        maxAge=14400000
                    )
                ))
                return crawl_response
            except Exception as e:
                print(f"Firecrawl error: {str(e)}")
                return None
        
        def run_perplexity():
            """Run Perplexity research"""
            try:
                print(f"Starting Perplexity research for {company_name}...")
                return get_perplexity_research(company_name)
            except Exception as e:
                print(f"Perplexity error: {str(e)}")
                return None
        
        # Run both tasks concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            firecrawl_future = executor.submit(run_firecrawl)
            perplexity_future = executor.submit(run_perplexity)
            
            # Wait for both to complete
            crawl_response = firecrawl_future.result()
            perplexity_research = perplexity_future.result()
        
        print(f"Both tasks completed. Processing results...")
        
        # Step 2: Process Firecrawl results
        if not crawl_response:
            raise Exception("Firecrawl failed to start")
        
        print(f"Initial response type: {type(crawl_response)}")
        if hasattr(crawl_response, 'status'):
            print(f"Initial response status: {crawl_response.status}")
        if hasattr(crawl_response, 'total'):
            print(f"Initial response total: {crawl_response.total}")
        if hasattr(crawl_response, 'completed'):
            print(f"Initial response completed: {crawl_response.completed}")
        
        # Check if the response is already completed (immediate completion)
        if hasattr(crawl_response, 'status') and crawl_response.status == 'completed':
            print("Crawl completed immediately, processing results directly")
            print(f"Immediate completion - Total pages: {getattr(crawl_response, 'total', 'unknown')}")
            status_response = crawl_response
            crawl_job_id = f"immediate-{job_id}"
        else:
            print("Crawl started as background job, polling for completion...")
            # Extract job ID from the response for background job
            crawl_job_id = None
            
            # Check if response is a dict (cURL response) or object (SDK response)
            if isinstance(crawl_response, dict):
                # Handle dict response (cURL style)
                if 'id' in crawl_response:
                    crawl_job_id = crawl_response['id']
                elif 'job_id' in crawl_response:
                    crawl_job_id = crawl_response['job_id']
            else:
                # Handle SDK response object
                if hasattr(crawl_response, 'id'):
                    crawl_job_id = crawl_response.id
                elif hasattr(crawl_response, 'job_id'):
                    crawl_job_id = crawl_response.job_id
                elif hasattr(crawl_response, 'success') and crawl_response.success:
                    # Try to get from response data
                    if hasattr(crawl_response, 'data') and hasattr(crawl_response.data, 'id'):
                        crawl_job_id = crawl_response.data.id
            
            if not crawl_job_id:
                print(f"Response type: {type(crawl_response)}")
                print(f"Response attributes: {[attr for attr in dir(crawl_response) if not attr.startswith('_')]}")
                if hasattr(crawl_response, 'status'):
                    print(f"Response status: {crawl_response.status}")
                if hasattr(crawl_response, 'success'):
                    print(f"Response success: {crawl_response.success}")
                raise Exception(f"Could not extract job ID from response")
            
            print(f"Firecrawl job ID: {crawl_job_id}")
            
            # Step 3: Poll for completion and get results (only for background jobs)
            max_attempts = 30  # 30 attempts with 10 second delays = 5 minutes max
            for attempt in range(max_attempts):
                if attempt % 5 == 0:  # Log every 5th attempt to reduce noise
                    print(f"Checking crawl status, attempt {attempt + 1}/{max_attempts}")
                
                try:
                    status_response = loop.run_until_complete(app.check_crawl_status(crawl_job_id))
                    
                    # Handle both dict and object responses
                    status = None
                    if isinstance(status_response, dict):
                        status = status_response.get('status')
                    else:
                        status = getattr(status_response, 'status', None)
                    
                    if status:
                        if status == 'completed':
                            print("Crawl completed, processing results")
                            break
                        elif status == 'failed':
                            error_msg = "Unknown error"
                            if isinstance(status_response, dict):
                                error_msg = status_response.get('error', error_msg)
                            else:
                                error_msg = getattr(status_response, 'error', error_msg)
                            raise Exception(f"Crawl failed: {error_msg}")
                        else:
                            # Log progress if available
                            if isinstance(status_response, dict):
                                completed = status_response.get('completed', 0)
                                total = status_response.get('total', 0)
                            else:
                                completed = getattr(status_response, 'completed', 0)
                                total = getattr(status_response, 'total', 0)
                            
                            if completed and total:
                                print(f"Progress: {completed}/{total} pages")
                            time.sleep(10)  # Wait 10 seconds before next check
                    else:
                        time.sleep(10)
                except Exception as e:
                    print(f"Error checking status: {e}")
                    time.sleep(10)
            else:
                raise Exception("Crawl timed out after 5 minutes")
        
        # Step 4: Process the results from the status response
        print("Processing scraped content...")
        processed_content = []
        
        # Extract data from status response - handle both dict and object
        data = None
        if isinstance(status_response, dict):
            data = status_response.get('data', [])
        else:
            data = getattr(status_response, 'data', [])
        
        if data:
            print(f"Processing {len(data)} content items")
            for item in data:
                # Handle both dict and object items
                if isinstance(item, dict):
                    # Dict item
                    if 'markdown' in item and item['markdown']:
                        processed_content.append({
                            "type": "markdown",
                            "url": item.get('url', ''),
                            "content": item['markdown'][:5000] if len(item['markdown']) > 5000 else item['markdown']
                        })
                    elif 'html' in item and item['html']:
                        processed_content.append({
                            "type": "html",
                            "url": item.get('url', ''),
                            "content": item['html'][:2000] if len(item['html']) > 2000 else item['html']
                        })
                    
                    # Extract metadata
                    if 'metadata' in item and item['metadata']:
                        metadata = item['metadata']
                        if 'title' in metadata and metadata['title']:
                            processed_content.append({
                                "type": "title",
                                "url": item.get('url', ''),
                                "content": metadata['title']
                            })
                        
                        if 'description' in metadata and metadata['description']:
                            processed_content.append({
                                "type": "description",
                                "url": item.get('url', ''),
                                "content": metadata['description']
                            })
                else:
                    # Object item
                    if hasattr(item, 'markdown') and item.markdown:
                        processed_content.append({
                            "type": "markdown",
                            "url": getattr(item, 'url', ''),
                            "content": item.markdown[:5000] if len(item.markdown) > 5000 else item.markdown
                        })
                    
                    elif hasattr(item, 'html') and item.html:
                        processed_content.append({
                            "type": "html",
                            "url": getattr(item, 'url', ''),
                            "content": item.html[:2000] if len(item.html) > 2000 else item.html
                        })
                    
                    # Extract metadata from object
                    if hasattr(item, 'metadata') and item.metadata:
                        metadata = item.metadata
                        if hasattr(metadata, 'title') and metadata.title:
                            processed_content.append({
                                "type": "title",
                                "url": getattr(item, 'url', ''),
                                "content": metadata.title
                            })
                        
                        if hasattr(metadata, 'description') and metadata.description:
                            processed_content.append({
                                "type": "description",
                                "url": getattr(item, 'url', ''),
                                "content": metadata.description
                            })
        else:
            print(f"No data found in status response")
        
        print(f"Successfully processed {len(processed_content)} content items")
        
        # Step 5: Perplexity research is already completed from concurrent execution
        print("Perplexity research status:")
        if perplexity_research and perplexity_research.get("success"):
            print("✅ Perplexity research completed successfully")
        else:
            print(f"❌ Perplexity research failed: {perplexity_research.get('error', 'Unknown error') if perplexity_research else 'No response'}")
        
        # Process and store results
        scraped_data = {
            "job_id": job_id,
            "firecrawl_job_id": crawl_job_id,
            "url": url,
            "company_name": company_name,
            "scraped_at": datetime.now().isoformat(),
            "processed_content": processed_content,
            "content_count": len(processed_content),
            "perplexity_research": perplexity_research,
            "status": "completed"
        }        
        # Save to file
        save_scraped_data(company_name, scraped_data)
        
        # Update job status
        crawl_jobs[job_id]["status"] = "completed"
        crawl_jobs[job_id]["result"] = scraped_data
        
        # Update companies data
        companies = load_companies()
        existing_company = next((c for c in companies if c['name'].lower() == company_name.lower()), None)
        
        if existing_company:
            existing_company['scraped_data'] = scraped_data
            existing_company['updated_at'] = datetime.now().isoformat()
        else:
            companies.append({
                "name": company_name,
                "scraped_data": scraped_data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        save_companies(companies)
        
        loop.close()
        
    except Exception as e:
        print(f"Scraping error for job {job_id}: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            print(f"Error details: {traceback.format_exc().split('Traceback')[-1].strip()}")
        crawl_jobs[job_id]["status"] = "failed"
        crawl_jobs[job_id]["error"] = str(e)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/test/firecrawl', methods=['GET'])
def test_firecrawl():
    """Test Firecrawl API connectivity"""
    try:
        # Test with a simple scrape
        
        # Create new event loop for this request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Try to scrape a simple page
            result = loop.run_until_complete(app.scrape_url(
                'https://httpbin.org/html',
                formats=['markdown']
            ))
            
            loop.close()
            
            # Extract only essential info for display
            result_summary = {
                "type": type(result).__name__,
                "has_markdown": hasattr(result, 'markdown') and bool(result.markdown),
                "has_metadata": hasattr(result, 'metadata') and bool(result.metadata),
                "success": getattr(result, 'success', None)
            }
            
            return jsonify({
                "status": "success",
                "message": "Firecrawl API is working",
                "result_summary": result_summary
            })
            
        except Exception as e:
            loop.close()
            return jsonify({
                "status": "error",
                "message": "Firecrawl API test failed",
                "error": str(e)
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to initialize Firecrawl",
            "error": str(e)
        }), 500

@app.route('/api/pitch/ingest/manual', methods=['POST'])
def ingest_manual_pitch():
    """Accept manual pitch input"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
        
        company_name = data.get('company_name', 'Unknown Company')
        content = data['content']
        industry = data.get('industry', 'Unknown Industry')
        
        # Create pitch entry
        pitch_data = {
            "id": str(uuid.uuid4()),
            "type": "manual",
            "company_name": company_name,
            "industry": industry,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Load existing companies and add/update
        companies = load_companies()
        existing_company = next((c for c in companies if c['name'].lower() == company_name.lower()), None)
        
        if existing_company:
            existing_company['pitch'] = pitch_data
            existing_company['updated_at'] = datetime.now().isoformat()
        else:
            companies.append({
                "name": company_name,
                "industry": industry,
                "pitch": pitch_data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        save_companies(companies)
        
        return jsonify({
            "message": "Pitch ingested successfully",
            "pitch_id": pitch_data["id"],
            "company_name": company_name
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pitch/ingest/scrape', methods=['POST'])
def start_scrape():
    """Start a web scraping job with Firecrawl"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        company_name = data.get('company_name', 'Unknown Company')
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return jsonify({"error": "Invalid URL format. Must start with http:// or https://"}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Store job info
        crawl_jobs[job_id] = {
            "url": url,
            "company_name": company_name,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        print(f"Starting scrape job {job_id} for {url}")
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=run_scrape_sync, args=(job_id, url, company_name))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "message": "Scraping job started",
            "job_id": job_id,
            "status": "pending",
            "company_name": company_name
        }), 202
        
    except Exception as e:
        print(f"Error starting scrape job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pitch/ingest/scrape/<job_id>/status', methods=['GET'])
def get_scrape_status(job_id):
    """Get the status of a scraping job"""
    if job_id not in crawl_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = crawl_jobs[job_id]
    response_data = {
        "job_id": job_id,
        "status": job["status"],
        "company_name": job["company_name"],
        "created_at": job["created_at"],
        "url": job["url"]
    }
    
    # Add error information if available
    if job.get("error"):
        response_data["error"] = job["error"]
    
    # Add result information if completed
    if job["status"] == "completed" and job.get("result"):
        response_data["result"] = job["result"]
    
    return jsonify(response_data)

@app.route('/api/pitch/ingest/scrape/<job_id>/result', methods=['GET'])
def get_scrape_result(job_id):
    """Get the result of a completed scraping job"""
    if job_id not in crawl_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = crawl_jobs[job_id]
    
    if job["status"] != "completed":
        return jsonify({"error": "Job not completed", "status": job["status"]}), 400
    
    return jsonify(job["result"])

@app.route('/api/pitch/companies', methods=['GET'])
def get_companies():
    """Get all companies and their pitch data"""
    companies = load_companies()
    return jsonify(companies)

@app.route('/api/pitch/companies/<company_name>', methods=['GET'])
def get_company(company_name):
    """Get specific company data"""
    companies = load_companies()
    company = next((c for c in companies if c['name'].lower() == company_name.lower()), None)
    
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    return jsonify(company)

@app.route('/api/test/perplexity', methods=['GET'])
def test_perplexity():
    """Test Perplexity API connectivity"""
    try:
        # Test with a simple company name
        test_company = "Microsoft"
        result = get_perplexity_research(test_company)
        
        if result.get("success"):
            return jsonify({
                "status": "success",
                "message": "Perplexity API is working",
                "test_company": test_company,
                "model": result.get("model", "unknown"),
                "usage": result.get("usage", {}),
                "content_preview": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", "")
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Perplexity API test failed",
                "error": result.get("error", "Unknown error")
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to test Perplexity API",
            "error": str(e)
        }), 500

@app.route('/api/prompts', methods=['GET'])
def list_prompts():
    """List all available prompts"""
    try:
        prompts = []
        for filename in os.listdir(PROMPTS_DIR):
            if filename.endswith('.txt'):
                prompt_name = filename[:-4]  # Remove .txt extension
                prompts.append({
                    "name": prompt_name,
                    "filename": filename
                })
        return jsonify(prompts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_name>', methods=['GET'])
def get_prompt(prompt_name):
    """Get a specific prompt"""
    try:
        content = load_prompt(prompt_name)
        if content is None:
            return jsonify({"error": "Prompt not found"}), 404
        
        return jsonify({
            "name": prompt_name,
            "content": content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_name>', methods=['POST'])
def update_prompt(prompt_name):
    """Update or create a prompt"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
        
        content = data['content']
        save_prompt(prompt_name, content)
        
        return jsonify({
            "message": "Prompt updated successfully",
            "name": prompt_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_name>', methods=['DELETE'])
def delete_prompt(prompt_name):
    """Delete a prompt"""
    try:
        prompt_path = os.path.join(PROMPTS_DIR, f"{prompt_name}.txt")
        if os.path.exists(prompt_path):
            os.remove(prompt_path)
            return jsonify({
                "message": "Prompt deleted successfully",
                "name": prompt_name
            })
        else:
            return jsonify({"error": "Prompt not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/research/company/<company_name>', methods=['GET'])
def research_company(company_name):
    """Get AI research for a company"""
    try:
        research = get_perplexity_research(company_name)
        return jsonify(research)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/market/analyze', methods=['POST'])
def analyze_market():
    """Generate market analysis for a company"""
    try:
        print("=== Market Analysis Request ===")
        data = request.get_json()
        print(f"Received data: {data}")
        
        # Extract whatever data is available
        company_name = data.get('company_name', 'Unknown Company')
        industry = data.get('industry', 'Unknown Industry')
        
        print(f"Extracted values:")
        print(f"  company_name: {company_name}")
        print(f"  industry: {industry}")
        
        # Use company name if available, otherwise try to get from existing company data
        if not company_name or company_name == 'Unknown Company':
            # Try to get company info from existing data
            companies = load_companies()
            if companies:
                # Use the first available company
                company_name = companies[0]['name']
                industry = companies[0].get('industry', 'Unknown Industry')
                print(f"Using existing company: {company_name} in {industry}")
        
        print("Calling generate_market_analysis...")
        
        # Generate market analysis
        result = generate_market_analysis(company_name, industry)
        
        print(f"Market analysis result: {result.get('success', False)}")
        
        if result['success']:
            # Save market analysis to company data
            companies = load_companies()
            company = next((c for c in companies if c['name'].lower() == company_name.lower()), None)
            
            if company:
                if 'market_analysis' not in company:
                    company['market_analysis'] = []
                company['market_analysis'].append({
                    "content": result['content'],
                    "created_at": datetime.now().isoformat()
                })
                save_companies(companies)
                print(f"Saved market analysis to company data")
            else:
                print(f"Company {company_name} not found in companies list")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_market endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/personas/generate', methods=['POST'])
def generate_personas():
    """Generate buyer personas for a company"""
    try:
        print("=== Persona Generation Request ===")
        data = request.get_json()
        print(f"Received data: {data}")
        
        # Extract whatever data is available
        company_name = data.get('company_name', 'Unknown Company')
        industry = data.get('industry', 'Unknown Industry')
        scraped_content = data.get('scraped_content')
        ai_research = data.get('ai_research')
        
        print(f"Extracted values:")
        print(f"  company_name: {company_name}")
        print(f"  industry: {industry}")
        print(f"  scraped_content: {bool(scraped_content)}")
        print(f"  ai_research: {bool(ai_research)}")
        
        # Use company name if available, otherwise try to get from existing company data
        if not company_name or company_name == 'Unknown Company':
            # Try to get company info from existing data
            companies = load_companies()
            if companies:
                # Use the first available company
                company_name = companies[0]['name']
                industry = companies[0].get('industry', 'Unknown Industry')
                print(f"Using existing company: {company_name} in {industry}")
        
        print("Calling generate_buyer_personas...")
        
        # Use the new centralized persona customization system
        result = customize_personas_for_company(company_name, industry, None, scraped_content, ai_research)
        
        print(f"Persona customization result: {result.get('success', False)}")
        
        if result['success']:
            # Save personas to company data
            companies = load_companies()
            company = next((c for c in companies if c['name'].lower() == company_name.lower()), None)
            
            if company:
                if 'personas' not in company:
                    company['personas'] = []
                company['personas'].extend(result['personas'])
                save_companies(companies)
                print(f"Saved {len(result['personas'])} personas to company data")
            else:
                print(f"Company {company_name} not found in companies list")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in generate_personas endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/personas/<company_name>', methods=['GET'])
def get_personas(company_name):
    """Get buyer personas for a company"""
    try:
        companies = load_companies()
        company = next((c for c in companies if c['name'].lower() == company_name.lower()), None)
        
        if not company:
            return jsonify({"error": "Company not found"}), 404
        
        personas = company.get('personas', [])
        return jsonify(personas)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load_core_personas():
    """Load the core persona library"""
    try:
        core_personas_path = os.path.join(DATA_DIR, "core_personas.json")
        if os.path.exists(core_personas_path):
            with open(core_personas_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading core personas: {str(e)}")
        return None

def customize_personas_for_company(company_name, industry, company_stage=None, scraped_content=None, ai_research=None):
    """Customize core personas for a specific company based on context"""
    try:
        print(f"Customizing personas for {company_name} in {industry}")
        
        # Load core personas
        core_data = load_core_personas()
        if not core_data:
            raise Exception("Core personas not found")
        
        # Determine company stage if not provided
        if not company_stage:
            company_stage = determine_company_stage(company_name, industry, scraped_content, ai_research)
        
        # Determine industry category
        industry_category = determine_industry_category(industry)
        
        print(f"Company stage: {company_stage}, Industry category: {industry_category}")
        
        # Get relevant personas for this company
        relevant_personas = select_relevant_personas(industry, company_stage)
        
        # Customize each persona
        customized_personas = []
        for persona_key in relevant_personas:
            base_persona = core_data["personas"][persona_key]
            customized = customize_single_persona(
                base_persona, 
                company_name, 
                industry, 
                company_stage, 
                industry_category,
                scraped_content,
                ai_research
            )
            customized_personas.append(customized)
        
        # Format the output
        output = format_customized_personas(customized_personas, company_name, industry, company_stage)
        
        return {
            "success": True,
            "content": output,
            "personas": customized_personas,
            "company_stage": company_stage,
            "industry_category": industry_category,
            "confidence_score": 0.95
        }
        
    except Exception as e:
        print(f"Error customizing personas: {str(e)}")
        return {
            "success": False,
            "content": f"Error customizing personas: {str(e)}",
            "model": "unknown",
            "usage": {}
        }

def determine_company_stage(company_name, industry, scraped_content=None, ai_research=None):
    """Determine company stage based on available information"""
    # Simple heuristic - could be enhanced with AI analysis
    if scraped_content and ai_research:
        content = f"{scraped_content} {ai_research}".lower()
        if any(word in content for word in ["startup", "seed", "series a", "early stage"]):
            return "startup"
        elif any(word in content for word in ["growth", "series b", "series c", "scaling"]):
            return "growth"
        elif any(word in content for word in ["enterprise", "public", "fortune", "global"]):
            return "enterprise"
    
    # Default based on industry
    if industry.lower() in ["predictive procurement software", "enterprise software"]:
        return "growth"  # Most enterprise software companies are growth stage
    return "growth"

def determine_industry_category(industry):
    """Determine industry category for persona customization"""
    industry_lower = industry.lower()
    if any(word in industry_lower for word in ["software", "saas", "tech"]):
        return "saas"
    elif any(word in industry_lower for word in ["manufacturing", "industrial"]):
        return "manufacturing"
    elif any(word in industry_lower for word in ["healthcare", "medical"]):
        return "healthcare"
    elif any(word in industry_lower for word in ["financial", "banking", "insurance"]):
        return "financial_services"
    return "saas"  # Default

def select_relevant_personas(industry, company_stage):
    """Select which personas are most relevant for this company"""
    # Base personas that are always relevant
    base_personas = ["cio_cto", "vp_operations"]
    
    # Add industry-specific personas
    if "procurement" in industry.lower():
        base_personas.append("procurement_manager")
    
    # Add stage-specific personas
    if company_stage == "startup":
        base_personas.extend(["cfo", "end_user_champion"])
    elif company_stage == "growth":
        base_personas.extend(["cfo", "it_director", "procurement_manager"])
    elif company_stage == "enterprise":
        base_personas.extend(["cfo", "it_director", "procurement_manager"])
    
    return base_personas

def customize_single_persona(base_persona, company_name, industry, company_stage, industry_category, scraped_content=None, ai_research=None):
    """Customize a single persona with company-specific context"""
    core_data = load_core_personas()
    
    # Start with base persona
    customized = base_persona.copy()
    
    # Add industry-specific modifiers
    if industry_category in core_data["industry_modifiers"]:
        industry_mod = core_data["industry_modifiers"][industry_category]
        customized["priorities"] = base_persona["core_priorities"] + industry_mod["priority_additions"]
        customized["pain_points"] = base_persona["core_pain_points"] + industry_mod["pain_point_additions"]
        customized["decision_criteria"] = base_persona["core_decision_criteria"] + industry_mod["decision_criteria_additions"]
    else:
        customized["priorities"] = base_persona["core_priorities"]
        customized["pain_points"] = base_persona["core_pain_points"]
        customized["decision_criteria"] = base_persona["core_decision_criteria"]
    
    # Add stage-specific modifiers
    if company_stage in core_data["company_stage_modifiers"]:
        stage_mod = core_data["company_stage_modifiers"][company_stage]
        customized["priorities"].extend(stage_mod["priority_additions"])
        customized["pain_points"].extend(stage_mod["pain_point_additions"])
        customized["decision_criteria"].extend(stage_mod["decision_criteria_additions"])
    
    # Add company-specific context
    customized["company_name"] = company_name
    customized["industry"] = industry
    customized["company_stage"] = company_stage
    customized["created_at"] = datetime.now().isoformat()
    customized["id"] = str(uuid.uuid4())
    
    return customized

def format_customized_personas(personas, company_name, industry, company_stage):
    """Format customized personas into strategic, actionable narratives"""
    output = f"🎯 STRATEGIC PERSONA ANALYSIS FOR {company_name.upper()}\n"
    output += f"Industry: {industry} | Stage: {company_stage.title()}\n\n"
    
    # Add strategic context
    core_data = load_core_personas()
    if core_data:
        industry_context = core_data["industry_modifiers"].get(determine_industry_category(industry), {}).get("land_expand_context", "")
        stage_context = core_data["company_stage_modifiers"].get(company_stage, {}).get("land_expand_context", "")
        
        if industry_context or stage_context:
            output += "📊 STRATEGIC CONTEXT:\n"
            if industry_context:
                output += f"• Industry Focus: {industry_context}\n"
            if stage_context:
                output += f"• Stage Strategy: {stage_context}\n"
            output += "\n"
    
    # Add land-and-expand roadmap
    output += "🗺️ LAND-AND-EXPAND ROADMAP:\n"
    output += "Based on market research and company analysis, here's your strategic approach:\n\n"
    
    for i, persona in enumerate(personas):
        output += f"👤 PERSONA {i+1}: {persona['base_role']}\n"
        output += f"Department: {persona['department']}\n"
        output += f"Land & Expand Strategy: {persona['land_expand_strategy']}\n\n"
        
        output += f"🎯 WHY THIS PERSONA MATTERS:\n"
        output += f"• {persona['sales_approach']}\n"
        output += f"• {persona['expansion_opportunities']}\n\n"
        
        output += f"🔍 CHAMPION INDICATORS:\n"
        for indicator in persona.get('champion_indicators', []):
            output += f"• {indicator}\n"
        output += "\n"
        
        output += f"🚀 EXPANSION PATHS:\n"
        for path in persona.get('expansion_paths', []):
            output += f"• {path}\n"
        output += "\n"
        
        output += f"📋 CUSTOMIZED INSIGHTS:\n"
        output += f"Priorities:\n"
        for priority in persona['priorities']:
            output += f"• {priority}\n"
        output += f"\nPain Points:\n"
        for pain in persona['pain_points']:
            output += f"• {pain}\n"
        output += f"\nDecision Criteria:\n"
        for criteria in persona['decision_criteria']:
            output += f"• {criteria}\n"
        output += f"\n"
        
        output += f"💼 SALES APPROACH:\n"
        output += f"{persona['sales_approach']}\n\n"
        
        output += f"🔗 EXPANSION OPPORTUNITIES:\n"
        output += f"{persona['expansion_opportunities']}\n\n"
        
        output += f"📊 INFLUENCE & AUTHORITY:\n"
        output += f"• Influence Level: {persona['influence_level']}\n"
        output += f"• Budget Authority: {persona['budget_authority']}\n"
        output += f"• Technical Expertise: {persona['technical_expertise']}\n\n"
        
        output += "─" * 80 + "\n\n"
    
    # Add strategic recommendations
    output += "🎯 STRATEGIC RECOMMENDATIONS:\n"
    output += "Based on this analysis:\n\n"
    
    # Identify primary champion
    primary_champion = next((p for p in personas if p['influence_level'] == 'high' and p['budget_authority'] == 'high'), None)
    if primary_champion:
        output += f"1. 🎯 PRIMARY CHAMPION: {primary_champion['base_role']}\n"
        output += f"   Start here - they have the influence and budget to drive adoption.\n\n"
    
    # Identify operational champions
    operational_champions = [p for p in personas if 'operations' in p['department'].lower()]
    if operational_champions:
        output += f"2. 🔧 OPERATIONAL CHAMPIONS: {', '.join([p['base_role'] for p in operational_champions])}\n"
        output += f"   These personas feel the daily pain and can demonstrate immediate value.\n\n"
    
    # Identify expansion targets
    expansion_targets = [p for p in personas if p['influence_level'] == 'medium' and p['budget_authority'] == 'medium']
    if expansion_targets:
        output += f"3. 🚀 EXPANSION TARGETS: {', '.join([p['base_role'] for p in expansion_targets])}\n"
        output += f"   Once you have champions, expand to these personas for broader adoption.\n\n"
    
    output += "💡 NEXT STEPS:\n"
    output += "1. Identify your current champion or primary contact\n"
    output += "2. Use the customized insights to tailor your pitch\n"
    output += "3. Focus on the expansion paths to grow your footprint\n"
    output += "4. Leverage industry and stage context for positioning\n\n"
    
    return output

def export_crm_ready_data(personas, company_name, industry, company_stage):
    """Export personas in CRM-ready format for future integration"""
    crm_data = {
        "company": {
            "name": company_name,
            "industry": industry,
            "stage": company_stage,
            "analysis_date": datetime.now().isoformat(),
            "land_expand_status": "research_completed"
        },
        "personas": [],
        "land_expand_opportunities": [],
        "champion_identification": [],
        "expansion_paths": []
    }
    
    for persona in personas:
        # CRM-ready persona record
        crm_persona = {
            "id": persona["id"],
            "title": persona["base_role"],
            "department": persona["department"],
            "influence_level": persona["influence_level"],
            "budget_authority": persona["budget_authority"],
            "technical_expertise": persona["technical_expertise"],
            "land_expand_strategy": persona["land_expand_strategy"],
            "champion_indicators": persona["champion_indicators"],
            "expansion_paths": persona["expansion_paths"],
            "priorities": persona["priorities"],
            "pain_points": persona["pain_points"],
            "decision_criteria": persona["decision_criteria"],
            "sales_approach": persona["sales_approach"],
            "expansion_opportunities": persona["expansion_opportunities"],
            "crm_fields": {
                "lead_source": "ai_analysis",
                "lead_score": calculate_lead_score(persona),
                "next_action": determine_next_action(persona),
                "expansion_potential": calculate_expansion_potential(persona),
                "champion_likelihood": calculate_champion_likelihood(persona)
            }
        }
        crm_data["personas"].append(crm_persona)
        
        # Land and expand opportunities
        if persona["influence_level"] == "high" and persona["budget_authority"] == "high":
            crm_data["land_expand_opportunities"].append({
                "persona_id": persona["id"],
                "opportunity_type": "primary_champion",
                "priority": "high",
                "description": f"Primary expansion target - {persona['land_expand_strategy']}"
            })
        
        # Champion identification
        for indicator in persona["champion_indicators"]:
            crm_data["champion_identification"].append({
                "persona_id": persona["id"],
                "indicator": indicator,
                "assessment": "needs_validation"
            })
        
        # Expansion paths
        for path in persona["expansion_paths"]:
            crm_data["expansion_paths"].append({
                "from_persona_id": persona["id"],
                "to_persona": path,
                "relationship_type": "influence_path",
                "expansion_stage": "identified"
            })
    
    return crm_data

def calculate_lead_score(persona):
    """Calculate lead score based on persona characteristics"""
    score = 0
    
    # Influence level scoring
    if persona["influence_level"] == "high":
        score += 30
    elif persona["influence_level"] == "medium":
        score += 20
    else:
        score += 10
    
    # Budget authority scoring
    if persona["budget_authority"] == "high":
        score += 25
    elif persona["budget_authority"] == "medium":
        score += 15
    else:
        score += 5
    
    # Technical expertise scoring
    if persona["technical_expertise"] == "high":
        score += 20
    elif persona["technical_expertise"] == "medium":
        score += 15
    else:
        score += 10
    
    # Department scoring
    if "executive" in persona["department"].lower():
        score += 15
    elif "operations" in persona["department"].lower():
        score += 10
    
    return min(score, 100)  # Cap at 100

def determine_next_action(persona):
    """Determine the next action for this persona"""
    if persona["influence_level"] == "high" and persona["budget_authority"] == "high":
        return "schedule_executive_demo"
    elif persona["influence_level"] == "high":
        return "schedule_technical_demo"
    elif "operations" in persona["department"].lower():
        return "schedule_process_review"
    else:
        return "schedule_intro_call"

def calculate_expansion_potential(persona):
    """Calculate expansion potential score"""
    potential = 0
    
    # More expansion paths = higher potential
    potential += len(persona["expansion_paths"]) * 10
    
    # Higher influence = higher expansion potential
    if persona["influence_level"] == "high":
        potential += 30
    elif persona["influence_level"] == "medium":
        potential += 20
    
    # Operations roles have high expansion potential
    if "operations" in persona["department"].lower():
        potential += 20
    
    return min(potential, 100)

def calculate_champion_likelihood(persona):
    """Calculate likelihood of becoming a champion"""
    likelihood = 50  # Base 50%
    
    # High influence + budget = more likely champion
    if persona["influence_level"] == "high" and persona["budget_authority"] == "high":
        likelihood += 25
    
    # Operations roles often become champions
    if "operations" in persona["department"].lower():
        likelihood += 15
    
    # Technical roles can become champions
    if persona["technical_expertise"] == "high":
        likelihood += 10
    
    return min(likelihood, 100)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

