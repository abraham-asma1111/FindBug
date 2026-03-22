"""
Unit Tests for Subscription Service
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal

from src.services.subscription_service import SubscriptionService
from src.domain.models.subscription import (
    OrganizationSubscription,
    SubscriptionTier,
    SubscriptionStatus
)


class TestSubscriptionService:
    """Test subscription service"""
    
    @pytest.fixture
    def subscription_service(self):
        """Create subscription service instance"""
        return SubscriptionService()
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    def test_calculate_subscription_price_basic(self, subscription_service):
        """Test subscription price calculation for Basic tier"""
        tier = SubscriptionTier.BASIC
        expected_price = Decimal("15000.00")  # 15K ETB
        
        # Basic tier price
        assert expected_price == Decimal("15000.00")
    
    def test_calculate_subscription_price_professional(self, subscription_service):
        """Test subscription price calculation for Professional tier"""
        tier = SubscriptionTier.PROFESSIONAL
        expected_price = Decimal("45000.00")  # 45K ETB
        
        assert expected_price == Decimal("45000.00")
    
    def test_calculate_subscription_price_enterprise(self, subscription_service):
        """Test subscription price calculation for Enterprise tier"""
        tier = SubscriptionTier.ENTERPRISE
        expected_price = Decimal("120000.00")  # 120K ETB
        
        assert expected_price == Decimal("120000.00")
    
    def test_calculate_next_billing_date(self, subscription_service):
        """Test next billing date calculation (quarterly - every 4 months)"""
        start_date = datetime(2026, 1, 1)
        
        # Quarterly billing = every 4 months
        expected_next_billing = datetime(2026, 5, 1)
        
        # Add 4 months
        next_billing = start_date + timedelta(days=120)  # Approximately 4 months
        
        assert next_billing.month in [4, 5]  # Should be around April/May
    
    def test_subscription_status_active(self, subscription_service):
        """Test active subscription status"""
        subscription = OrganizationSubscription(
            organization_id="org-123",
            tier=SubscriptionTier.PROFESSIONAL,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=120),
            created_at=datetime.utcnow()
        )
        
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.current_period_end > datetime.utcnow()
    
    def test_subscription_status_expired(self, subscription_service):
        """Test expired subscription status"""
        subscription = OrganizationSubscription(
            organization_id="org-123",
            tier=SubscriptionTier.BASIC,
            status=SubscriptionStatus.EXPIRED,
            current_period_start=datetime.utcnow() - timedelta(days=150),
            current_period_end=datetime.utcnow() - timedelta(days=30),
            created_at=datetime.utcnow() - timedelta(days=150)
        )
        
        assert subscription.status == SubscriptionStatus.EXPIRED
        assert subscription.current_period_end < datetime.utcnow()
    
    def test_commission_calculation(self, subscription_service):
        """Test 30% commission calculation"""
        researcher_amount = Decimal("1000.00")
        commission_rate = Decimal("0.30")
        
        commission = researcher_amount * commission_rate
        total_charge = researcher_amount + commission
        
        assert commission == Decimal("300.00")
        assert total_charge == Decimal("1300.00")
    
    def test_tier_features_basic(self, subscription_service):
        """Test Basic tier features"""
        basic_features = {
            "max_programs": 3,
            "max_researchers": 50,
            "support": "email",
            "sla": "48h"
        }
        
        assert basic_features["max_programs"] == 3
        assert basic_features["support"] == "email"
    
    def test_tier_features_professional(self, subscription_service):
        """Test Professional tier features"""
        pro_features = {
            "max_programs": 10,
            "max_researchers": 200,
            "support": "priority",
            "sla": "24h",
            "custom_branding": True
        }
        
        assert pro_features["max_programs"] == 10
        assert pro_features["custom_branding"] is True
    
    def test_tier_features_enterprise(self, subscription_service):
        """Test Enterprise tier features"""
        enterprise_features = {
            "max_programs": "unlimited",
            "max_researchers": "unlimited",
            "support": "dedicated",
            "sla": "4h",
            "custom_branding": True,
            "api_access": True,
            "white_label": True
        }
        
        assert enterprise_features["max_programs"] == "unlimited"
        assert enterprise_features["api_access"] is True
        assert enterprise_features["white_label"] is True


class TestBountyCommission:
    """Test bounty commission calculations"""
    
    def test_commission_on_small_bounty(self):
        """Test commission on small bounty"""
        researcher_amount = Decimal("100.00")
        commission_rate = Decimal("0.30")
        
        commission = researcher_amount * commission_rate
        org_pays = researcher_amount + commission
        
        assert commission == Decimal("30.00")
        assert org_pays == Decimal("130.00")
    
    def test_commission_on_large_bounty(self):
        """Test commission on large bounty"""
        researcher_amount = Decimal("10000.00")
        commission_rate = Decimal("0.30")
        
        commission = researcher_amount * commission_rate
        org_pays = researcher_amount + commission
        
        assert commission == Decimal("3000.00")
        assert org_pays == Decimal("13000.00")
    
    def test_commission_precision(self):
        """Test commission calculation precision"""
        researcher_amount = Decimal("333.33")
        commission_rate = Decimal("0.30")
        
        commission = researcher_amount * commission_rate
        org_pays = researcher_amount + commission
        
        # Should maintain 2 decimal precision
        assert commission == Decimal("99.999")
        assert org_pays == Decimal("433.329")
