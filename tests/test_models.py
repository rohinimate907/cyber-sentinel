"""
Unit tests for PentestX data models.

Tests Pydantic models, validation, and data processing functionality.
"""

import pytest
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from pentestx.models import (
    SubdomainResult, IPResult, ASNResult, CIDRResult, 
    CertificateResult, WHOISResult, DomainMapping,
    EnumerationSummary, EnumerationResults,
    DataSource, EnumerationType, OutputFormat
)


class TestSubdomainResult:
    """Test SubdomainResult model validation and functionality."""
    
    def test_valid_subdomain_result(self):
        """Test creating a valid subdomain result."""
        result = SubdomainResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.DOMAIN,
            subdomain="www.example.com",
            ip_addresses=["192.168.1.1", "192.168.1.2"],
            status_code=200,
            technology_stack=["nginx", "cloudflare"]
        )
        
        assert result.subdomain == "www.example.com"
        assert len(result.ip_addresses) == 2
        assert result.status_code == 200
        assert "nginx" in result.technology_stack
        assert result.source == DataSource.NETLAS
    
    def test_subdomain_validation(self):
        """Test subdomain format validation."""
        with pytest.raises(ValueError, match="Invalid subdomain format"):
            SubdomainResult(
                source=DataSource.NETLAS,
                target="example.com",
                enumeration_type=EnumerationType.DOMAIN,
                subdomain="invalid"  # No dot in subdomain
            )
    
    def test_subdomain_normalization(self):
        """Test subdomain normalization to lowercase."""
        result = SubdomainResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.DOMAIN,
            subdomain="  WWW.EXAMPLE.COM  "
        )
        
        assert result.subdomain == "www.example.com"


class TestIPResult:
    """Test IPResult model validation and functionality."""
    
    def test_valid_ipv4_result(self):
        """Test creating a valid IPv4 result."""
        result = IPResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.IP,
            ip_address="192.168.1.1",
            hostname="host.example.com",
            asn_number=12345,
            asn_name="Example ASN",
            country="US",
            open_ports=[80, 443, 22],
            services={80: "http", 443: "https", 22: "ssh"}
        )
        
        assert isinstance(result.ip_address, IPv4Address)
        assert str(result.ip_address) == "192.168.1.1"
        assert result.hostname == "host.example.com"
        assert result.asn_number == 12345
        assert 80 in result.open_ports
        assert result.services[443] == "https"
    
    def test_valid_ipv6_result(self):
        """Test creating a valid IPv6 result."""
        result = IPResult(
            source=DataSource.NETLAS,
            target="example.com", 
            enumeration_type=EnumerationType.IP,
            ip_address="2001:db8::1"
        )
        
        assert isinstance(result.ip_address, IPv6Address)
        assert str(result.ip_address) == "2001:db8::1"
    
    def test_invalid_ip_address(self):
        """Test validation of invalid IP addresses."""
        with pytest.raises(ValueError):
            IPResult(
                source=DataSource.NETLAS,
                target="example.com",
                enumeration_type=EnumerationType.IP,
                ip_address="invalid_ip"
            )


class TestASNResult:
    """Test ASNResult model validation and functionality."""
    
    def test_valid_asn_result(self):
        """Test creating a valid ASN result."""
        result = ASNResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.ASN,
            asn_number=15169,
            asn_name="GOOGLE",
            country="US",
            cidr_ranges=["8.8.8.0/24", "8.8.4.0/24"],
            ip_count=512
        )
        
        assert result.asn_number == 15169
        assert result.asn_name == "GOOGLE"
        assert len(result.cidr_ranges) == 2
        assert result.ip_count == 512
    
    def test_invalid_asn_number(self):
        """Test validation of invalid ASN numbers."""
        with pytest.raises(ValueError, match="ASN number must be positive"):
            ASNResult(
                source=DataSource.NETLAS,
                target="example.com",
                enumeration_type=EnumerationType.ASN,
                asn_number=0,
                asn_name="Invalid ASN"
            )


