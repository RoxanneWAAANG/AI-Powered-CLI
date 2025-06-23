import json
import boto3
import time
from typing import Dict, Any

# Set this to True once you have Bedrock access enabled
USE_BEDROCK = False

def content_filter_check(prompt: str) -> Dict[str, Any]:
    """Content filtering logic that works in both mock and real modes"""
    
    # Define harmful patterns
    harmful_patterns = [
        'harmful', 'violent', 'abuse', 'illegal', 'hate', 'discriminatory',
        'dangerous', 'toxic', 'offensive', 'inappropriate', 'explicit'
    ]
    
    prompt_lower = prompt.lower()
    
    # Check for harmful patterns
    detected_patterns = [pattern for pattern in harmful_patterns if pattern in prompt_lower]
    
    if detected_patterns:
        return {
            'blocked': True,
            'reason': 'Content policy violation',
            'detected_patterns': detected_patterns,
            'severity': 'HIGH' if len(detected_patterns) > 2 else 'MEDIUM'
        }
    
    return {'blocked': False, 'severity': 'LOW'}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Text generation handler with Bedrock toggle"""
    
    try:
        # Debug: Print the entire event to CloudWatch logs
        print(f"Event received: {json.dumps(event)}")
        
        # Parse request - handle both direct invocation and API Gateway
        body_str = event.get('body')
        if body_str is None:
            body = event
        else:
            body = json.loads(body_str)
            
        prompt = body.get('prompt', body.get('message', ''))
        max_tokens = body.get('max_tokens', 1000)
        temperature = body.get('temperature', 0.7)
        user_id = body.get('user_id', 'anonymous')
        
        if not prompt:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Prompt is required'})
            }
        
        # Content filtering check (works in both mock and real modes)
        filter_result = content_filter_check(prompt)
        
        if filter_result['blocked']:
            # Log security event
            print(f"SECURITY ALERT: Content blocked for user {user_id}: {filter_result}")
            
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Content policy violation detected',
                    'details': {
                        'reason': filter_result['reason'],
                        'severity': filter_result['severity'],
                        'user_id': user_id,
                        'timestamp': int(time.time())
                    },
                    'message': 'Your request contains content that violates our usage policies. Please modify your prompt and try again.'
                })
            }
        
        if USE_BEDROCK:
            # Real Bedrock call
            try:
                bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
                
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}]
                }
                
                response = bedrock.invoke_model(
                    modelId="anthropic.claude-sonnet-4-20250514-v1:0",
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                generated_text = response_body['content'][0]['text']
                
                # Additional content filtering on output (for real mode)
                output_filter = content_filter_check(generated_text)
                if output_filter['blocked']:
                    print(f"SECURITY ALERT: Output filtered for user {user_id}")
                    generated_text = "I cannot provide that type of content. Please try a different request."
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'generated_text': generated_text,
                        'metadata': {
                            'input_tokens': len(prompt.split()) * 1.3,
                            'output_tokens': len(generated_text.split()) * 1.3,
                            'response_time_ms': 200,
                            'model_id': 'anthropic.claude-sonnet-4-20250514-v1:0',
                            'user_id': user_id,
                            'content_filter_status': 'passed'
                        }
                    })
                }
                
            except Exception as e:
                print(f"Bedrock error: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': f'Bedrock error: {str(e)}'})
                }
        else:
            # Mock response until Bedrock access is enabled
            mock_response = f"[MOCK] AI Generated Response for: '{prompt}'\n\nThis is a simulated Claude 4 Sonnet response. The actual AI response will be much more sophisticated once Bedrock model access is enabled.\n\nParameters used:\n- Max tokens: {max_tokens}\n- Temperature: {temperature}\n- User ID: {user_id}"
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'generated_text': mock_response,
                    'metadata': {
                        'input_tokens': len(prompt.split()),
                        'output_tokens': len(mock_response.split()),
                        'response_time_ms': 50,
                        'mock_mode': True,
                        'user_id': user_id,
                        'content_filter_status': 'passed',
                        'note': 'Enable Bedrock Claude 4 Sonnet access to get real AI responses'
                    }
                })
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def get_usage_stats(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Enhanced usage stats for demo"""
    try:
        user_id = event['pathParameters'].get('user_id', 'anonymous')
        days = event.get('queryStringParameters', {}).get('days', 7) if event.get('queryStringParameters') else 7
        
        # Mock usage data for demo
        mock_stats = {
            'user_id': user_id,
            'period_days': int(days),
            'total_requests': 47,
            'total_input_tokens': 1250,
            'total_output_tokens': 3890,
            'average_response_time_ms': 185,
            'requests_by_day': [
                {'date': '2025-06-22', 'requests': 8, 'tokens': 421},
                {'date': '2025-06-21', 'requests': 12, 'tokens': 587},
                {'date': '2025-06-20', 'requests': 15, 'tokens': 692},
                {'date': '2025-06-19', 'requests': 7, 'tokens': 298},
                {'date': '2025-06-18', 'requests': 5, 'tokens': 201}
            ],
            'content_filter_events': 2,
            'last_request': '2025-06-22T16:45:32Z',
            'status': 'active'
        }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(mock_stats)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }