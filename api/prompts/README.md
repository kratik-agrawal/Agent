# Prompt Management System

This directory contains prompts used by the API for various AI-powered research and analysis tasks.

## Current Prompts

### `sales_research_prompt.txt`
A comprehensive prompt for Perplexity API that generates detailed sales research reports for companies. This prompt instructs the AI to act as a senior sales strategist and deliver structured, actionable insights for sales prospecting.

## API Endpoints

### List Prompts
- **GET** `/api/prompts` - List all available prompts

### Get Prompt
- **GET** `/api/prompts/{prompt_name}` - Get a specific prompt's content

### Update/Create Prompt
- **POST** `/api/prompts/{prompt_name}` - Update or create a prompt
- **Body**: `{"content": "prompt content here"}`

### Delete Prompt
- **DELETE** `/api/prompts/{prompt_name}` - Delete a prompt

## Usage Examples

### Testing Perplexity API
```bash
curl http://localhost:5000/api/test/perplexity
```

### Research a Company
```bash
curl http://localhost:5000/api/research/company/Microsoft
```

### Update Sales Research Prompt
```bash
curl -X POST http://localhost:5000/api/prompts/sales_research_prompt \
  -H "Content-Type: application/json" \
  -d '{"content": "Your updated prompt content here"}'
```

## Prompt Structure

Prompts are stored as `.txt` files in this directory. The system automatically loads them when needed and can replace placeholders (like `[INSERT COMPANY NAME HERE]`) with actual values.

## Best Practices

1. **Version Control**: Keep prompts in version control to track changes
2. **Testing**: Test prompts with the `/api/test/perplexity` endpoint
3. **Iteration**: Use the API endpoints to iterate and improve prompts
4. **Documentation**: Document any special placeholders or formatting requirements
5. **Backup**: Keep backups of working prompts before making major changes

## Integration

The prompts are automatically integrated into the scraping workflow:
1. Firecrawl scrapes the company website
2. Perplexity researches the company using the sales research prompt
3. Both results are combined and stored together
4. The combined data provides a comprehensive view of the company

## Customization

To create new prompts:
1. Create a new `.txt` file in this directory
2. Use the API endpoints to manage the prompt
3. Integrate the prompt into your workflow as needed

To modify existing prompts:
1. Use the GET endpoint to view current content
2. Use the POST endpoint to update the content
3. Test the updated prompt with the test endpoints 