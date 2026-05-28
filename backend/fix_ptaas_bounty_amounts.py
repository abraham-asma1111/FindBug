"""Fix PTaaS bounty amounts based on new calculation logic."""
import psycopg2
from decimal import Decimal

# New multipliers
PTAAS_SEVERITY_MULTIPLIER = {
    "critical": Decimal("1.50"),
    "high": Decimal("1.00"),
    "medium": Decimal("0.60"),
    "low": Decimal("0.30"),
    "info": Decimal("0.10"),
}

conn = psycopg2.connect(
    dbname="bug_bounty_production",
    user="bugbounty_user",
    password="changeme123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

print("=== Recalculating PTaaS Bounty Amounts ===\n")

# Get all findings with bounty amounts
cur.execute("""
    SELECT f.id, f.engagement_id, f.title, f.severity, f.bounty_amount, e.base_price
    FROM ptaas_findings f
    JOIN ptaas_engagements e ON f.engagement_id = e.id
    WHERE f.bounty_amount IS NOT NULL
    ORDER BY f.discovered_at DESC
""")

findings = cur.fetchall()
updated_count = 0

for finding in findings:
    finding_id, engagement_id, title, severity, old_bounty, base_price = finding
    
    # Calculate new bounty amount
    severity_key = (severity or "high").lower()
    multiplier = PTAAS_SEVERITY_MULTIPLIER.get(severity_key, PTAAS_SEVERITY_MULTIPLIER["high"])
    new_bounty = (Decimal(str(base_price)) * multiplier).quantize(Decimal("0.01"))
    
    print(f"Finding: {title}")
    print(f"  Severity: {severity}")
    print(f"  Base Price: {base_price} ETB")
    print(f"  Old Bounty: {old_bounty} ETB")
    print(f"  New Bounty: {new_bounty} ETB")
    print(f"  Multiplier: {multiplier}")
    
    # Update the bounty amount
    cur.execute("""
        UPDATE ptaas_findings
        SET bounty_amount = %s
        WHERE id = %s
    """, (new_bounty, finding_id))
    
    updated_count += 1
    print(f"  ✓ Updated\n")

conn.commit()
print(f"\n=== Summary ===")
print(f"Total findings updated: {updated_count}")

cur.close()
conn.close()
