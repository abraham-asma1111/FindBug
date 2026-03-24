"""
Commission Service — Calculates platform fees
"""
from typing import Dict
from src.core.constants import PLATFORM_COMMISSION_RATE
from src.core.exceptions import ValidationException

class CommissionService:
    @staticmethod
    def calculate_commission(bounty_amount: float) -> Dict[str, float]:
        """
        Calculates the platform commission and researcher payout.
        Platform takes a percentage of the total bounty amount.
        """
        if bounty_amount < 0:
            raise ValidationException("Bounty amount cannot be negative.")
        
        commission_amount = bounty_amount * PLATFORM_COMMISSION_RATE
        researcher_payout = bounty_amount - commission_amount
        
        # Round to 2 decimal places
        return {
            "total_bounty": round(bounty_amount, 2),
            "platform_commission": round(commission_amount, 2),
            "researcher_payout": round(researcher_payout, 2),
            "commission_rate": PLATFORM_COMMISSION_RATE
        }
