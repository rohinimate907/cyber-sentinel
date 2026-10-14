"""
Test configuration and setup for PentestX.

This module provides common test fixtures and configurations
used across the test suite.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import AsyncGenerator

from pentestx.config import Settings, NetlasConfig, OutputConfig, ToolConfig, LoggingConfig
from pentestx.models import EnumerationResults, EnumerationSummary
from pentestx.netlas_client import NetlasClient
from pentestx.integrations import ToolManager
from pentestx.pipeline import EnumerationPipeline


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock configuration."""
    netlas_config = NetlasConfig(
        api_key="test_api_key_12345",
        rate_limit=5,
        max_retries=2,
        timeout=10,
        backoff_factor=1.5
    )
    
    output_config = OutputConfig(
        output_dir=Path("/tmp/pentestx_test"),
        default_format="json",
        create_timestamps=False
    )
    
    tools_config = ToolConfig(
        subfinder_path="/usr/bin/subfinder",
        amass_path="/usr/bin/amass"
    )
    
    logging_config = LoggingConfig(
        log_level="DEBUG",
        log_file="test.log",
        console_output=False
    )
    
    # Create settings with mock data
    settings = Settings.__new__(Settings)
    settings.netlas = netlas_config
    settings.output = output_config
    settings.tools = tools_config
    settings.logging = logging_config
    
    return settings


@pytest.fixture
def mock_netlas_client(test_settings: Settings) -> Mock:
    """Create a mock Netlas client for testing."""
    mock_client = Mock(spec=NetlasClient)
    mock_client.settings = test_settings
    mock_client.requests_made = 0
    mock_client.errors_encountered = 0
    
    # Mock async methods
    mock_client.test_connection = AsyncMock(return_value=True)
    mock_client.get_domain_info = AsyncMock(return_value={"domain": "test.com"})
    mock_client.get_ip_info = AsyncMock(return_value={"ip": "1.2.3.4"})
    mock_client.search_subdomains = AsyncMock(return_value=[])
    mock_client.search_ips_by_asn = AsyncMock(return_value=[])
    mock_client.search_certificates_by_org = AsyncMock(return_value=[])
    mock_client.get_asn_info = AsyncMock(return_value=None)
    
    return mock_client


@pytest.fixture
def mock_tool_manager(test_settings: Settings) -> Mock:
    """Create a mock tool manager for testing."""
    mock_manager = Mock(spec=ToolManager)
    mock_manager.settings = test_settings
    mock_manager.tools = {}
    mock_manager.tool_status = {"subfinder": True, "amass": True}
    
    # Mock async methods
    mock_manager.check_tool_availability = AsyncMock(return_value={"subfinder": True, "amass": True})
    mock_manager.run_subdomain_enumeration = AsyncMock(return_value={})
    mock_manager.run_passive_enumeration = AsyncMock(return_value={})
    mock_manager.run_active_enumeration = AsyncMock(return_value={})
    mock_manager.aggregate_results = Mock(return_value=[])
    
    return mock_manager


@pytest.fixture
def sample_enumeration_results() -> EnumerationResults:
    """Create sample enumeration results for testing."""
    from datetime import datetime
    from pentestx.models import SubdomainResult, DataSource, EnumerationType
    
    summary = EnumerationSummary(
        target="test.com",
        start_time=datetime.now()
    )
    
    results = EnumerationResults(summary=summary)
    
    # Add sample subdomain result
    subdomain_result = SubdomainResult(
        source=DataSource.NETLAS,
        target="test.com",
        enumeration_type=EnumerationType.DOMAIN,
        subdomain="www.test.com",
        ip_addresses=["1.2.3.4"]
    )
    
    results.add_subdomain(subdomain_result)
    
    return results


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test data
SAMPLE_DOMAIN = "example.com"
SAMPLE_IP = "8.8.8.8"
SAMPLE_ASN = 15169
SAMPLE_ORG = "Google LLC"

SAMPLE_NETLAS_DOMAIN_RESPONSE = {
    "domain": "example.com",
    "ip": "93.184.216.34",
    "asn": {
        "number": 15133,
        "name": "EDGECAST"
    },
    "geo": {
        "country": "US"
    }
}

SAMPLE_NETLAS_SUBDOMAIN_RESPONSE = {
    "items": [
        {
            "data": {
                "domain": "www.example.com",
                "ip": ["93.184.216.34"],
                "http": {
                    "status_code": 200
                },
                "technologies": ["nginx"]
            }
        }
    ]
}

SAMPLE_NETLAS_CERTIFICATE_RESPONSE = {
    "items": [
        {
            "data": {
                "subject": {
                    "common_name": "example.com",
                    "organization": "Example Organization"
                },
                "extensions": {
                    "subject_alt_name": ["www.example.com", "api.example.com"]
                },
                "issuer": {
                    "common_name": "DigiCert"
                },
                "validity": {
                    "not_before": "2023-01-01T00:00:00Z",
                    "not_after": "2024-01-01T00:00:00Z"
                },
                "fingerprint": "abc123"
            }
        }
    ]
}


class AsyncContextManager:
    """Helper class for testing async context managers."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
