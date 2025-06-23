# Project 5 - GenAI Command Line Interface

A comprehensive command-line interface for the AWS GenAI Bot text generation service. This CLI tool provides seamless integration with your deployed AWS serverless GenAI API, offering text generation, batch processing, usage analytics, and configuration management capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands Reference](#commands-reference)
- [Batch Processing](#batch-processing)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API Integration](#api-integration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

This CLI tool extends the existing AWS GenAI Bot serverless application by providing a powerful command-line interface for developers and content creators. Built with Python and Click, it offers both simple one-off text generation and sophisticated batch processing capabilities.

### Architecture Integration

The CLI integrates with your existing AWS infrastructure:

```
CLI Tool  →  API Gateway  →  Lambda Functions  →  AWS Bedrock
    ↓            ↓              ↓                  ↓
Commands    REST API     Text Generation     Claude 4 Sonnet
Batch       Rate Limiting   Content Filter    AI Responses
Config      CORS Support    Usage Tracking    Real/Mock Mode
```

## Features

### Core Functionality
- **Interactive Text Generation**: Real-time AI-powered text generation
- **Batch Processing**: Process multiple prompts with concurrency control
- **Usage Analytics**: Comprehensive usage statistics and reporting
- **Configuration Management**: Flexible configuration with validation
- **Multiple Output Formats**: Text, JSON, and rich terminal formatting

### Advanced Capabilities
- **Content Policy Integration**: Handles content filtering responses gracefully
- **Concurrent Processing**: Configurable worker pools for batch operations
- **Progress Monitoring**: Real-time progress tracking for long-running operations
- **Error Recovery**: Robust error handling with detailed diagnostics
- **Rate Limiting**: Built-in delays and throttling for API protection

### Developer Experience
- **Comprehensive Testing**: Full test suite with coverage reporting
- **Rich Terminal Output**: Colored output with tables and panels
- **Flexible Input**: Support for text files, JSON, and direct input
- **Extensible Architecture**: Modular design for easy enhancement

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS credentials configured (for your deployed GenAI Bot API)
- Access to your deployed AWS GenAI Bot service

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/RoxanneWAAANG/AI-Powered-CLI.git
cd AI-Powered-CLI
```

2. Install dependencies:
```bash
pip install -r requirements-cli.txt
```

3. Install the CLI tool:
```bash
pip install -e .
```

4. Verify installation:
```bash
genai --help
```

## Quick Start

### 1. Test Connection

The CLI comes pre-configured with your API endpoint. Test the connection:

```bash
genai config test
```

### 2. Generate Text

```bash
# Simple text generation
genai generate text "Write a haiku about programming"

# Quick generation (shorthand)
genai quick "Explain machine learning in simple terms"
```

### 3. Interactive Mode

```bash
genai generate interactive
```

### 4. Check Usage

```bash
genai usage stats
genai status
```

## Configuration

### Default Configuration

The CLI is pre-configured to work with your deployed AWS GenAI Bot API:

```yaml
api_endpoint: https://2i9yquihz5.execute-api.us-east-2.amazonaws.com/Prod
default_user_id: cli_user
default_max_tokens: 1000
default_temperature: 0.7
output_format: text
log_level: INFO
timeout: 30
```

### Configuration Commands

```bash
# View current configuration
genai config show

# Set configuration values
genai config set default_user_id my_team
genai config set default_max_tokens 1500
genai config set default_temperature 0.8

# Get specific values
genai config get api_endpoint

# Interactive setup
genai config init

# Reset to defaults
genai config reset
```

### Environment Variables

Override configuration using environment variables:

```bash
export GENAI_API_ENDPOINT="https://your-custom-endpoint.com/Prod"
export GENAI_USER_ID="production_user"
export GENAI_MAX_TOKENS="2000"
export GENAI_TEMPERATURE="0.5"
```

## Usage

### Text Generation

#### Basic Generation

```bash
# Generate text with default parameters
genai generate text "Write a story about artificial intelligence"

# Customize parameters
genai generate text "Explain quantum computing" \
  --max-tokens 500 \
  --temperature 0.3 \
  --user-id research_team

# Save output to file
genai generate text "Create a product description" --save description.txt

# Output in JSON format
genai generate text "List programming benefits" --format json
```

#### Interactive Mode

```bash
genai generate interactive

# In interactive mode:
# - Type prompts and get real-time responses
# - Use 'help' for available commands
# - Use 'stats' to see usage statistics
# - Use 'quit' to exit
```

#### File Processing

```bash
# Process prompts from a text file (one per line)
genai generate file --file prompts.txt --output-dir results

# Process with custom parameters
genai generate file --file prompts.txt \
  --max-tokens 800 \
  --temperature 0.6 \
  --output-dir custom_results
```

### Usage Analytics

#### Basic Statistics

```bash
# View usage stats for last 7 days
genai usage stats

# Custom time period and user
genai usage stats --user-id team_bot --days 30

# JSON output for integration
genai usage stats --format json
```

#### Quick Summary

```bash
genai usage summary
```

#### Detailed Reports

```bash
# Generate comprehensive report
genai usage report --days 90 --output quarterly_report.md

# Custom user report
genai usage report --user-id production_team --days 30 --output team_report.txt
```

## Commands Reference

### Text Generation Commands

| Command | Description | Options |
|---------|-------------|---------|
| `genai generate text <prompt>` | Generate text from prompt | `--max-tokens`, `--temperature`, `--user-id`, `--format`, `--save` |
| `genai generate interactive` | Start interactive session | `--user-id` |
| `genai generate file` | Process file of prompts | `--file`, `--output-dir`, `--max-tokens`, `--temperature`, `--user-id` |
| `genai quick <prompt>` | Quick text generation | None |

### Batch Processing Commands

| Command | Description | Options |
|---------|-------------|---------|
| `genai batch process` | Advanced batch processing | `--input`, `--output`, `--max-workers`, `--delay`, `--max-tokens`, `--temperature`, `--user-id` |

### Usage Commands

| Command | Description | Options |
|---------|-------------|---------|
| `genai usage stats` | Show usage statistics | `--user-id`, `--days`, `--format` |
| `genai usage summary` | Quick usage summary | `--user-id` |
| `genai usage report` | Generate detailed report | `--user-id`, `--days`, `--output` |

### Configuration Commands

| Command | Description | Options |
|---------|-------------|---------|
| `genai config show` | Display configuration | None |
| `genai config set <key> <value>` | Set configuration value | None |
| `genai config get <key>` | Get configuration value | None |
| `genai config test` | Test API connection | None |
| `genai config init` | Interactive configuration | None |
| `genai config reset` | Reset to defaults | None |

### Utility Commands

| Command | Description | Options |
|---------|-------------|---------|
| `genai status` | Show CLI and API status | None |
| `genai --help` | Show help information | None |
| `genai --version` | Show version | None |

## Batch Processing

### Input File Formats

#### Text File Format
```
What is artificial intelligence?
Write a haiku about programming
Explain the benefits of cloud computing
Create a product description for a smartwatch
```

#### JSON File Format
```json
{
  "prompts": [
    "What is artificial intelligence?",
    "Write a haiku about programming",
    "Explain the benefits of cloud computing",
    "Create a product description for a smartwatch"
  ]
}
```

Or simple array format:
```json
[
  "What is artificial intelligence?",
  "Write a haiku about programming"
]
```

### Batch Processing Examples

#### Basic Batch Processing

```bash
# Process text file
genai batch process --input prompts.txt --output results

# Process JSON file with custom settings
genai batch process \
  --input batch_prompts.json \
  --output team_results \
  --max-tokens 800 \
  --temperature 0.7 \
  --user-id content_team
```

#### Advanced Batch Processing

```bash
# High-concurrency processing with rate limiting
genai batch process \
  --input large_batch.txt \
  --output production_results \
  --max-workers 10 \
  --delay 0.5 \
  --max-tokens 1200

# Conservative processing for rate-limited APIs
genai batch process \
  --input sensitive_prompts.txt \
  --max-workers 1 \
  --delay 2.0 \
  --output careful_results
```

### Batch Output

Batch processing creates:
- Individual result files: `result_001.txt`, `result_002.txt`, etc.
- Summary file: `batch_summary.json` with processing statistics
- Progress tracking during execution
- Error handling and reporting

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cli --cov-report=html --cov-report=term-missing

# Run specific test files
pytest cli/tests/test_cli.py
pytest cli/tests/test_client.py -v
```

### Test Coverage

The test suite covers:
- CLI command functionality
- API client operations
- Configuration management
- Error handling scenarios
- Batch processing logic

View detailed coverage:
```bash
# Generate HTML coverage report
pytest --cov=cli --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Manual Testing

```bash
# Test basic functionality
genai config test
genai quick "Test message"
genai usage summary

# Test batch processing
echo -e "Hello\nHow are you?\nWrite a poem" > test.txt
genai batch process --input test.txt --output test_results

# Test error handling
genai generate text ""  # Should show validation error
genai config set invalid_key value  # Should show warning
```

## Project Structure

```
AWS-GenAI-Bot/
├── chatbot/                    # Original Lambda functions
│   ├── app.py                  # Lambda handlers
│   └── requirements.txt        # Lambda dependencies
├── template.yaml               # SAM template
├── cli/                        # CLI application
│   ├── __init__.py
│   ├── main.py                 # Main CLI entry point
│   ├── config.py               # Configuration management
│   ├── client.py               # API client
│   ├── commands/               # Command modules
│   │   ├── __init__.py
│   │   ├── generate.py         # Text generation commands
│   │   ├── batch.py            # Batch processing
│   │   ├── usage.py            # Usage statistics
│   │   └── config.py           # Configuration commands
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── logger.py           # Logging configuration
│   │   └── formatter.py        # Output formatting
│   └── tests/                  # Test suite
│       ├── __init__.py
│       ├── test_cli.py         # CLI tests
│       ├── test_client.py      # API client tests
│       └── test_commands.py    # Command tests
├── docs/                       # Documentation
├── requirements-cli.txt        # CLI dependencies
├── setup.py                    # CLI installation
├── pytest.ini                 # Test configuration
└── README.md                   # This file
```

## API Integration

### Endpoint Compatibility

The CLI integrates with your existing AWS GenAI Bot API endpoints:

#### Text Generation Endpoint
```
POST /generate
Content-Type: application/json

{
  "prompt": "Your text prompt",
  "max_tokens": 1000,
  "temperature": 0.7,
  "user_id": "cli_user"
}
```

#### Usage Statistics Endpoint
```
GET /usage/{user_id}?days=7
```

### Response Handling

The CLI handles all response types from your API:

#### Successful Generation
```json
{
  "generated_text": "AI-generated response...",
  "metadata": {
    "input_tokens": 10,
    "output_tokens": 50,
    "response_time_ms": 200,
    "model_id": "anthropic.claude-sonnet-4",
    "user_id": "cli_user",
    "content_filter_status": "passed",
    "mock_mode": false
  }
}
```

#### Content Policy Violations
```json
{
  "error": "Content policy violation detected",
  "details": {
    "reason": "Content policy violation",
    "severity": "HIGH",
    "user_id": "cli_user",
    "timestamp": 1640995200
  },
  "message": "Your request contains content that violates our usage policies."
}
```

### Mock Mode Support

The CLI automatically detects and handles mock mode responses:
- Displays mock mode indicators
- Provides guidance for enabling real AI responses
- Maintains full functionality during development

## Troubleshooting

### Common Issues

#### Connection Problems

**Issue**: `Connection failed` or `API not accessible`

**Solutions**:
1. Verify your API is deployed:
   ```bash
   aws cloudformation describe-stacks --stack-name genai-bot
   ```
2. Check API endpoint configuration:
   ```bash
   genai config show
   genai config test
   ```
3. Update endpoint if changed:
   ```bash
   genai config set api_endpoint https://new-endpoint.com/Prod
   ```

#### Permission Errors

**Issue**: `403 Forbidden` or authentication errors

**Solutions**:
1. Verify AWS credentials are configured
2. Check API Gateway permissions
3. Ensure Lambda function has proper IAM roles

#### Rate Limiting

**Issue**: Too many requests or throttling

**Solutions**:
1. Reduce batch concurrency:
   ```bash
   genai batch process --input file.txt --max-workers 1 --delay 2.0
   ```
2. Check your API Gateway throttling settings
3. Monitor CloudWatch for throttling metrics

#### Content Filtering

**Issue**: Content policy violations

**Solutions**:
1. Review and modify prompts
2. Check content filtering severity levels
3. Use the interactive mode to test prompts

### Debug Information

Enable debug logging:
```bash
genai config set log_level DEBUG
```

Check log files:
```bash
tail -f ~/.genai-bot/logs/genai-bot-cli.log
```

### Getting Help

1. Check command help:
   ```bash
   genai --help
   genai generate --help
   genai batch process --help
   ```

2. Test configuration:
   ```bash
   genai config show
   genai config test
   genai status
   ```

3. Review logs for detailed error information
4. Check your AWS GenAI Bot service status in AWS Console

## Contributing

### Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-cli.txt
   pip install -e .
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cli --cov-report=html

# Run specific tests
pytest cli/tests/test_client.py::TestGenAIClient::test_generate_text_success -v
```
