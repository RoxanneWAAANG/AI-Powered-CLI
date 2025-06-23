import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = 'INFO') -> None:
    """Setup logging configuration for the CLI"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    log_dir = Path.home() / '.genai-bot' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (only show WARNING and above to keep CLI output clean)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (capture all logs)
    file_handler = logging.FileHandler(log_dir / 'genai-bot-cli.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)