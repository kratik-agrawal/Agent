# AI Sales Pitch Customization Agent

A web application that helps customize sales pitches for different buyer personas within target companies using web scraping and AI-powered research.

## Features

- **Manual Pitch Input**: Enter company information and pitch content manually
- **Web Scraping**: Automatically scrape company websites for pitch content using Firecrawl
- **AI Research**: Leverage Perplexity AI for comprehensive company research and market intelligence
- **Prompt Management**: Create, edit, and manage AI prompts for different research tasks
- **Company Management**: Track and manage companies and their associated pitch data
- **Real-time Status**: Monitor scraping job progress in real-time
- **Dual Source Intelligence**: Combine web scraping with AI research for comprehensive insights

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Firecrawl API key
- Perplexity API key

### Backend Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. API keys are already configured in `api/api.py`:
   - Firecrawl API key: `fc-9293d60703d44e69ba17c0ced291f8aa`
   - Perplexity API key: `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`

3. Start the Flask backend:
   ```bash
   cd api
   python api.py
   ```

The backend will run on `http://127.0.0.1:5000`

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will run on `http://localhost:3000`

## Usage

### Testing the API

Run the test script to verify all endpoints are working:

```bash
python test_api.py
```

### Testing Perplexity Integration

Test the new AI research capabilities:

```bash
python test_perplexity_integration.py
```

### Manual Pitch Input

1. Fill in the company name, industry, and pitch content
2. Click "Submit Pitch"
3. The pitch will be stored and associated with the company

### Web Scraping with AI Research

1. Enter the company website URL (must start with http:// or https://)
2. Enter the company name
3. Click "Start Scraping"
4. The system will:
   - Scrape the website using Firecrawl
   - Research the company using Perplexity AI
   - Combine both sources for comprehensive insights
5. Monitor the job status in the "Scraping Jobs" section
6. Once completed, both scraped data and AI research will be available

### AI Research Only

Get AI-powered company research without web scraping:

```bash
curl http://localhost:5000/api/research/company/CompanyName
```

### Prompt Management

Manage AI prompts for different research tasks:

- **List prompts**: `GET /api/prompts`
- **Get prompt**: `GET /api/prompts/{prompt_name}`
- **Update prompt**: `POST /api/prompts/{prompt_name}`
- **Delete prompt**: `DELETE /api/prompts/{prompt_name}`

### Monitoring Jobs

- Jobs show real-time status updates
- Failed jobs display error messages
- Completed jobs show content summaries and AI research
- Status is automatically checked every 10 seconds

## API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/test/firecrawl` - Test Firecrawl connectivity
- `GET /api/test/perplexity` - Test Perplexity API connectivity
- `POST /api/pitch/ingest/manual` - Submit manual pitch
- `POST /api/pitch/ingest/scrape` - Start scraping job
- `GET /api/pitch/ingest/scrape/<job_id>/status` - Check job status
- `GET /api/pitch/companies` - Get all companies

### AI Research Endpoints
- `GET /api/research/company/<company_name>` - Get AI research for a company
- `GET /api/prompts` - List all prompts
- `GET /api/prompts/<prompt_name>` - Get specific prompt
- `POST /api/prompts/<prompt_name>` - Create/update prompt
- `DELETE /api/prompts/<prompt_name>` - Delete prompt

## AI Research Capabilities

The system now includes comprehensive AI research powered by Perplexity:

### Sales Research Prompt
- Company overview and size information
- Products & services analysis
- Target customer identification
- Pain point analysis
- Competitive landscape
- Recent developments
- Industry trends
- Sales opportunities
- Conversation starters

### Dual Source Intelligence
1. **Firecrawl**: Web scraping for current website content and structure
2. **Perplexity**: AI research for market intelligence and strategic insights
3. **Combined Results**: Comprehensive company profiles with both technical and strategic data

## Prompt Management

### Current Prompts
- `sales_research_prompt.txt` - Comprehensive sales research template

### Creating Custom Prompts
1. Create a new `.txt` file in the `api/prompts/` directory
2. Use the API endpoints to manage and test your prompts
3. Integrate custom prompts into your workflow

### Best Practices
- Use clear, specific instructions
- Include placeholders for dynamic content (e.g., `[COMPANY_NAME]`)
- Test prompts with the API before production use
- Version control your prompts for tracking changes

## Examples

See `api/prompts/example_usage.py` for practical examples of:
- Company research workflows
- Prompt management
- Custom prompt creation
- Full scraping with AI research

## Troubleshooting

### Common Issues

1. **Firecrawl API errors**: Check your API key and ensure you have sufficient credits
2. **Perplexity API errors**: Verify API key and check rate limits
3. **Scraping timeouts**: Some websites may take longer to scrape, adjust the timeout in the code
4. **CORS errors**: Ensure the backend is running and accessible from the frontend
5. **Prompt errors**: Check prompt syntax and ensure placeholders are properly formatted

### Testing

Run the comprehensive test suite:

```bash
# Test basic API functionality
python test_api.py

# Test Perplexity integration and prompt management
python test_perplexity_integration.py

# Run examples
python api/prompts/example_usage.py
```
