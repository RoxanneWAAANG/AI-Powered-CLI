import click
from cli.client import GenAIClient

@click.group()
def usage():
    """Usage statistics and analytics"""
    pass

@usage.command()
@click.option('--user-id', '-u', help='User ID (defaults to configured user)')
@click.option('--days', '-d', default=7, type=int, help='Number of days to analyze (default: 7)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['text', 'json']),
              default='text', help='Output format')
@click.pass_context
def stats(ctx, user_id, days, output_format):
    """Show usage statistics from your AWS GenAI Bot
    
    Examples:
      genai usage stats
      genai usage stats --user-id john_doe --days 30
      genai usage stats --format json
    """
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    target_user_id = user_id or config.get('default_user_id', 'cli_user')
    
    try:
        result = client.get_usage_stats(target_user_id, days)
        
        if result.get('success'):
            stats = result['data']
            
            if output_format == 'json':
                import json
                click.echo(json.dumps(stats, indent=2))
            else:
                # Text format
                click.echo(f"Usage Statistics for {target_user_id}")
                click.echo("=" * 50)
                click.echo(f"Period: {stats.get('period_days', 'N/A')} days")
                click.echo(f"Total Requests: {stats.get('total_requests', 0):,}")
                click.echo(f"Total Input Tokens: {stats.get('total_input_tokens', 0):,}")
                click.echo(f"Total Output Tokens: {stats.get('total_output_tokens', 0):,}")
                click.echo(f"Average Response Time: {stats.get('average_response_time_ms', 0)}ms")
                click.echo(f"Content Filter Events: {stats.get('content_filter_events', 0)}")
                click.echo(f"Status: {stats.get('status', 'Unknown')}")
                click.echo(f"Last Request: {stats.get('last_request', 'N/A')}")
                
                # Daily breakdown
                requests_by_day = stats.get('requests_by_day', [])
                if requests_by_day:
                    click.echo("\nDaily Breakdown:")
                    for day_stats in requests_by_day:
                        click.echo(f"  {day_stats['date']}: {day_stats['requests']} requests, {day_stats['tokens']:,} tokens")
        else:
            click.echo(f"❌ Error fetching usage stats: {result.get('error')}", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)

@usage.command()
@click.option('--user-id', '-u', help='User ID (defaults to configured user)')
@click.option('--days', '-d', default=30, type=int, help='Number of days to analyze (default: 30)')
@click.option('--output', '-o', help='Output file for report')
@click.pass_context
def report(ctx, user_id, days, output):
    """Generate detailed usage report
    
    Examples:
      genai usage report --days 30
      genai usage report --output usage_report.md
      genai usage report --user-id team_bot --days 90 --output team_report.txt
    """
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    target_user_id = user_id or config.get('default_user_id', 'cli_user')
    
    try:
        # Get stats for different time periods
        periods = [1, 7, days] if days > 7 else [1, days]
        report_data = {}
        
        click.echo("📊 Generating usage report...")
        
        for period in periods:
            click.echo(f"  📈 Fetching {period} day statistics...")
            result = client.get_usage_stats(target_user_id, period)
            if result.get('success'):
                report_data[f"{period}_days"] = result['data']
        
        if not report_data:
            click.echo("❌ No data available for report generation", err=True)
            return
        
        # Generate report
        report = generate_usage_report(target_user_id, report_data, days)
        
        if output:
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(report)
                click.echo(f"✅ Report saved to {output}")
            except Exception as e:
                click.echo(f"❌ Error saving report: {e}", err=True)
        else:
            click.echo(report)
            
    except Exception as e:
        click.echo(f"❌ Error generating report: {str(e)}", err=True)

