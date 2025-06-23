import pytest
from unittest.mock import Mock, patch
from cli.client import GenAIClient
from cli.config import CLIConfig

class TestGenAIClient:
    def setup_method(self):
        self.config = CLIConfig()
        self.client = GenAIClient(self.config)
    
    @patch('boto3.client')
    def test_generate_text_success(self, mock_boto3):
        """Test successful text generation via Lambda"""
        # Mock successful Lambda response
        mock_lambda = Mock()
        mock_lambda.invoke.return_value = {
            'StatusCode': 200,
            'Payload': Mock()
        }
        mock_lambda.invoke.return_value['Payload'].read.return_value = b'{"response": "Test response"}'
        mock_boto3.return_value = mock_lambda
        
        client = GenAIClient(self.config)
        result = client.generate_text('test message')
        
        assert result['success'] == True
        assert 'response' in result['data']
    
    @patch('boto3.client')
    def test_generate_text_error(self, mock_boto3):
        """Test Lambda error handling"""
        # Mock error response
        mock_lambda = Mock()
        mock_lambda.invoke.return_value = {
            'StatusCode': 400,
            'Payload': Mock()
        }
        mock_lambda.invoke.return_value['Payload'].read.return_value = b'{"error": "Bad request"}'
        mock_boto3.return_value = mock_lambda
        
        client = GenAIClient(self.config)
        result = client.generate_text('test message')
        
        assert result['success'] == False
        assert 'error' in result['error']
    
    @patch('requests.post')
    def test_generate_via_api_success(self, mock_post):
        """Test successful text generation via API"""
        # Configure API endpoint
        self.config.set('api_endpoint', 'https://example.com/api')
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': 'Test response'}
        mock_post.return_value = mock_response
        
        result = self.client.generate_via_api('test message')
        
        assert result['success'] == True
        assert 'Test response' in result['data']['response']
    
    @patch('requests.post')
    def test_generate_via_api_error(self, mock_post):
        """Test API error handling"""
        # Configure API endpoint
        self.config.set('api_endpoint', 'https://example.com/api')
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Bad request'}
        mock_post.return_value = mock_response
        
        result = self.client.generate_via_api('test message')
        
        assert result['success'] == False
        assert 'Bad request' in result['error']
    
    def test_generate_via_api_no_endpoint(self):
        """Test API call without configured endpoint"""
        result = self.client.generate_via_api('test message')
        
        assert result['success'] == False
        assert 'not configured' in result['error']