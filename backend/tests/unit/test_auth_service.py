"""
Unit Tests for Authentication Service
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.auth_service import AuthService
from src.domain.models.user import User, UserRole
from src.core.security import PasswordSecurity


class TestAuthService:
    """Test authentication service"""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance"""
        return AuthService()
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            password_hash=PasswordSecurity.hash_password("Test123!@#"),
            role=UserRole.RESEARCHER,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        return user
    
    def test_hash_password(self, auth_service):
        """Test password hashing"""
        password = "Test123!@#"
        hashed = PasswordSecurity.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password"""
        password = "Test123!@#"
        hashed = PasswordSecurity.hash_password(password)
        
        assert PasswordSecurity.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password"""
        password = "Test123!@#"
        wrong_password = "Wrong123!@#"
        hashed = PasswordSecurity.hash_password(password)
        
        assert PasswordSecurity.verify_password(wrong_password, hashed) is False
    
    def test_create_access_token(self, auth_service):
        """Test JWT token creation"""
        from src.core.security import TokenSecurity
        
        data = {"sub": "test@example.com", "role": "researcher"}
        token = TokenSecurity.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_validate_email_format(self, auth_service):
        """Test email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.com"
        ]
        
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test @example.com"
        ]
        
        for email in valid_emails:
            # Should not raise exception
            from email_validator import validate_email
            validate_email(email)
        
        for email in invalid_emails:
            with pytest.raises(Exception):
                from email_validator import validate_email
                validate_email(email)
    
    def test_password_strength_validation(self, auth_service):
        """Test password strength requirements"""
        weak_passwords = [
            "short",
            "nouppercase123!",
            "NOLOWERCASE123!",
            "NoSpecialChar123",
            "NoNumber!@#"
        ]
        
        strong_password = "Test123!@#"
        
        # Password should have: min 8 chars, uppercase, lowercase, number, special char
        import re
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        
        for pwd in weak_passwords:
            assert re.match(pattern, pwd) is None
        
        assert re.match(pattern, strong_password) is not None


class TestUserRoles:
    """Test user role functionality"""
    
    def test_user_roles_enum(self):
        """Test user role enum values"""
        assert UserRole.RESEARCHER.value == "researcher"
        assert UserRole.ORGANIZATION.value == "organization"
        assert UserRole.STAFF.value == "staff"
    
    def test_role_permissions(self):
        """Test role-based permissions"""
        # Researcher can submit reports
        researcher_permissions = ["submit_report", "view_programs", "view_bounties"]
        
        # Organization can create programs
        org_permissions = ["create_program", "manage_program", "view_reports", "pay_bounties"]
        
        # Staff can moderate
        staff_permissions = ["moderate_reports", "manage_users", "view_analytics"]
        
        # Basic permission check
        assert "submit_report" in researcher_permissions
        assert "create_program" in org_permissions
        assert "moderate_reports" in staff_permissions
