import click
from cli.client import GenAIClient

@click.group(name='config')
def config_cmd():
    """Configuration management commands"""
    pass

@config_cmd.command()
@click.pass_context
def show(ctx):
    """Show current configuration"""
    config = ctx.obj['config']
    
    click.echo("🔧 Current Configuration")
    click.echo("=" * 50)
    
    for key, value in config.display().items():
        # Format key nicely
        formatted_key = key.replace('_', ' ').title()
        
        # Show special formatting for certain values
        if key == 'api_endpoint':
            click.echo(f"📡 {formatted_key}: {value}")
        elif key == 'default_user_id':
            click.echo(f"👤 {formatted_key}: {value}")
        elif 'token' in key:
            click.echo(f"🔢 {formatted_key}: {value:,}")
        elif key == 'timeout':
            click.echo(f"⏱️  {formatted_key}: {value}s")
        else:
            click.echo(f"   {formatted_key}: {value}")

@config_cmd.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set(ctx, key, value):
    """Set configuration value
    
    Available configuration keys:
    - api_endpoint: Your AWS API Gateway endpoint
    - default_user_id: Default user ID for tracking
    - default_max_tokens: Default maximum tokens (number)
    - default_temperature: Default temperature 0.0-1.0 (number)
    - output_format: Default output format (text/json)
    - log_level: Logging level (DEBUG/INFO/WARNING/ERROR)
    - timeout: Request timeout in seconds (number)
    
    Examples:
      genai config set api_endpoint https://your-api.amazonaws.com/Prod
      genai config set default_user_id my_team
      genai config set default_max_tokens 1500
      genai config set default_temperature 0.8
    """
    config = ctx.obj['config']
    
    # Validate known keys
    valid_keys = [
        'api_endpoint', 'default_user_id', 'default_max_tokens', 
        'default_temperature', 'output_format', 'log_level', 'timeout'
    ]
    
    if key not in valid_keys:
        click.echo(f"⚠️  Warning: '{key}' is not a recognized configuration key")
        click.echo(f"Valid keys: {', '.join(valid_keys)}")
        if not click.confirm("Continue anyway?"):
            return
    
    # Type conversion for known numeric values
    if key in ['default_max_tokens', 'timeout']:
        value = int(value)
        if key == 'default_max_tokens' and (value < 1 or value > 4000):
            click.echo("❌ Error: max_tokens must be between 1 and 4000", err=True)
            return
        if key == 'timeout' and (value < 1 or value > 300):
            click.echo("❌ Error: timeout must be between 1 and 300 seconds", err=True)
            return
    elif key in ['default_temperature']:
        value = float(value)
        if value < 0.0 or value > 1.0:
            click.echo("❌ Error: temperature must be between 0.0 and 1.0", err=True)
            return
    elif key == 'output_format':
        if value not in ['text', 'json']:
            click.echo("❌ Error: output_format must be one of: text, json", err=True)
            return
    elif key == 'log_level':
        if value.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            click.echo("❌ Error: log_level must be one of: DEBUG, INFO, WARNING, ERROR", err=True)
            return
        value = value.upper()
    
    # Validate API endpoint format
    if key == 'api_endpoint':
        if not value.startswith('https://'):
            click.echo("❌ Error: api_endpoint must start with https://", err=True)
            return
        if not ('amazonaws.com' in value or 'localhost' in value):
            click.echo("⚠️  Warning: API endpoint doesn't look like an AWS API Gateway URL")
            if not click.confirm("Continue anyway?"):
                return
    
    config.set(key, value)
    config.save_config()
    
    click.echo(f"✅ Configuration updated: {key} = {value}")

@config_cmd.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    """Get configuration value
    
    Example:
      genai config get api_endpoint
      genai config get default_user_id
    """
    config = ctx.obj['config']
    value = config.get(key)
    
    if value is not None:
        click.echo(f"{key}: {value}")
    else:
        click.echo(f"❌ Configuration key '{key}' not found", err=True)
        click.echo("Use 'genai config show' to see all available keys")

