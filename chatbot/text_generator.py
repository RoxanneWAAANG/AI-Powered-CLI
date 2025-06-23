import boto3
import json
from typing import Dict, List, Optional

class TextGenerator:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, 
                     temperature: float = 0.7, stop_sequences: List[str] = None) -> Dict:
        """
        Generate text using AWS Bedrock Claude
        """
        try:
            # Prepare the request
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            if stop_sequences:
                request_body["stop_sequences"] = stop_sequences
            
            # Make the request
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            generated_text = response_body['content'][0]['text']
            
            # Calculate tokens (rough estimation)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(generated_text.split()) * 1.3
            
            return {
                "success": True,
                "generated_text": generated_text,
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "model_id": self.model_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "generated_text": "",
                "input_tokens": 0,
                "output_tokens": 0
            }