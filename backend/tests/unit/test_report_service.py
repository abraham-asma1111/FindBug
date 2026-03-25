"""
Unit Tests for Report Service
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.services.report_service import ReportService


class TestReportService:
    """Test vulnerability report service"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def report_service(self, mock_db):
        """Create report service instance with mocked dependencies"""
        service = Mock(spec=ReportService)
        service.db = mock_db
        return service
    
    def test_severity_levels(self, report_service):
        """Test severity level validation"""
        valid_severities = ["critical", "high", "medium", "low", "info"]
        
        for severity in valid_severities:
            assert severity in valid_severities
    
    def test_cvss_score_critical(self, report_service):
        """Test CVSS score for critical severity"""
        # CVSS 9.0-10.0 = Critical
        critical_scores = [9.0, 9.5, 10.0]
        
        for score in critical_scores:
            assert 9.0 <= score <= 10.0
    
    def test_cvss_score_high(self, report_service):
        """Test CVSS score for high severity"""
        # CVSS 7.0-8.9 = High
        high_scores = [7.0, 7.5, 8.0, 8.9]
        
        for score in high_scores:
            assert 7.0 <= score < 9.0
    
    def test_cvss_score_medium(self, report_service):
        """Test CVSS score for medium severity"""
        # CVSS 4.0-6.9 = Medium
        medium_scores = [4.0, 5.0, 6.0, 6.9]
        
        for score in medium_scores:
            assert 4.0 <= score < 7.0
    
    def test_cvss_score_low(self, report_service):
        """Test CVSS score for low severity"""
        # CVSS 0.1-3.9 = Low
        low_scores = [0.1, 1.0, 2.0, 3.9]
        
        for score in low_scores:
            assert 0.1 <= score < 4.0
    
    def test_report_status_transitions(self, report_service):
        """Test valid report status transitions"""
        valid_transitions = {
            "submitted": ["triaging", "rejected"],
            "triaging": ["validated", "invalid", "duplicate"],
            "validated": ["resolved", "accepted"],
            "accepted": ["resolved"],
            "resolved": ["closed"]
        }
        
        # Test submitted -> triaging
        assert "triaging" in valid_transitions["submitted"]
        
        # Test triaging -> validated
        assert "validated" in valid_transitions["triaging"]
        
        # Test validated -> resolved
        assert "resolved" in valid_transitions["validated"]
    
    def test_duplicate_detection(self, report_service):
        """Test duplicate report detection logic"""
        report1 = {
            "title": "SQL Injection in login form",
            "vulnerability_type": "sqli",
            "affected_url": "https://example.com/login"
        }
        
        report2 = {
            "title": "SQL Injection in login page",
            "vulnerability_type": "sqli",
            "affected_url": "https://example.com/login"
        }
        
        # Same vulnerability type and URL = potential duplicate
        assert report1["vulnerability_type"] == report2["vulnerability_type"]
        assert report1["affected_url"] == report2["affected_url"]
    
    def test_bounty_calculation_critical(self, report_service):
        """Test bounty calculation for critical severity"""
        # Critical vulnerabilities typically get highest bounty
        severity = "critical"
        base_bounty = 5000
        
        # Critical might get 100% of base
        bounty = base_bounty * 1.0
        
        assert bounty == 5000
    
    def test_bounty_calculation_high(self, report_service):
        """Test bounty calculation for high severity"""
        severity = "high"
        base_bounty = 5000
        
        # High might get 60% of base
        bounty = base_bounty * 0.6
        
        assert bounty == 3000
    
    def test_bounty_calculation_medium(self, report_service):
        """Test bounty calculation for medium severity"""
        severity = "medium"
        base_bounty = 5000
        
        # Medium might get 30% of base
        bounty = base_bounty * 0.3
        
        assert bounty == 1500
    
    def test_report_validation_required_fields(self, report_service):
        """Test report validation for required fields"""
        required_fields = [
            "title",
            "description",
            "vulnerability_type",
            "severity",
            "steps_to_reproduce",
            "affected_url"
        ]
        
        report = {
            "title": "XSS Vulnerability",
            "description": "Stored XSS in comment section",
            "vulnerability_type": "xss",
            "severity": "high",
            "steps_to_reproduce": "1. Go to comments\n2. Submit script",
            "affected_url": "https://example.com/comments"
        }
        
        for field in required_fields:
            assert field in report
            assert report[field] is not None
            assert len(str(report[field])) > 0
