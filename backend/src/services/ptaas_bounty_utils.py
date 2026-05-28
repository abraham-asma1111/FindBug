"""PTaaS bounty amount calculation from engagement base price."""
from decimal import Decimal
from typing import Optional

# Multiplier applied to base_price per validated finding by severity
# For PTaaS, base_price is the baseline bounty amount, and severity adjusts it
PTAAS_SEVERITY_MULTIPLIER = {
    "critical": Decimal("1.50"),  # 150% of base price
    "high": Decimal("1.00"),      # 100% of base price (baseline)
    "medium": Decimal("0.60"),    # 60% of base price
    "low": Decimal("0.30"),       # 30% of base price
    "info": Decimal("0.10"),      # 10% of base price
}


def calculate_ptaas_bounty_amount(base_price: Optional[Decimal], severity: Optional[str]) -> Optional[Decimal]:
    """
    Derive per-finding bounty from engagement base_price and triage severity.
    
    For PTaaS engagements, base_price represents the baseline bounty amount per finding.
    The severity multiplier adjusts this amount based on the finding's severity level.
    
    Example: If base_price = 10,000 ETB:
    - Critical: 10,000 * 1.50 = 15,000 ETB
    - High: 10,000 * 1.00 = 10,000 ETB
    - Medium: 10,000 * 0.60 = 6,000 ETB
    - Low: 10,000 * 0.30 = 3,000 ETB
    - Info: 10,000 * 0.10 = 1,000 ETB
    """
    if base_price is None:
        return None
    price = Decimal(str(base_price))
    if price <= 0:
        return None
    key = (severity or "high").lower()
    multiplier = PTAAS_SEVERITY_MULTIPLIER.get(key, PTAAS_SEVERITY_MULTIPLIER["high"])
    amount = (price * multiplier).quantize(Decimal("0.01"))
    return amount if amount > 0 else None
