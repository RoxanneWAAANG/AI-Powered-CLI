import requests
import json
from typing import Dict, Any, Optional
from cli.config import CLIConfig
from cli.utils.logger import get_logger

class GenAIClient:
    """Client for your existing AWS GenAI Bot API"""
    
    def __init__(self, config: CLIConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.base_url = config.get('api_endpoint', 'https://2i9yquihz5.execute-api.us-east-2.amazonaws.com/Prod')
        self.timeout = config.get('timeout', 30)
    
    def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using your existing /generate endpoint"""
        url = f"{self.base_url}/generate"
        
        payload = {
            'prompt': prompt,
            'max_tokens': kwargs.get('max_tokens', self.config.get('default_max_tokens', 1000)),
            'temperature': kwargs.get('temperature', self.config.get('default_temperature', 0.7)),
            'user_id': kwargs.get('user_id', self.config.get('default_user_id', 'cli_user'))
        }
        
        try:
            self.logger.info(f"Sending request to {url}")
            self.logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Response body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info("Text generation successful")
                return {
                    'success': True,
                    'data': result,
                    'status_code': response.status_code
                }
            elif response.status_code == 400:
                # Handle content policy violations and other client errors
                error_data = response.json()
                self.logger.warning(f"Client error: {error_data}")
                return {
                    'success': False,
                    'error': error_data.get('error', 'Bad request'),
                    'details': error_data.get('details', {}),
                    'message': error_data.get('message', ''),
                    'status_code': response.status_code
                }
            else:
                error_data = response.json() if response.content else {}
                self.logger.error(f"API error: {response.status_code} - {error_data}")
                return {
                    'success': False,
                    'error': error_data.get('error', 'Unknown API error'),
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            self.logger.error("API request timeout")
            return {
                'success': False,
                'error': 'Request timeout - API took too long to respond',
                'status_code': 408
            }
        except requests.exceptions.ConnectionError:
            self.logger.error("API connection error")
            return {
                'success': False,
                'error': 'Connection error - Could not reach API',
                'status_code': 503
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}',
                'status_code': 500
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'status_code': 500
            }
    
    def get_usage_stats(self, user_id: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Get usage statistics using your existing /usage endpoint"""
        user_id = user_id or self.config.get('default_user_id', 'cli_user')
        url = f"{self.base_url}/usage/{user_id}"
        
        params = {'days': days} if days != 7 else {}
        
        try:
            self.logger.info(f"Fetching usage stats for user: {user_id}")
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'status_code': response.status_code
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('error', 'Could not fetch usage statistics'),
                    'status_code': response.status_code
                }
        except Exception as e:
            self.logger.error(f"Error fetching usage stats: {str(e)}")
            return {
                'success': False,
                'error': f'Error fetching stats: {str(e)}',
                'status_code': 500
            }
    
    def health_check(self) -> bool:
        """Check if your API is accessible"""
        try:
            # Simple test with a basic prompt
            result = self.generate_text("test", max_tokens=10)
            return result['success']
        except:
            return False