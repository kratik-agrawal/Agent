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

# API Keys
PERPLEXITY_API_KEY = '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'
FIRECRAWL_API_KEY = 'fc-9293d60703d44e69ba17c0ced291f8aa'

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
        
        print(f"Making Perplexity API call for company: {company_name}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        print(f"Perplexity API response status: {response.status_code}")
        print(f"Perplexity API response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Perplexity API error response: {response.text}")
            response.raise_for_status()
        
        result = response.json()
        print(f"Perplexity API response: {json.dumps(result, indent=2)}")
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return {
                "success": True,
                "content": content,
                "model": result.get('model', 'unknown'),
                "usage": result.get('usage', {})
            }
        else:
            raise Exception("No content in Perplexity response")
            
    except Exception as e:
        print(f"Perplexity API error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return {
            "success": False,
            "error": str(e)
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
        app = AsyncFirecrawlApp(api_key='fc-9293d60703d44e69ba17c0ced2918aa')
        
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
    """Get Perplexity research for a specific company without scraping"""
    try:
        result = get_perplexity_research(company_name)
        
        if result.get("success"):
            return jsonify({
                "status": "success",
                "company_name": company_name,
                "research": result.get("content"),
                "model": result.get("model", "unknown"),
                "usage": result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "company_name": company_name,
                "error": result.get("error", "Unknown error")
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to research company",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