class TestCIDRResult:
    """Test CIDRResult model validation and functionality."""
    
    def test_valid_cidr_result(self):
        """Test creating a valid CIDR result."""
        result = CIDRResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.CIDR,
            cidr_range="192.168.0.0/24",
            asn_number=12345,
            organization="Example Org",
            country="US",
            ip_count=256
        )
        
        assert result.cidr_range == "192.168.0.0/24"
        assert result.asn_number == 12345
        assert result.ip_count == 256
    
    def test_invalid_cidr_notation(self):
        """Test validation of invalid CIDR notation."""
        with pytest.raises(ValueError, match="Invalid CIDR notation"):
            CIDRResult(
                source=DataSource.NETLAS,
                target="example.com",
                enumeration_type=EnumerationType.CIDR,
                cidr_range="invalid_cidr"
            )


class TestCertificateResult:
    """Test CertificateResult model validation and functionality."""
    
    def test_valid_certificate_result(self):
        """Test creating a valid certificate result."""
        valid_from = datetime(2023, 1, 1)
        valid_to = datetime(2024, 1, 1)
        
        result = CertificateResult(
            source=DataSource.NETLAS,
            target="Example Org",
            enumeration_type=EnumerationType.CERTIFICATE,
            common_name="example.com",
            subject_alt_names=["www.example.com", "api.example.com"],
            issuer="DigiCert",
            organization="Example Organization",
            valid_from=valid_from,
            valid_to=valid_to,
            fingerprint="abc123def456"
        )
        
        assert result.common_name == "example.com"
        assert len(result.subject_alt_names) == 2
        assert result.issuer == "DigiCert"
        assert result.valid_from == valid_from
        assert result.valid_to == valid_to
    
    def test_empty_common_name_validation(self):
        """Test validation of empty common names."""
        with pytest.raises(ValueError, match="Common name cannot be empty"):
            CertificateResult(
                source=DataSource.NETLAS,
                target="Example Org",
                enumeration_type=EnumerationType.CERTIFICATE,
                common_name=""
            )
    
    def test_common_name_normalization(self):
        """Test common name whitespace normalization."""
        result = CertificateResult(
            source=DataSource.NETLAS,
            target="Example Org",
            enumeration_type=EnumerationType.CERTIFICATE,
            common_name="  example.com  "
        )
        
        assert result.common_name == "example.com"


class TestEnumerationSummary:
    """Test EnumerationSummary model and functionality."""
    
    def test_enumeration_summary_creation(self):
        """Test creating an enumeration summary."""
        start_time = datetime.now()
        
        summary = EnumerationSummary(
            target="example.com",
            start_time=start_time
        )
        
        assert summary.target == "example.com"
        assert summary.start_time == start_time
        assert summary.status == "in_progress"
        assert summary.subdomains_found == 0
    
    def test_add_results_counting(self):
        """Test that add_results properly counts different result types."""
        summary = EnumerationSummary(
            target="example.com",
            start_time=datetime.now()
        )
        
        subdomain_result = SubdomainResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.DOMAIN,
            subdomain="www.example.com"
        )
        
        ip_result = IPResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.IP,
            ip_address="192.168.1.1"
        )
        
        summary.add_results([subdomain_result, ip_result])
        
        assert summary.subdomains_found == 1
        assert summary.ips_found == 1
        assert summary.source_breakdown["netlas"] == 2
    
    def test_completion_tracking(self):
        """Test summary completion tracking."""
        start_time = datetime.now()
        summary = EnumerationSummary(target="example.com", start_time=start_time)
        
        summary.complete()
        
        assert summary.status == "completed"
        assert summary.end_time is not None
        assert summary.duration_seconds is not None
        assert summary.duration_seconds >= 0
    
    def test_failure_tracking(self):
        """Test summary failure tracking."""
        summary = EnumerationSummary(
            target="example.com",
            start_time=datetime.now()
        )
        
        error_msg = "Test error"
        summary.fail(error_msg)
        
        assert summary.status == "failed"
        assert error_msg in summary.errors


