import boto3
import json
from datetime import datetime
from typing import Dict, Any

class UsageMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.dynamodb = boto3.resource('dynamodb')
        # Create usage table if it doesn't exist
        self.usage_table_name = 'TextGenerationUsage'
        
    def log_usage(self, user_id: str, request_data: Dict[str, Any]) -> None:
        """Log usage metrics to CloudWatch and DynamoDB"""
        
        # 1. CloudWatch metrics
        metrics = [
            {
                'MetricName': 'TextGenerationRequests',
                'Value': 1,
                'Unit': 'Count'
            },
            {
                'MetricName': 'InputTokens',
                'Value': request_data.get('input_tokens', 0),
                'Unit': 'Count'
            },
            {
                'MetricName': 'OutputTokens', 
                'Value': request_data.get('output_tokens', 0),
                'Unit': 'Count'
            }
        ]
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace='TextGeneration/Usage',
                MetricData=metrics
            )
        except Exception as e:
            print(f"CloudWatch error: {str(e)}")
        
        # 2. DynamoDB detailed logging
        try:
            table = self.dynamodb.Table(self.usage_table_name)
            table.put_item(
                Item={
                    'user_id': user_id,
                    'timestamp': int(datetime.now().timestamp()),
                    'request_type': request_data.get('type', 'text_generation'),
                    'input_tokens': request_data.get('input_tokens', 0),
                    'output_tokens': request_data.get('output_tokens', 0),
                    'response_time_ms': request_data.get('response_time_ms', 0),
                    'filtered': request_data.get('filtered', False)
                }
            )
        except Exception as e:
            print(f"DynamoDB error: {str(e)}")
    
    def get_usage_stats(self, user_id: str, days: int = 7) -> Dict:
        """Get usage statistics for a user"""
        try:
            table = self.dynamodb.Table(self.usage_table_name)
            # Simple query for recent usage
            response = table.query(
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                ScanIndexForward=False,
                Limit=100
            )
            
            items = response.get('Items', [])
            total_requests = len(items)
            total_tokens = sum(item.get('input_tokens', 0) + item.get('output_tokens', 0) for item in items)
            
            return {
                'total_requests': total_requests,
                'total_tokens': total_tokens,
                'average_tokens_per_request': total_tokens / total_requests if total_requests > 0 else 0
            }
        except Exception as e:
            print(f"Usage stats error: {str(e)}")
            return {'error': str(e)}