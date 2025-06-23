import re
import json
from typing import Dict, List, Tuple
import boto3

class ContentFilter:
    def __init__(self):
        self.comprehend = boto3.client('comprehend')
        self.blocked_patterns = [
            r'\b(?:violence|hate|harmful)\b',
            r'\b(?:illegal|drug)\b',
            # Add more patterns as needed
        ]
        
    def filter_content(self, text: str) -> Dict:
        """
        Filter content using AWS Comprehend and custom rules
        Returns: {"is_safe": bool, "filtered_text": str, "reasons": []}
        """
        result = {
            "is_safe": True,
            "filtered_text": text,
            "reasons": []
        }
        
        # 1. Check custom patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result["is_safe"] = False
                result["reasons"].append(f"Contains blocked pattern: {pattern}")
        
        # 2. Use AWS Comprehend for sentiment analysis
        try:
            sentiment_response = self.comprehend.detect_sentiment(
                Text=text[:5000],  # Comprehend limit
                LanguageCode='en'
            )
            
            if sentiment_response['Sentiment'] == 'NEGATIVE':
                confidence = sentiment_response['SentimentScore']['Negative']
                if confidence > 0.8:  # High confidence negative
                    result["is_safe"] = False
                    result["reasons"].append(f"High negative sentiment: {confidence:.2f}")
                    
        except Exception as e:
            print(f"Comprehend error: {str(e)}")
            # Don't block on service errors
        
        # 3. Apply content filtering if needed
        if not result["is_safe"]:
            result["filtered_text"] = "[Content filtered due to policy violations]"
            
        return result