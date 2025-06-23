import click
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from cli.client import GenAIClient

@click.group()
def batch():
    """Batch processing commands for multiple text generations"""
    pass

@batch.command()
@click.option('--input', '-i', required=True, help='Input file with prompts')
@click.option('--output', '-o', default='./batch_output', help='Output directory')
@click.option('--max-tokens', '-t', type=int, help='Maximum tokens per generation')
@click.option('--temperature', '-temp', type=float, help='Temperature for all generations')
@click.option('--user-id', '-u', help='User ID for tracking')
@click.option('--max-workers', '-w', default=3, type=int, help='Max concurrent requests')
@click.option('--delay', '-d', default=1.0, type=float, help='Delay between requests (seconds)')
@click.pass_context
def process(ctx, input, output, max_tokens, temperature, user_id, max_workers, delay):
    """Process multiple prompts from a file in batch
    
    This command processes multiple text generation requests efficiently using
    your existing AWS GenAI Bot API with controlled concurrency and rate limiting.
    
    Input file formats:
    - Text file: One prompt per line
    - JSON file: {"prompts": ["prompt1", "prompt2"]} or ["prompt1", "prompt2"]
    
    Examples:
      genai batch process --input prompts.txt
      genai batch process --input batch.json --max-workers 5 --delay 0.5
      genai batch process --input data.txt --max-tokens 500 --output results
    """
    config = ctx.obj['config']
    client = GenAIClient(config)
    
    # Load prompts from file
    prompts = load_prompts(input)
    click.echo(f"📂 Loaded {len(prompts)} prompts from {input}")
    
    if len(prompts) == 0:
        click.echo("❌ No prompts found in input file", err=True)
        return
    
    # Create output directory
    output_path = Path(output)
    output_path.mkdir(exist_ok=True)
    click.echo(f"📁 Output directory: {output}")
    
    # Process prompts
    results = process_prompts_concurrent(
        prompts, client, max_tokens, temperature, user_id, 
        max_workers, delay, output_path
    )
    
    # Generate summary
    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful
    content_filtered = sum(1 for r in results if r.get('content_filtered'))
    
    # Save summary
    summary = {
        'input_file': input,
        'total_prompts': len(prompts),
        'successful': successful,
        'failed': failed,
        'content_filtered': content_filtered,
        'output_directory': output,
        'processing_time': sum(r.get('processing_time', 0) for r in results),
        'results': results
    }
    
    summary_file = output_path / 'batch_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    # Display results
    click.echo(f"\n📊 Batch Processing Complete!")
    click.echo(f"✅ Successful: {successful}")
    click.echo(f"❌ Failed: {failed}")
    if content_filtered > 0:
        click.echo(f"🛡️  Content Filtered: {content_filtered}")
    click.echo(f"📄 Summary saved to: {summary_file}")
    
    if successful > 0:
        click.echo(f"📁 Generated files saved to: {output}")

def load_prompts(input_file: str) -> list:
    """Load prompts from input file"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if input_path.suffix.lower() == '.json':
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'prompts' in data:
                return data['prompts']
            else:
                raise ValueError("JSON file must contain a list or have a 'prompts' key")
    else:  # Text file
        with open(input_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

def process_prompts_concurrent(prompts: list, client: GenAIClient, 
                              max_tokens: int, temperature: float, user_id: str,
                              max_workers: int, delay: float, output_path: Path) -> list:
    """Process prompts with controlled concurrency"""
    
    results = []
    
    # Progress tracking
    total = len(prompts)
    completed = 0
    
    click.echo(f"🚀 Starting batch processing with {max_workers} workers...")
    click.echo(f"⏱️  Delay between requests: {delay}s")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_index = {}
        
        for i, prompt in enumerate(prompts):
            future = executor.submit(
                process_single_prompt, 
                prompt, i, client, max_tokens, temperature, user_id, output_path
            )
            future_to_index[future] = i
            
            # Add delay between submissions to respect rate limits
            if delay > 0 and i < len(prompts) - 1:
                time.sleep(delay)
        
        # Collect results as they complete
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            result = future.result()
            results.append(result)
            completed += 1
            
            # Progress indicator
            status = "✅" if result.get('success') else "❌"
            if result.get('content_filtered'):
                status = "🛡️"
            
            click.echo(f"{status} [{completed}/{total}] Prompt {index + 1}")
    
    # Sort results by index to maintain order
    results.sort(key=lambda x: x.get('index', 0))
    return results

def process_single_prompt(prompt: str, index: int, client: GenAIClient,
                         max_tokens: int, temperature: float, user_id: str,
                         output_path: Path) -> dict:
    """Process a single prompt"""
    start_time = time.time()

    # Build parameters
    params = {}
    if max_tokens:
        params['max_tokens'] = max_tokens
    if temperature:
        params['temperature'] = temperature
    if user_id:
        params['user_id'] = user_id
    
    # Generate text
    result = client.generate_text(prompt, **params)
    processing_time = time.time() - start_time
    
    if result.get('success'):
        # Save individual result
        output_file = output_path / f"result_{index + 1:04d}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['data']['generated_text'])
        
        return {
            'success': True,
            'index': index,
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'output_file': str(output_file),
            'processing_time': processing_time,
            'metadata': result['data'].get('metadata', {})
        }
    
    else:
        # Check if it's a content policy violation
        is_content_filtered = (result.get('status_code') == 400 and 
                                result.get('details', {}).get('reason') == 'Content policy violation')
        
        return {
            'success': False,
            'content_filtered': is_content_filtered,
            'index': index,
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'error': result.get('error', 'Unknown error'),
            'processing_time': processing_time
        }
            