@config_cmd.command()
@click.pass_context
def test(ctx):
    """Test connection to your AWS GenAI Bot API
    
    This command sends a test request to verify that your API endpoint
    is working correctly and that you can successfully generate text.
    """
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    api_endpoint = config.get('api_endpoint')
    click.echo(f"🔍 Testing connection to: {api_endpoint}")
    click.echo("📡 Sending test request...")

    # Test with a simple prompt
    result = client.generate_text("Hello, this is a test message", max_tokens=50)
    
    if result.get('success'):
        click.echo("✅ Connection successful!")
        
        # Show some details about the response
        metadata = result['data'].get('metadata', {})
        if metadata.get('mock_mode'):
            click.echo("ℹ️ API is running in mock mode")
            click.echo("💡 Enable Bedrock Claude 4 Sonnet access for real AI responses")
        else:
            click.echo("🤖 Real AI responses are enabled")
        
        response_time = metadata.get('response_time_ms', 0)
        click.echo(f"⚡ Response time: {response_time}ms")
        
    else:
        click.echo("❌ Connection failed", err=True)
        error = result.get('error', 'Unknown error')
        click.echo(f"Error: {error}")
        
        # Provide helpful troubleshooting
        status_code = result.get('status_code', 0)
        if status_code == 403:
            click.echo("💡 This might be an authentication or permission issue")
        elif status_code == 404:
            click.echo("💡 Check if your API endpoint URL is correct")
        elif status_code >= 500:
            click.echo("💡 This appears to be a server-side issue")
        
        click.echo("\n🔧 Troubleshooting:")
        click.echo("1. Verify your API endpoint with 'genai config show'")
        click.echo("2. Check if your AWS GenAI Bot service is deployed")
        click.echo("3. Ensure the API Gateway is properly configured")

@config_cmd.command()
@click.confirmation_option(prompt='Reset all configuration to defaults?')
@click.pass_context
def reset(ctx):
    """Reset configuration to defaults
    
    This will reset all configuration values to their defaults,
    including your API endpoint and user ID settings.
    """
    config = ctx.obj['config']
    
    # Reset to default values for your API
    defaults = {
        'api_endpoint': 'https://2i9yquihz5.execute-api.us-east-2.amazonaws.com/Prod',
        'default_user_id': 'cli_user',
        'default_max_tokens': 1000,
        'default_temperature': 0.7,
        'output_format': 'text',
        'log_level': 'INFO',
        'timeout': 30
    }
    
    for key, value in defaults.items():
        config.set(key, value)
    
    config.save_config()
    click.echo("Configuration reset to defaults")
    click.echo("Use 'genai config test' to verify the connection")

@config_cmd.command()
@click.pass_context
def init(ctx):
    """Initialize configuration for your AWS GenAI Bot
    
    This interactive command will help you set up the CLI
    to work with your deployed AWS GenAI Bot API.
    """
    config = ctx.obj['config']
    
    click.echo("🚀 Welcome to AWS GenAI Bot CLI Setup!")
    click.echo("This will help you configure the CLI to work with your API.")
    click.echo()
    
    # API Endpoint
    current_endpoint = config.get('api_endpoint')
    click.echo(f"Current API endpoint: {current_endpoint}")
    
    if click.confirm("Do you want to change the API endpoint?"):
        new_endpoint = click.prompt(
            "Enter your API Gateway endpoint",
            default=current_endpoint,
            type=str
        )
        config.set('api_endpoint', new_endpoint)
    
    # User ID
    current_user = config.get('default_user_id')
    new_user = click.prompt(
        "Enter your default user ID",
        default=current_user,
        type=str
    )
    config.set('default_user_id', new_user)
    
    # Optional: Max tokens
    if click.confirm("Do you want to set custom default parameters?", default=False):
        max_tokens = click.prompt(
            "Default max tokens",
            default=config.get('default_max_tokens'),
            type=int
        )
        config.set('default_max_tokens', max_tokens)
        
        temperature = click.prompt(
            "Default temperature (0.0-1.0)",
            default=config.get('default_temperature'),
            type=float
        )
        config.set('default_temperature', temperature)
    
    # Save configuration
    config.save_config()
    click.echo("\nConfiguration saved!")
    
    # Test connection
    if click.confirm("Test the connection now?", default=True):
        click.echo()
        ctx.invoke(test)