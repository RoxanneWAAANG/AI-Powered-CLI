import click
from cli.config import CLIConfig
from cli.utils.logger import setup_logging, get_logger
from cli.commands import generate, batch, usage, config

# Initialize configuration
config_obj = CLIConfig()
setup_logging(config_obj.get('log_level', 'INFO'))

@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    """AWS GenAI Bot CLI - Command-line interface for your text generation service
    
    A powerful command-line tool to interact with your deployed AWS GenAI Bot API.
    Generate text, process batches, monitor usage, and manage configuration.
    
    Quick Start:
      genai config test              # Test your API connection
      genai generate text "Hello"    # Generate text
      genai usage stats              # Check usage statistics
      genai generate interactive     # Start interactive session
    
    For detailed help on any command, use: genai COMMAND --help
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = config_obj

# Register command groups
cli.add_command(generate.generate)
cli.add_command(batch.batch)
cli.add_command(usage.usage)
cli.add_command(config.config_cmd)

# Add some helpful standalone commands
@cli.command()
@click.pass_context
def status(ctx):
    """Check API status and show quick information"""
    from cli.client import GenAIClient
    
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    click.echo("🤖 AWS GenAI Bot CLI Status")
    click.echo("=" * 40)
    
    # Configuration info
    api_endpoint = config.get('api_endpoint')
    user_id = config.get('default_user_id')
    click.echo(f"API Endpoint: {api_endpoint}")
    click.echo(f"User ID: {user_id}")
    
    # Test connection
    click.echo("\nTesting API connection...")
    if client.health_check():
        click.echo("API is accessible")
        
        # Quick usage stats
        stats_result = client.get_usage_stats(user_id, 7)
        if stats_result.get('success'):
            stats = stats_result['data']
            click.echo(f"Requests (7 days): {stats.get('total_requests', 0)}")
            click.echo(f"Total tokens: {stats.get('total_input_tokens', 0) + stats.get('total_output_tokens', 0)}")
    else:
        click.echo("API connection failed")
        click.echo("Run 'genai config test' for detailed diagnostics")

@cli.command()
@click.argument('prompt')
@click.pass_context  
def quick(ctx, prompt):
    """Quick text generation (shorthand for 'generate text')
    
    Example:
      genai quick "Write a haiku about coding"
    """
    from cli.client import GenAIClient
    
    config = ctx.obj['config']
    client = GenAIClient(config)

    result = client.generate_text(prompt)
    
    if result.get('success'):
        generated_text = result['data']['generated_text']
        click.echo(generated_text)
        
        # Show brief metadata
        metadata = result['data'].get('metadata', {})
        if metadata.get('mock_mode'):
            click.echo("\nℹ️  (Mock mode - enable Bedrock for real AI responses)")
    else:
        click.echo(f"Error: {result.get('error')}", err=True)

if __name__ == '__main__':
    cli()