class TestEnumerationResults:
    """Test EnumerationResults container model."""
    
    def test_enumeration_results_creation(self):
        """Test creating enumeration results container."""
        summary = EnumerationSummary(
            target="example.com",
            start_time=datetime.now()
        )
        
        results = EnumerationResults(summary=summary)
        
        assert results.summary.target == "example.com"
        assert len(results.subdomains) == 0
        assert len(results.ips) == 0
    
    def test_adding_results(self):
        """Test adding different types of results."""
        summary = EnumerationSummary(
            target="example.com",
            start_time=datetime.now()
        )
        results = EnumerationResults(summary=summary)
        
        # Add subdomain result
        subdomain_result = SubdomainResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.DOMAIN,
            subdomain="www.example.com"
        )
        results.add_subdomain(subdomain_result)
        
        # Add IP result
        ip_result = IPResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.IP,
            ip_address="192.168.1.1"
        )
        results.add_ip(ip_result)
        
        assert len(results.subdomains) == 1
        assert len(results.ips) == 1
        assert results.summary.subdomains_found == 1
        assert results.summary.ips_found == 1
    
    def test_deduplication(self):
        """Test result deduplication functionality."""
        summary = EnumerationSummary(
            target="example.com",
            start_time=datetime.now()
        )
        results = EnumerationResults(summary=summary)
        
        # Add duplicate subdomain results
        for i in range(3):
            subdomain_result = SubdomainResult(
                source=DataSource.NETLAS,
                target="example.com",
                enumeration_type=EnumerationType.DOMAIN,
                subdomain="www.example.com"
            )
            results.add_subdomain(subdomain_result)
        
        assert len(results.subdomains) == 3  # Before deduplication
        
        results.deduplicate()
        
        assert len(results.subdomains) == 1  # After deduplication
        assert results.summary.subdomains_found == 1
    
    def test_get_all_results(self):
        """Test getting all results as a flat list."""
        summary = EnumerationSummary(
            target="example.com",
            start_time=datetime.now()
        )
        results = EnumerationResults(summary=summary)
        
        # Add various results
        subdomain_result = SubdomainResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.DOMAIN,
            subdomain="www.example.com"
        )
        results.add_subdomain(subdomain_result)
        
        ip_result = IPResult(
            source=DataSource.NETLAS,
            target="example.com",
            enumeration_type=EnumerationType.IP,
            ip_address="192.168.1.1"
        )
        results.add_ip(ip_result)
        
        all_results = results.get_all_results()
        
        assert len(all_results) == 2
        assert isinstance(all_results[0], (SubdomainResult, IPResult))
        assert isinstance(all_results[1], (SubdomainResult, IPResult))


class TestDomainMapping:
    """Test DomainMapping model functionality."""
    
    def test_valid_domain_mapping(self):
        """Test creating a valid domain mapping."""
        mapping = DomainMapping(
            domain="www.example.com",
            ip_addresses=["192.168.1.1", "192.168.1.2"],
            record_type="A",
            ttl=300
        )
        
        assert mapping.domain == "www.example.com"
        assert len(mapping.ip_addresses) == 2
        assert mapping.record_type == "A"
        assert mapping.ttl == 300
        assert isinstance(mapping.timestamp, datetime)


class TestEnums:
    """Test enum definitions."""
    
    def test_output_format_enum(self):
        """Test OutputFormat enum values."""
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.CSV.value == "csv"
        assert OutputFormat.TXT.value == "txt"
    
    def test_enumeration_type_enum(self):
        """Test EnumerationType enum values."""
        assert EnumerationType.DOMAIN.value == "domain"
        assert EnumerationType.IP.value == "ip"
        assert EnumerationType.ASN.value == "asn"
        assert EnumerationType.CIDR.value == "cidr"
        assert EnumerationType.CERTIFICATE.value == "certificate"
    
    def test_data_source_enum(self):
        """Test DataSource enum values."""
        assert DataSource.NETLAS.value == "netlas"
        assert DataSource.SUBFINDER.value == "subfinder"
        assert DataSource.AMASS.value == "amass"
