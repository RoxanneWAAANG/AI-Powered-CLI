import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class CLIConfig:
    """Manage CLI configuration for your existing AWS GenAI Bot API"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.genai-bot'
        self.config_file = self.config_dir / 'config.yaml'
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with your API endpoint as default"""
        # Default configuration for your existing API
        config = {
            'api_endpoint': 'https://2i9yquihz5.execute-api.us-east-2.amazonaws.com/Prod',
            'default_user_id': 'cli_user',
            'default_max_tokens': 1000,
            'default_temperature': 0.7,
            'output_format': 'text',
            'log_level': 'INFO',
            'timeout': 30
        }
        
        # Load from config file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables
        env_mapping = {
            'GENAI_API_ENDPOINT': 'api_endpoint',
            'GENAI_USER_ID': 'default_user_id',
            'GENAI_MAX_TOKENS': 'default_max_tokens',
            'GENAI_TEMPERATURE': 'default_temperature'
        }
        
        for env_var, config_key in env_mapping.items():
            if os.getenv(env_var):
                value = os.getenv(env_var)
                # Type conversion for numeric values
                if config_key in ['default_max_tokens', 'timeout']:
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                elif config_key in ['default_temperature']:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                config[config_key] = value
        
        return config
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def display(self) -> Dict[str, Any]:
        """Get all configuration for display"""
        return self._config.copy()