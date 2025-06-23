import json
import yaml
from typing import Any, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

class OutputFormatter:
    """Format output for your AWS GenAI Bot API responses"""
    
    @staticmethod
    def format_generation_response(result: Dict[str, Any], format_type: str = 'text') -> str:
        """Format text generation response from your API"""
        if not result.get('success'):
            # Handle different types of errors
            error_msg = result.get('error', 'Unknown error')
            details = result.get('details', {})
            message = result.get('message', '')
            
            if details:
                # Content policy violation or detailed error
                error_output = f"Error: {error_msg}"
                if message:
                    error_output += f"\nMessage: {message}"
                if details.get('severity'):
                    error_output += f"\nSeverity: {details['severity']}"
                return error_output
            else:
                return f"Error: {error_msg}"
        
        data = result['data']
        generated_text = data.get('generated_text', '')
        metadata = data.get('metadata', {})
        
        if format_type == 'json':
            return json.dumps(data, indent=2)
        elif format_type == 'yaml':
            return yaml.dump(data, default_flow_style=False)
        elif format_type == 'rich':
            OutputFormatter._display_generation_rich(generated_text, metadata)
            return ""
        else:  # text format
            output = generated_text
            if metadata:
                output += "\n\n--- Response Details ---"
                for key, value in metadata.items():
                    formatted_key = key.replace('_', ' ').title()
                    output += f"\n{formatted_key}: {value}"
            return output
    
    @staticmethod
    def format_usage_stats(result: Dict[str, Any], format_type: str = 'text') -> str:
        """Format usage statistics from your API"""
        if not result.get('success'):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        stats = result['data']
        
        if format_type == 'json':
            return json.dumps(stats, indent=2)
        elif format_type == 'yaml':
            return yaml.dump(stats, default_flow_style=False)
        elif format_type == 'rich':
            OutputFormatter._display_usage_rich(stats)
            return ""
        else:  # text format
            output = f"Usage Statistics for {stats.get('user_id', 'Unknown User')}\n"
            output += "=" * 50 + "\n"
            
            # Summary stats
            output += f"Period: {stats.get('period_days', 'N/A')} days\n"
            output += f"Total Requests: {stats.get('total_requests', 0)}\n"
            output += f"Total Input Tokens: {stats.get('total_input_tokens', 0):,}\n"
            output += f"Total Output Tokens: {stats.get('total_output_tokens', 0):,}\n"
            output += f"Average Response Time: {stats.get('average_response_time_ms', 0)}ms\n"
            output += f"Content Filter Events: {stats.get('content_filter_events', 0)}\n"
            output += f"Status: {stats.get('status', 'Unknown')}\n"
            output += f"Last Request: {stats.get('last_request', 'N/A')}\n"
            
            # Daily breakdown
            requests_by_day = stats.get('requests_by_day', [])
            if requests_by_day:
                output += "\nDaily Breakdown:\n"
                for day_stats in requests_by_day:
                    output += f"  {day_stats['date']}: {day_stats['requests']} requests, {day_stats['tokens']} tokens\n"
            
            return output
    
    @staticmethod
    def _display_generation_rich(generated_text: str, metadata: Dict[str, Any]) -> None:
        """Display generation response with rich formatting"""
        # Main response panel
        response_text = Text(generated_text)
        panel = Panel(
            response_text,
            title="Generated Text",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
        
        # Metadata table
        if metadata:
            table = Table(title="Response Metadata", show_header=True)
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            
            for key, value in metadata.items():
                formatted_key = key.replace('_', ' ').title()
                
                # Special formatting for certain fields
                if 'tokens' in key.lower():
                    formatted_value = f"{value:,}" if isinstance(value, (int, float)) else str(value)
                elif 'time' in key.lower() and 'ms' in str(value):
                    formatted_value = f"{value}ms"
                elif key == 'mock_mode':
                    formatted_value = "🔄 Mock Mode" if value else "✅ Real Mode"
                else:
                    formatted_value = str(value)
                
                table.add_row(formatted_key, formatted_value)
            
            console.print(table)
    
    @staticmethod
    def _display_usage_rich(stats: Dict[str, Any]) -> None:
        """Display usage statistics with rich formatting"""
        # Header
        user_id = stats.get('user_id', 'Unknown User')
        console.print(f"\n[bold cyan]Usage Statistics for {user_id}[/bold cyan]")
        
        # Summary table
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_items = [
            ("Period", f"{stats.get('period_days', 'N/A')} days"),
            ("Total Requests", f"{stats.get('total_requests', 0):,}"),
            ("Input Tokens", f"{stats.get('total_input_tokens', 0):,}"),
            ("Output Tokens", f"{stats.get('total_output_tokens', 0):,}"),
            ("Avg Response Time", f"{stats.get('average_response_time_ms', 0)}ms"),
            ("Filter Events", str(stats.get('content_filter_events', 0))),
            ("Status", stats.get('status', 'Unknown')),
            ("Last Request", stats.get('last_request', 'N/A'))
        ]
        
        for metric, value in summary_items:
            summary_table.add_row(metric, value)
        
        console.print(summary_table)
        
        # Daily breakdown
        requests_by_day = stats.get('requests_by_day', [])
        if requests_by_day:
            daily_table = Table(title="Daily Breakdown")
            daily_table.add_column("Date", style="cyan")
            daily_table.add_column("Requests", style="white", justify="right")
            daily_table.add_column("Tokens", style="white", justify="right")
            
            for day_stats in requests_by_day:
                daily_table.add_row(
                    day_stats['date'],
                    str(day_stats['requests']),
                    f"{day_stats['tokens']:,}"
                )
            
            console.print(daily_table)