import requests
from typing import Dict, Any, Optional
from ..config import Config

class PerplexityService:
    """Service for interacting with Perplexity API"""
    
    def __init__(self):
        self.api_key = Config.PERPLEXITY_API_KEY
        self.base_url = Config.PERPLEXITY_BASE_URL
        self.model = Config.PERPLEXITY_MODEL
        self.max_tokens = Config.PERPLEXITY_MAX_TOKENS
        self.temperature = Config.PERPLEXITY_TEMPERATURE
        self.top_p = Config.PERPLEXITY_TOP_P
        
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY is required")
    
    def research_company(self, company_name: str, prompt_template: str) -> Dict[str, Any]:
        """Get company research from Perplexity API"""
        try:
            # Replace placeholder with company name
            prompt = prompt_template.replace("[INSERT COMPANY NAME HERE]", company_name)
            
            # Prepare request data
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract content and usage information
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                usage = result.get('usage', {})
                
                return {
                    "success": True,
                    "content": content,
                    "model": self.model,
                    "usage": usage
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Perplexity API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test request
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Connection successful",
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"API test failed with status {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            } 