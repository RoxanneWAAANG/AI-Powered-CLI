import click
from cli.client import GenAIClient

@click.group()
def generate():
    """Text generation commands for your AWS GenAI Bot"""
    pass

@generate.command()
@click.argument('prompt')
@click.option('--max-tokens', '-t', type=int, help='Maximum tokens to generate')
@click.option('--temperature', '-temp', type=float, help='Temperature 0.0-1.0')
@click.option('--user-id', '-u', help='User ID for tracking')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['text', 'json']), 
              default='text', help='Output format')
@click.option('--save', '-s', help='Save generated text to file')
@click.pass_context
def text(ctx, prompt, max_tokens, temperature, user_id, output_format, save):
    """Generate text using your AWS GenAI Bot API
    
    Examples:
      genai generate text "Write a poem about AI"
      genai generate text "Explain quantum computing" --max-tokens 500 --temperature 0.3
      genai generate text "Write a story" --save story.txt
    """
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    # Build parameters
    params = {}
    if max_tokens:
        params['max_tokens'] = max_tokens
    if temperature:
        params['temperature'] = temperature
    if user_id:
        params['user_id'] = user_id
    
    try:
        result = client.generate_text(prompt, **params)
        
        # Handle content policy violations gracefully
        if not result.get('success') and result.get('status_code') == 400:
            details = result.get('details', {})
            if details.get('reason') == 'Content policy violation':
                click.echo("❌ Content Policy Violation", err=True)
                click.echo(f"Severity: {details.get('severity', 'Unknown')}")
                click.echo(f"Message: {result.get('message', 'No additional details')}")
                return
        
        if result.get('success'):
            generated_text = result['data']['generated_text']
            metadata = result['data'].get('metadata', {})
            
            if output_format == 'json':
                import json
                output = json.dumps(result['data'], indent=2)
                click.echo(output)
            else:
                click.echo(generated_text)
                
                # Show metadata for text format
                if metadata:
                    click.echo("\n--- Response Details ---")
                    for key, value in metadata.items():
                        formatted_key = key.replace('_', ' ').title()
                        click.echo(f"{formatted_key}: {value}")
            
            # Save to file if requested
            if save:
                try:
                    with open(save, 'w', encoding='utf-8') as f:
                        if output_format == 'json':
                            import json
                            json.dump(result['data'], f, indent=2)
                        else:
                            f.write(generated_text)
                    click.echo(f"\n✅ Generated text saved to {save}")
                except Exception as e:
                    click.echo(f"❌ Error saving file: {e}", err=True)
        else:
            # Handle other errors
            error_msg = result.get('error', 'Unknown error')
            click.echo(f"❌ Error: {error_msg}", err=True)
            
            message = result.get('message')
            if message:
                click.echo(f"💡 {message}")
                
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)

@generate.command()
@click.option('--user-id', '-u', help='User ID for tracking')
@click.pass_context
def interactive(ctx, user_id):
    """Start interactive text generation session
    
    Example:
      genai generate interactive
      genai generate interactive --user-id my_user
    """
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    click.echo("🤖 AWS GenAI Bot - Interactive Mode")
    click.echo("Type 'quit' or 'exit' to leave")
    click.echo("Type 'help' for commands")
    click.echo("Type 'stats' to see your usage statistics")
    click.echo()
    
    session_user_id = user_id or config.get('default_user_id', 'cli_user')
    
    while True:
        try:
            prompt = click.prompt("You", type=str)
            
            if prompt.lower() in ['quit', 'exit']:
                click.echo("👋 Goodbye!")
                break
            elif prompt.lower() == 'help':
                click.echo("Commands:")
                click.echo("  help   - Show this help")
                click.echo("  stats  - Show usage statistics")
                click.echo("  quit   - Exit interactive mode")
                continue
            elif prompt.lower() == 'stats':
                stats_result = client.get_usage_stats(session_user_id)
                if stats_result.get('success'):
                    stats = stats_result['data']
                    click.echo(f"📊 Total Requests (7 days): {stats.get('total_requests', 0)}")
                    click.echo(f"🔢 Total tokens: {stats.get('total_input_tokens', 0) + stats.get('total_output_tokens', 0)}")
                else:
                    click.echo("❌ Could not fetch stats")
                continue
            
            # Generate response
            result = client.generate_text(prompt, user_id=session_user_id)
            
            if result.get('success'):
                generated_text = result['data']['generated_text']
                metadata = result['data'].get('metadata', {})
                
                click.echo(f"\n🤖 Bot: {generated_text}")
                
                # Show brief metadata
                if metadata.get('mock_mode'):
                    click.echo("ℹ️  (Mock mode - enable Bedrock for real AI responses)")
                else:
                    tokens = metadata.get('output_tokens', 0)
                    time_ms = metadata.get('response_time_ms', 0)
                    click.echo(f"ℹ️  ({tokens} tokens, {time_ms}ms)")
                click.echo()
            else:
                click.echo(f"❌ Error: {result.get('error')}", err=True)
                message = result.get('message')
                if message:
                    click.echo(f"💡 {message}")
                click.echo()
                
        except KeyboardInterrupt:
            click.echo("\n👋 Goodbye!")
            break
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)

@generate.command()
@click.option('--file', '-f', required=True, help='File containing prompts (one per line)')
@click.option('--output-dir', '-o', default='./output', help='Output directory')
@click.option('--max-tokens', '-t', type=int, help='Maximum tokens per generation')
@click.option('--temperature', '-temp', type=float, help='Temperature for all generations')
@click.option('--user-id', '-u', help='User ID for tracking')
@click.pass_context
def file(ctx, file, output_dir, max_tokens, temperature, user_id):
    """Generate text from prompts in a file
    
    File format: One prompt per line
    
    Examples:
      genai generate file --file prompts.txt
      genai generate file --file batch.txt --max-tokens 500 --output-dir results
    """
    import os
    from pathlib import Path
    
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Load prompts from file
    with open(file, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    click.echo(f"📄 Processing {len(prompts)} prompts from {file}")
    
    params = {}
    if max_tokens:
        params['max_tokens'] = max_tokens
    if temperature:
        params['temperature'] = temperature
    if user_id:
        params['user_id'] = user_id
    
    successful = 0
    failed = 0
    
    for i, prompt in enumerate(prompts, 1):
        click.echo(f"🔄 Processing prompt {i}/{len(prompts)}")
        
        result = client.generate_text(prompt, **params)
        
        if result.get('success'):
            # Save output
            filename = f"output_{i:03d}.txt"
            output_file = output_path / filename
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['data']['generated_text'])
                
                click.echo(f"  ✅ Saved to {output_file}")
                successful += 1
            except Exception as e:
                click.echo(f"  ❌ Error saving: {e}")
                failed += 1
        else:
            click.echo(f"  ❌ Generation failed: {result.get('error')}")
            failed += 1
    
    click.echo(f"\n📊 File processing completed!")
    click.echo(f"✅ Successful: {successful}")
    click.echo(f"❌ Failed: {failed}")
    click.echo(f"📁 Results saved to: {output_dir}")
