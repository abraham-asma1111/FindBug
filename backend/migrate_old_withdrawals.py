"""
Migrate old withdrawal transactions to payout requests
"""
from src.core.database import SessionLocal
from src.domain.models.bounty_payment import WalletTransaction, Wallet
from src.domain.models.payment_extended import PayoutRequest
from src.domain.models.researcher import Researcher
from datetime import datetime
from uuid import uuid4

db = SessionLocal()

try:
    # Find all withdrawal transactions that don't have corresponding payout requests
    withdrawal_txs = db.query(WalletTransaction).filter(
        WalletTransaction.reference_type == 'withdrawal'
    ).all()
    
    print(f'Found {len(withdrawal_txs)} withdrawal transactions')
    
    # Get existing payout request transaction IDs to avoid duplicates
    existing_payouts = db.query(PayoutRequest).all()
    print(f'Found {len(existing_payouts)} existing payout requests')
    
    created_count = 0
    
    for tx in withdrawal_txs:
        # Get the wallet to find the owner
        wallet = db.query(Wallet).filter(Wallet.wallet_id == tx.wallet_id).first()
        if not wallet:
            print(f'  ⚠️  Wallet not found for transaction {tx.transaction_id}')
            continue
        
        # Get researcher
        researcher = db.query(Researcher).filter(Researcher.user_id == wallet.owner_id).first()
        if not researcher:
            print(f'  ⚠️  Researcher not found for wallet owner {wallet.owner_id}')
            continue
        
        # Check if payout request already exists for this transaction
        existing = db.query(PayoutRequest).filter(
            PayoutRequest.researcher_id == researcher.id,
            PayoutRequest.amount == tx.amount,
            PayoutRequest.created_at == tx.created_at
        ).first()
        
        if existing:
            print(f'  ℹ️  Payout request already exists for transaction {tx.transaction_id}')
            continue
        
        # Create payout request
        payout = PayoutRequest(
            id=uuid4(),
            researcher_id=researcher.id,
            amount=tx.amount,
            payment_method='bank_transfer',  # Default
            payment_details={},
            status='pending',
            created_at=tx.created_at
        )
        
        db.add(payout)
        created_count += 1
        print(f'  ✅ Created payout request for {tx.amount} ETB (tx: {tx.transaction_id})')
    
    db.commit()
    print(f'\n✅ Migration complete! Created {created_count} payout requests')
    
except Exception as e:
    db.rollback()
    print(f'\n❌ Error: {e}')
    raise
finally:
    db.close()
