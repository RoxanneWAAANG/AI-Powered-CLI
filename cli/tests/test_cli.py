import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from cli.main import cli

class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'GenAI CLI' in result.output
    
    def test_cli_version(self):
        """Test CLI version command"""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    def test_chat_help(self):
        """Test chat help command"""
        result = self.runner.invoke(cli, ['chat', '--help'])
        assert result.exit_code == 0
        assert 'Chat with GenAI bot' in result.output
    
    def test_batch_help(self):
        """Test batch help command"""
        result = self.runner.invoke(cli, ['batch', '--help'])
        assert result.exit_code == 0
        assert 'Batch processing commands' in result.output
    
    def test_config_help(self):
        """Test config help command"""
        result = self.runner.invoke(cli, ['config', '--help'])
        assert result.exit_code == 0
        assert 'Configuration management commands' in result.output
    
    @patch('cli.commands.chat.GenAIClient')
    def test_chat_send_command(self, mock_client):
        """Test chat send command"""
        # Mock successful response
        mock_client.return_value.generate_text.return_value = {
            'success': True,
            'data': {'response': 'Test response'}
        }
        
        result = self.runner.invoke(cli, ['chat', 'send', 'test message'])
        assert result.exit_code == 0
        assert 'Test response' in result.output
    
    @patch('cli.commands.chat.GenAIClient')
    def test_chat_send_error(self, mock_client):
        """Test chat send command with error"""
        # Mock error response
        mock_client.return_value.generate_text.return_value = {
            'success': False,
            'error': 'Test error'
        }
        
        result = self.runner.invoke(cli, ['chat', 'send', 'test message'])
        assert result.exit_code == 0
        assert 'Test error' in result.output