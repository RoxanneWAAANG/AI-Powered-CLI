import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from cli.main import cli

class TestCommands:
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_config_show(self):
        """Test config show command"""
        result = self.runner.invoke(cli, ['config', 'show'])
        assert result.exit_code == 0
        assert 'Current Configuration' in result.output
    
    def test_config_set_get(self):
        """Test config set and get commands"""
        with self.runner.isolated_filesystem():
            # Test set config
            result = self.runner.invoke(cli, ['config', 'set', 'test_key', 'test_value'])
            assert result.exit_code == 0
            assert 'Configuration updated' in result.output
            
            # Test get config
            result = self.runner.invoke(cli, ['config', 'get', 'test_key'])
            assert result.exit_code == 0
            assert 'test_value' in result.output
    
    def test_config_get_nonexistent(self):
        """Test getting non-existent config key"""
        result = self.runner.invoke(cli, ['config', 'get', 'nonexistent_key'])
        assert result.exit_code == 0
        assert 'not found' in result.output
    
    @patch('cli.commands.config.GenAIClient')
    def test_config_test_success(self, mock_client):
        """Test config test command success"""
        mock_client.return_value.health_check.return_value = True
        
        result = self.runner.invoke(cli, ['config', 'test'])
        assert result.exit_code == 0
        assert 'successful' in result.output
    
    @patch('cli.commands.config.GenAIClient')
    def test_config_test_failure(self, mock_client):
        """Test config test command failure"""
        mock_client.return_value.health_check.return_value = False
        
        result = self.runner.invoke(cli, ['config', 'test'])
        assert result.exit_code == 0
        assert 'failed' in result.output
    
    def test_config_reset(self):
        """Test config reset command"""
        result = self.runner.invoke(cli, ['config', 'reset'], input='y\n')
        assert result.exit_code == 0
        assert 'reset to defaults' in result.output
    
    @patch('cli.commands.batch.load_messages')
    @patch('cli.commands.batch.process_messages_concurrent')
    def test_batch_process(self, mock_process, mock_load):
        """Test batch process command"""
        with self.runner.isolated_filesystem():
            # Create test input file
            with open('test_messages.txt', 'w') as f:
                f.write('Hello\nHow are you?\n')
            
            # Mock functions
            mock_load.return_value = ['Hello', 'How are you?']
            mock_process.return_value = [
                {'success': True, 'data': {'response': 'Hi'}},
                {'success': True, 'data': {'response': 'Good'}}
            ]
            
            result = self.runner.invoke(cli, [
                'batch', 'process', 
                '--input', 'test_messages.txt'
            ])
            assert result.exit_code == 0
            assert 'completed' in result.output