"""
Unit tests for PentestX configuration module.

Tests configuration loading, validation, and environment management.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from pentestx.config import (
    NetlasConfig, OutputConfig, ToolConfig, LoggingConfig,
    Settings, get_settings, validate_environment
)


class TestNetlasConfig:
    """Test NetlasConfig validation and functionality."""
    
    def test_valid_netlas_config(self):
        """Test creating a valid Netlas configuration."""
        config = NetlasConfig(
            api_key="test_key_12345",
            rate_limit=10,
            max_retries=3,
            timeout=30,
            backoff_factor=2.0
        )
        
        assert config.api_key == "test_key_12345"
        assert config.rate_limit == 10
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.backoff_factor == 2.0
    
    def test_invalid_api_key(self):
        """Test validation of invalid API keys."""
        with pytest.raises(ValueError, match="Valid Netlas API key must be provided"):
            NetlasConfig(api_key="")
        
        with pytest.raises(ValueError, match="Valid Netlas API key must be provided"):
            NetlasConfig(api_key="your_api_key_here")
    
    def test_invalid_rate_limit(self):
        """Test validation of invalid rate limits."""
        with pytest.raises(ValueError, match="Rate limit must be between 1 and 100"):
            NetlasConfig(api_key="test_key", rate_limit=0)
        
        with pytest.raises(ValueError, match="Rate limit must be between 1 and 100"):
            NetlasConfig(api_key="test_key", rate_limit=101)


class TestOutputConfig:
    """Test OutputConfig validation and functionality."""
    
    def test_valid_output_config(self, tmp_path):
        """Test creating a valid output configuration."""
        config = OutputConfig(
            output_dir=tmp_path,
            default_format="json",
            create_timestamps=True
        )
        
        assert config.output_dir == tmp_path
        assert config.default_format == "json"
        assert config.create_timestamps is True
    
    def test_invalid_output_format(self):
        """Test validation of invalid output formats."""
        with pytest.raises(ValueError, match="Output format must be one of"):
            OutputConfig(default_format="invalid")
    
    def test_output_directory_creation(self, tmp_path):
        """Test that output directory is created automatically."""
        test_dir = tmp_path / "test_output"
        config = OutputConfig(output_dir=test_dir)
        
        assert test_dir.exists()
        assert test_dir.is_dir()


class TestToolConfig:
    """Test ToolConfig validation and functionality."""
    
    def test_valid_tool_config(self):
        """Test creating a valid tool configuration."""
        config = ToolConfig(
            subfinder_path="subfinder",
            amass_path="amass"
        )
        
        assert config.subfinder_path == "subfinder"
        assert config.amass_path == "amass"
    
    def test_tool_availability_check(self):
        """Test tool availability checking."""
        config = ToolConfig()
        
        # Mock subprocess to simulate tool availability
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            status = config.validate_tool_availability()
            
            assert isinstance(status, dict)
            assert "subfinder" in status
            assert "amass" in status


class TestLoggingConfig:
    """Test LoggingConfig validation and functionality."""
    
    def test_valid_logging_config(self):
        """Test creating a valid logging configuration."""
        config = LoggingConfig(
            log_level="INFO",
            log_file="test.log",
            console_output=True
        )
        
        assert config.log_level == "INFO"
        assert config.log_file == "test.log"
        assert config.console_output is True
    
    def test_invalid_log_level(self):
        """Test validation of invalid log levels."""
        with pytest.raises(ValueError, match="Log level must be one of"):
            LoggingConfig(log_level="INVALID")
    
    def test_log_level_normalization(self):
        """Test that log level is normalized to uppercase."""
        config = LoggingConfig(log_level="debug")
        assert config.log_level == "DEBUG"


class TestSettings:
    """Test Settings class and environment loading."""
    
    @patch.dict(os.environ, {
        'NETLAS_API_KEY': 'test_key_12345',
        'RATE_LIMIT': '15',
        'MAX_RETRIES': '5',
        'TIMEOUT': '60',
        'OUTPUT_DIR': '/tmp/test_output',
        'DEFAULT_FORMAT': 'csv',
        'LOG_LEVEL': 'WARNING'
    })
    def test_settings_from_environment(self):
        """Test loading settings from environment variables."""
        settings = Settings()
        
        assert settings.netlas.api_key == 'test_key_12345'
        assert settings.netlas.rate_limit == 15
        assert settings.netlas.max_retries == 5
        assert settings.netlas.timeout == 60
        assert str(settings.output.output_dir) == '/tmp/test_output'
        assert settings.output.default_format == 'csv'
        assert settings.logging.log_level == 'WARNING'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_settings_defaults(self):
        """Test default settings when no environment variables are set."""
        # This should fail due to missing API key
        with pytest.raises(ValueError):
            Settings()
    
    def test_get_output_path(self, test_settings):
        """Test output path generation."""
        test_settings.output.create_timestamps = False
        
        path = test_settings.get_output_path("test_file", "json")
        
        assert path.name == "test_file.json"
        assert path.parent == test_settings.output.output_dir
    
    def test_get_output_path_with_timestamp(self, test_settings):
        """Test output path generation with timestamps."""
        test_settings.output.create_timestamps = True
        
        path = test_settings.get_output_path("test_file", "json")
        
        assert path.name.startswith("test_file_")
        assert path.name.endswith(".json")
        assert path.parent == test_settings.output.output_dir


class TestValidateEnvironment:
    """Test environment validation functionality."""
    
    @patch('pentestx.config.get_settings')
    def test_valid_environment(self, mock_get_settings, test_settings):
        """Test validation of a valid environment."""
        test_settings.tools.validate_tool_availability = lambda: {"subfinder": True, "amass": True}
        mock_get_settings.return_value = test_settings
        
        is_valid, errors = validate_environment()
        
        assert is_valid is True
        assert len(errors) == 0
    
    @patch('pentestx.config.get_settings')
    def test_invalid_api_key(self, mock_get_settings, test_settings):
        """Test validation with invalid API key."""
        test_settings.netlas.api_key = "your_api_key_here"
        mock_get_settings.return_value = test_settings
        
        is_valid, errors = validate_environment()
        
        assert is_valid is False
        assert any("Netlas API key" in error for error in errors)
    
    @patch('pentestx.config.get_settings')
    def test_missing_tools(self, mock_get_settings, test_settings):
        """Test validation with missing tools."""
        test_settings.tools.validate_tool_availability = lambda: {"subfinder": False, "amass": False}
        mock_get_settings.return_value = test_settings
        
        is_valid, errors = validate_environment()
        
        assert is_valid is False
        assert any("Subfinder" in error for error in errors)
        assert any("Amass" in error for error in errors)
    
    @patch('pentestx.config.get_settings')
    def test_configuration_exception(self, mock_get_settings):
        """Test validation when configuration loading fails."""
        mock_get_settings.side_effect = Exception("Config error")
        
        is_valid, errors = validate_environment()
        
        assert is_valid is False
        assert len(errors) == 1
        assert "Configuration validation failed" in errors[0]


class TestGetSettings:
    """Test the get_settings function."""
    
    @patch.dict(os.environ, {
        'NETLAS_API_KEY': 'test_key_12345',
    })
    def test_get_settings_success(self):
        """Test successful settings retrieval."""
        settings = get_settings()
        
        assert isinstance(settings, Settings)
        assert settings.netlas.api_key == 'test_key_12345'
    
    @patch('pentestx.config.Settings')
    def test_get_settings_caching(self, mock_settings_class):
        """Test that settings are properly instantiated."""
        mock_instance = mock_settings_class.return_value
        
        result = get_settings()
        
        assert result == mock_instance
        mock_settings_class.assert_called_once()
