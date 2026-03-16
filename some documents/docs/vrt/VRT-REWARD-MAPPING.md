# VRT Reward Tier Mapping

## Default Reward Structure

### P1 - Critical
- **Severity**: Critical
- **Default Range**: $2,000 - $10,000
- **Examples**:
  - Remote Code Execution (RCE)
  - Authentication Bypass
  - SQL Injection with data access
  - Complete account takeover

### P2 - High
- **Severity**: High
- **Default Range**: $500 - $2,000
- **Examples**:
  - Stored XSS
  - IDOR with sensitive data access
  - CSRF on critical functions
  - Privilege escalation

### P3 - Medium
- **Severity**: Medium
- **Default Range**: $100 - $500
- **Examples**:
  - Reflected XSS
  - Information disclosure
  - CSRF on non-critical functions
  - Rate limiting bypass

### P4 - Low
- **Severity**: Low
- **Default Range**: $50 - $100
- **Examples**:
  - Self-XSS
  - Minor information leakage
  - Missing security headers
  - Clickjacking

### P5 - Informational
- **Severity**: Informational
- **Default Range**: $0 - $50 (or no reward)
- **Examples**:
  - Outdated software versions
  - Best practice recommendations
  - Minor configuration issues

---

## Program-Specific Customization

Organizations can customize reward tiers:

```json
{
  "program_id": 123,
  "reward_tiers": {
    "P1": {
      "min": 5000,
      "max": 20000,
      "currency": "USD"
    },
    "P2": {
      "min": 1000,
      "max": 5000,
      "currency": "USD"
    },
    "P3": {
      "min": 250,
      "max": 1000,
      "currency": "USD"
    },
    "P4": {
      "min": 100,
      "max": 250,
      "currency": "USD"
    },
    "P5": {
      "min": 0,
      "max": 50,
      "currency": "USD"
    }
  }
}
```

---

## Ethiopian Birr Conversion

For Ethiopian organizations, rewards in ETB:

### P1 - Critical
- **Range**: 110,000 - 550,000 ETB (at 55 ETB/USD)

### P2 - High
- **Range**: 27,500 - 110,000 ETB

### P3 - Medium
- **Range**: 5,500 - 27,500 ETB

### P4 - Low
- **Range**: 2,750 - 5,500 ETB

### P5 - Informational
- **Range**: 0 - 2,750 ETB

---

## Automatic Reward Calculation

```python
def calculate_reward(vrt_priority: str, program_tiers: dict, impact_multiplier: float = 1.0) -> int:
    """
    Calculate reward based on VRT priority and program tiers
    
    Args:
        vrt_priority: P1, P2, P3, P4, or P5
        program_tiers: Program-specific reward tiers
        impact_multiplier: Adjustment factor (0.5 - 2.0)
    
    Returns:
        Suggested reward amount
    """
    tier = program_tiers.get(vrt_priority)
    base_reward = (tier['min'] + tier['max']) / 2
    adjusted_reward = base_reward * impact_multiplier
    
    # Ensure within tier bounds
    return max(tier['min'], min(tier['max'], adjusted_reward))
```
