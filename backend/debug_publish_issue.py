#!/usr/bin/env python3
"""Debug script to investigate program publish 400 error."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

program_id = "90d18e1d-5a42-423d-9d08-f89a8dbc2b46"

print("=" * 80)
print("PROGRAM PUBLISH DEBUG")
print("=" * 80)

# 1. Check if program exists
print("\n1. PROGRAM DETAILS:")
program_query = text("""
    SELECT 
        id, name, status, type, visibility, organization_id,
        created_at, updated_at
    FROM bounty_programs
    WHERE id = :program_id
""")
program = db.execute(program_query, {"program_id": program_id}).fetchone()

if program:
    print(f"   Program ID: {program.id}")
    print(f"   Name: {program.name}")
    print(f"   Status: {program.status}")
    print(f"   Type: {program.type}")
    print(f"   Visibility: {program.visibility}")
    print(f"   Organization ID: {program.organization_id}")
else:
    print("   ❌ Program not found!")
    sys.exit(1)

# 2. Check reward tiers
print("\n2. REWARD TIERS:")
tiers_query = text("""
    SELECT 
        id, severity, min_amount, max_amount
    FROM reward_tiers
    WHERE program_id = :program_id
    ORDER BY max_amount DESC
""")
tiers = db.execute(tiers_query, {"program_id": program_id}).fetchall()

if tiers:
    print(f"   Found {len(tiers)} reward tiers:")
    for tier in tiers:
        print(f"   - {tier.severity}: {tier.min_amount} - {tier.max_amount} ETB")
    
    critical_tier = tiers[0]
    critical_amount = critical_tier.max_amount
    print(f"\n   Critical tier max amount: {critical_amount} ETB")
else:
    print("   ❌ No reward tiers found!")
    print("   This is the issue - bounty programs need reward tiers to publish")

# 3. Check organization wallet
print("\n3. ORGANIZATION WALLET:")
wallet_query = text("""
    SELECT 
        wallet_id, owner_id, owner_type, balance, 
        reserved_balance, available_balance, currency
    FROM wallets
    WHERE owner_id = :org_id AND owner_type = 'organization'
""")
wallet = db.execute(wallet_query, {"org_id": program.organization_id}).fetchone()

if wallet:
    print(f"   Wallet ID: {wallet.wallet_id}")
    print(f"   Balance: {wallet.balance} {wallet.currency}")
    print(f"   Reserved: {wallet.reserved_balance} {wallet.currency}")
    print(f"   Available: {wallet.available_balance} {wallet.currency}")
    
    if tiers:
        if wallet.available_balance >= critical_amount:
            print(f"   ✅ Sufficient balance (need {critical_amount} ETB)")
        else:
            print(f"   ❌ Insufficient balance!")
            print(f"      Need: {critical_amount} ETB")
            print(f"      Have: {wallet.available_balance} ETB")
            print(f"      Shortfall: {critical_amount - wallet.available_balance} ETB")
else:
    print("   ❌ No wallet found for organization!")
    print("   Creating wallet would show 0 balance")

# 4. Check program scopes
print("\n4. PROGRAM SCOPES:")
scopes_query = text("""
    SELECT 
        id, asset_type, asset_identifier, is_in_scope
    FROM program_scopes
    WHERE program_id = :program_id
""")
scopes = db.execute(scopes_query, {"program_id": program_id}).fetchall()

if scopes:
    print(f"   Found {len(scopes)} scopes:")
    for scope in scopes:
        status = "IN SCOPE" if scope.is_in_scope else "OUT OF SCOPE"
        print(f"   - {scope.asset_type}: {scope.asset_identifier} ({status})")
else:
    print("   ⚠️  No scopes defined")

# 5. Summary
print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

issues = []
if not tiers:
    issues.append("❌ No reward tiers defined - CRITICAL")
elif not wallet or wallet.available_balance < critical_amount:
    issues.append(f"❌ Insufficient wallet balance - need {critical_amount} ETB")
if not scopes:
    issues.append("⚠️  No scopes defined - recommended but not blocking")

if issues:
    print("\nIssues preventing publish:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n✅ All checks passed - program should be publishable")

print("\n" + "=" * 80)

db.close()