@usage.command()
@click.option('--user-id', '-u', help='User ID (defaults to configured user)')
@click.pass_context
def summary(ctx, user_id):
    """Show quick usage summary
    
    Example:
      genai usage summary
      genai usage summary --user-id team_bot
    """
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    target_user_id = user_id or config.get('default_user_id', 'cli_user')
    
    try:
        result = client.get_usage_stats(target_user_id, 7)
        
        if result.get('success'):
            stats = result['data']
            
            click.echo(f"📊 Quick Summary for {target_user_id}")
            click.echo("=" * 40)
            click.echo(f"🔢 Total Requests (7 days): {stats.get('total_requests', 0):,}")
            click.echo(f"📝 Input Tokens: {stats.get('total_input_tokens', 0):,}")
            click.echo(f"📤 Output Tokens: {stats.get('total_output_tokens', 0):,}")
            click.echo(f"⚡ Avg Response Time: {stats.get('average_response_time_ms', 0)}ms")
            click.echo(f"🛡️  Filter Events: {stats.get('content_filter_events', 0)}")
            click.echo(f"📅 Last Request: {stats.get('last_request', 'N/A')}")
            
            # Status indicator
            status = stats.get('status', 'unknown')
            status_emoji = "✅" if status == 'active' else "⚠️"
            click.echo(f"{status_emoji} Status: {status.title()}")
        else:
            click.echo(f"❌ Error: {result.get('error')}", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)

def generate_usage_report(user_id: str, report_data: dict, max_days: int) -> str:
    """Generate a comprehensive usage report"""
    from datetime import datetime
    
    report = f"# AWS GenAI Bot Usage Report\n\n"
    report += f"**User ID:** {user_id}\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**Report Period:** {max_days} days\n\n"
    
    # Executive Summary
    latest_data = report_data.get(f"{max_days}_days", {})
    if latest_data:
        report += "## Executive Summary\n\n"
        report += f"- **Total Requests:** {latest_data.get('total_requests', 0):,}\n"
        report += f"- **Total Tokens Processed:** {latest_data.get('total_input_tokens', 0) + latest_data.get('total_output_tokens', 0):,}\n"
        report += f"- **Average Response Time:** {latest_data.get('average_response_time_ms', 0)}ms\n"
        report += f"- **Content Filter Events:** {latest_data.get('content_filter_events', 0)}\n"
        report += f"- **Account Status:** {latest_data.get('status', 'Unknown').title()}\n\n"
    
    # Detailed Breakdown
    for period_key, data in report_data.items():
        period_name = period_key.replace('_', ' ').title()
        report += f"## {period_name} Analysis\n\n"
        
        report += f"| Metric | Value |\n"
        report += f"|--------|-------|\n"
        report += f"| Requests | {data.get('total_requests', 0):,} |\n"
        report += f"| Input Tokens | {data.get('total_input_tokens', 0):,} |\n"
        report += f"| Output Tokens | {data.get('total_output_tokens', 0):,} |\n"
        report += f"| Avg Response Time | {data.get('average_response_time_ms', 0)}ms |\n"
        report += f"| Filter Events | {data.get('content_filter_events', 0)} |\n\n"
        
        # Daily breakdown if available
        requests_by_day = data.get('requests_by_day', [])
        if requests_by_day:
            report += f"### Daily Activity ({period_name})\n\n"
            report += f"| Date | Requests | Tokens |\n"
            report += f"|------|----------|--------|\n"
            for day in requests_by_day:
                report += f"| {day['date']} | {day['requests']} | {day['tokens']:,} |\n"
            report += "\n"
    
    # Recommendations
    if latest_data:
        report += "## Recommendations\n\n"
        
        total_requests = latest_data.get('total_requests', 0)
        filter_events = latest_data.get('content_filter_events', 0)
        avg_response_time = latest_data.get('average_response_time_ms', 0)
        
        if total_requests > 1000:
            report += "- High usage detected - consider monitoring costs and implementing rate limiting\n"
        elif total_requests < 10:
            report += "- Low usage - consider promoting the service or checking integration\n"
        
        if filter_events > 0:
            report += f"- {filter_events} content filter events detected - review input guidelines\n"
        
        if avg_response_time > 1000:
            report += "- High response times - monitor API performance\n"
        
        report += "- Regular monitoring recommended for optimal performance\n"
    
    return report