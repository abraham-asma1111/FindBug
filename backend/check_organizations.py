#!/usr/bin/env python3
"""Check organizations data in database."""

import psycopg2

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="bug_bounty_production",
    user="bugbounty_user",
    password="changeme123"
)

cursor = conn.cursor()

print("=" * 80)
print("ORGANIZATIONS DATA")
print("=" * 80)

# Check organizations with subscription data
cursor.execute("""
    SELECT 
        o.id,
        o.company_name,
        o.industry,
        o.website,
        o.subscription_type,
        o.created_at,
        u.email,
        os.tier,
        os.status,
        os.subscription_fee,
        os.currency,
        os.next_billing_date
    FROM organizations o
    LEFT JOIN users u ON o.user_id = u.id
    LEFT JOIN organization_subscriptions os ON o.id = os.organization_id
    ORDER BY o.created_at DESC
""")

orgs = cursor.fetchall()
print(f"\nTotal Organizations: {len(orgs)}")

for i, org in enumerate(orgs, 1):
    print(f"\n{i}. {org[1] or 'N/A'}")
    print(f"   ID: {org[0]}")
    print(f"   Industry: {org[2] or 'N/A'}")
    print(f"   Website: {org[3] or 'N/A'}")
    print(f"   Subscription Type: {org[4] or 'N/A'}")
    print(f"   Email: {org[6] or 'N/A'}")
    print(f"   Created: {org[5]}")
    
    if org[7]:  # Has subscription
        print(f"   Subscription Tier: {org[7]}")
        print(f"   Subscription Status: {org[8]}")
        print(f"   Subscription Fee: {org[9]} {org[10]}")
        print(f"   Next Billing: {org[11]}")
    
    # Check wallet balance
    cursor.execute("""
        SELECT balance, currency
        FROM wallets
        WHERE owner_id = (SELECT user_id FROM organizations WHERE id = %s)
        AND owner_type = 'organization'
    """, (org[0],))
    
    wallet = cursor.fetchone()
    if wallet:
        print(f"   Wallet Balance: {wallet[0]} {wallet[1]}")
    
    # Check active programs
    cursor.execute("""
        SELECT COUNT(*)
        FROM bounty_programs
        WHERE organization_id = %s AND status = 'active'
    """, (org[0],))
    
    active_programs = cursor.fetchone()[0]
    print(f"   Active Programs: {active_programs}")
    
    # Check total bounty payments
    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0)
        FROM bounty_payments bp
        JOIN bounty_programs prog ON bp.program_id = prog.id
        WHERE prog.organization_id = %s AND bp.status = 'completed'
    """, (org[0],))
    
    payment_data = cursor.fetchone()
    print(f"   Total Payments: {payment_data[0]} ({payment_data[1]} ETB)")

cursor.close()
conn.close()

print("\n" + "=" * 80)
