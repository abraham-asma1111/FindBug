"""
Setup Complete Finance Portal Test Data
Creates real database records for all Finance Portal pages
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.core.database import SessionLocal
from src.core.security import get_password_hash
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram
from src.domain.models.bounty_payment import BountyPayment, Wallet, WalletTransaction
from src.domain.models.payment_extended import PayoutRequest
from src.domain.models.kyc import KYCVerification
from src.utils.constants import UserRole


def create_finance_test_data():
    """Create comprehensive test data for Finance Portal"""
    db = SessionLocal()
    
    try:
        print("🚀 Setting up Finance Portal Test Data...")
        print("=" * 60)
        
        # 1. Create Finance Officer User
        print("\n1️⃣  Creating Finance Officer User...")
        finance_user = db.query(User).filter(User.email == "finance@findbug.com").first()
        if not finance_user:
            finance_user = User(
                id=uuid4(),
                email="finance@findbug.com",
                password_hash=get_password_hash("Finance123!"),
                role="finance_officer",
                full_name="Finance Officer",
                is_active=True,
                email_verified=True,
                mfa_enabled=False
            )
            db.add(finance_user)
            db.commit()
            print(f"   ✅ Created: finance@findbug.com")
        else:
            print(f"   ℹ️  Already exists: finance@findbug.com")
        
        # 2. Create Test Researchers
        print("\n2️⃣  Creating Test Researchers...")
        researchers = []
        for i in range(1, 6):
            user = db.query(User).filter(User.email == f"researcher{i}@test.com").first()
            if not user:
                user = User(
                    id=uuid4(),
                    email=f"researcher{i}@test.com",
                    password_hash=get_password_hash("Test123!"),
                    role="researcher",
                    full_name=f"Test Researcher {i}",
                    is_active=True,
                    email_verified=True
                )
                db.add(user)
                db.flush()
                
                researcher = Researcher(
                    id=uuid4(),
                    user_id=user.id,
                    username=f"researcher{i}",
                    bio=f"Security researcher #{i}",
                    reputation_score=1000 + (i * 100),
                    total_earnings=Decimal(5000 + (i * 1000))
                )
                db.add(researcher)
                researchers.append(researcher)
                print(f"   ✅ Created: researcher{i}@test.com")
            else:
                researcher = db.query(Researcher).filter(Researcher.user_id == user.id).first()
                if researcher:
                    researchers.append(researcher)
                print(f"   ℹ️  Already exists: researcher{i}@test.com")
        
        db.commit()
        
        # 3. Create Test Organizations
        print("\n3️⃣  Creating Test Organizations...")
        organizations = []
        org_names = ["TechCorp", "SecureBank", "HealthTech", "FinanceApp", "CloudServices"]
        for i, name in enumerate(org_names, 1):
            user = db.query(User).filter(User.email == f"org{i}@test.com").first()
            if not user:
                user = User(
                    id=uuid4(),
                    email=f"org{i}@test.com",
                    password_hash=get_password_hash("Test123!"),
                    role="organization",
                    full_name=name,
                    is_active=True,
                    email_verified=True
                )
                db.add(user)
                db.flush()
                
                org = Organization(
                    id=uuid4(),
                    user_id=user.id,
                    name=name,
                    company_name=name,
                    industry="Technology",
                    subscription_type=["free", "basic", "premium", "enterprise"][i % 4],
                    subscription_status="active",
                    subscription_amount=Decimal([0, 99, 299, 999][i % 4])
                )
                db.add(org)
                organizations.append(org)
                print(f"   ✅ Created: {name}")
            else:
                org = db.query(Organization).filter(Organization.user_id == user.id).first()
                if org:
                    organizations.append(org)
                print(f"   ℹ️  Already exists: {name}")
        
        db.commit()
        
        # 4. Create Test Programs
        print("\n4️⃣  Creating Test Programs...")
        programs = []
        for i, org in enumerate(organizations[:3], 1):
            program = db.query(BountyProgram).filter(
                BountyProgram.organization_id == org.id
            ).first()
            
            if not program:
                program = BountyProgram(
                    id=uuid4(),
                    organization_id=org.id,
                    name=f"{org.name} Bug Bounty Program",
                    description=f"Security testing program for {org.name}",
                    program_type="public",
                    status="active",
                    min_bounty=Decimal(100),
                    max_bounty=Decimal(10000)
                )
                db.add(program)
                programs.append(program)
                print(f"   ✅ Created program for {org.name}")
            else:
                programs.append(program)
                print(f"   ℹ️  Program exists for {org.name}")
        
        db.commit()
        
        # 5. Create Test Reports
        print("\n5️⃣  Creating Test Vulnerability Reports...")
        reports = []
        severities = ["critical", "high", "medium", "low"]
        statuses = ["accepted", "accepted", "triaged", "submitted"]
        
        for i, (researcher, program) in enumerate(zip(researchers[:4], programs * 2), 1):
            report = VulnerabilityReport(
                id=uuid4(),
                program_id=program.id,
                researcher_id=researcher.id,
                report_number=f"REP-2026-{str(i).zfill(3)}",
                title=f"Security Vulnerability #{i}",
                description=f"Detailed description of vulnerability #{i}",
                steps_to_reproduce=f"Steps to reproduce vulnerability #{i}",
                impact_assessment=f"Impact assessment for vulnerability #{i}",
                suggested_severity=severities[i % 4],
                severity=severities[i % 4],
                status=statuses[i % 4],
                cvss_score=Decimal(7.5 + (i % 3)),
                submitted_at=datetime.utcnow() - timedelta(days=30-i)
            )
            db.add(report)
            reports.append(report)
        
        db.commit()
        print(f"   ✅ Created {len(reports)} vulnerability reports")
        
        # 6. Create Wallets for Researchers
        print("\n6️⃣  Creating Researcher Wallets...")
        wallets = []
        for researcher in researchers:
            wallet = db.query(Wallet).filter(
                Wallet.owner_id == researcher.id,
                Wallet.owner_type == "researcher"
            ).first()
            
            if not wallet:
                wallet = Wallet(
                    id=uuid4(),
                    owner_id=researcher.id,
                    owner_type="researcher",
                    balance=Decimal(1000 + (len(wallets) * 500)),
                    currency="ETB"
                )
                db.add(wallet)
                wallets.append(wallet)
        
        db.commit()
        print(f"   ✅ Created {len(wallets)} wallets")
        
        # 7. Create Bounty Payments
        print("\n7️⃣  Creating Bounty Payments...")
        payment_statuses = ["pending", "approved", "completed", "pending"]
        payments = []
        
        for i, report in enumerate(reports[:4], 1):
            program = db.query(BountyProgram).filter(BountyProgram.id == report.program_id).first()
            org = db.query(Organization).filter(Organization.id == program.organization_id).first()
            
            researcher_amount = Decimal(500 * i)
            commission = researcher_amount * Decimal(0.15)
            total = researcher_amount + commission
            
            payment = BountyPayment(
                payment_id=uuid4(),
                transaction_id=f"TXN-{uuid4().hex[:12].upper()}",
                report_id=report.id,
                researcher_id=report.researcher_id,
                organization_id=org.id,
                researcher_amount=researcher_amount,
                commission_amount=commission,
                total_amount=total,
                status=payment_statuses[i % 4],
                payment_method="bank_transfer",
                payout_deadline=datetime.utcnow() + timedelta(days=30),
                created_at=datetime.utcnow() - timedelta(days=20-i)
            )
            
            if payment.status == "completed":
                payment.completed_at = datetime.utcnow() - timedelta(days=10-i)
            
            db.add(payment)
            payments.append(payment)
        
        db.commit()
        print(f"   ✅ Created {len(payments)} bounty payments")
        
        # 8. Create Payout Requests
        print("\n8️⃣  Creating Payout Requests...")
        payout_statuses = ["requested", "processing", "completed", "requested"]
        payouts = []
        
        for i, researcher in enumerate(researchers[:4], 1):
            payout = PayoutRequest(
                id=uuid4(),
                researcher_id=researcher.id,
                amount=Decimal(200 * i),
                payment_method=["bank_transfer", "paypal", "crypto"][i % 3],
                status=payout_statuses[i % 4],
                created_at=datetime.utcnow() - timedelta(days=15-i)
            )
            
            if payout.status in ["processing", "completed"]:
                payout.processed_at = datetime.utcnow() - timedelta(days=10-i)
            
            db.add(payout)
            payouts.append(payout)
        
        db.commit()
        print(f"   ✅ Created {len(payouts)} payout requests")
        
        # 9. Create Wallet Transactions
        print("\n9️⃣  Creating Wallet Transactions...")
        transactions = []
        
        for i, wallet in enumerate(wallets[:4], 1):
            # Credit transaction
            txn1 = WalletTransaction(
                id=uuid4(),
                wallet_id=wallet.id,
                transaction_type="credit",
                amount=Decimal(500 * i),
                description=f"Bounty payment #{i}",
                created_at=datetime.utcnow() - timedelta(days=20-i)
            )
            db.add(txn1)
            transactions.append(txn1)
            
            # Debit transaction
            txn2 = WalletTransaction(
                id=uuid4(),
                wallet_id=wallet.id,
                transaction_type="debit",
                amount=Decimal(200 * i),
                description=f"Payout request #{i}",
                created_at=datetime.utcnow() - timedelta(days=15-i)
            )
            db.add(txn2)
            transactions.append(txn2)
        
        db.commit()
        print(f"   ✅ Created {len(transactions)} wallet transactions")
        
        # 10. Create KYC Verifications
        print("\n🔟 Creating KYC Verifications...")
        kyc_statuses = ["pending", "approved", "rejected", "pending"]
        kycs = []
        
        for i, researcher in enumerate(researchers[:4], 1):
            kyc = db.query(KYCVerification).filter(
                KYCVerification.user_id == researcher.user_id
            ).first()
            
            if not kyc:
                kyc = KYCVerification(
                    id=uuid4(),
                    user_id=researcher.user_id,
                    document_type=["passport", "national_id", "drivers_license"][i % 3],
                    document_number=f"DOC{uuid4().hex[:8].upper()}",
                    status=kyc_statuses[i % 4],
                    submitted_at=datetime.utcnow() - timedelta(days=25-i)
                )
                
                if kyc.status in ["approved", "rejected"]:
                    kyc.reviewed_at = datetime.utcnow() - timedelta(days=20-i)
                    kyc.reviewed_by = finance_user.id
                
                db.add(kyc)
                kycs.append(kyc)
        
        db.commit()
        print(f"   ✅ Created {len(kycs)} KYC verifications")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ FINANCE PORTAL TEST DATA SETUP COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Finance Officer: 1")
        print(f"   • Researchers: {len(researchers)}")
        print(f"   • Organizations: {len(organizations)}")
        print(f"   • Programs: {len(programs)}")
        print(f"   • Reports: {len(reports)}")
        print(f"   • Bounty Payments: {len(payments)}")
        print(f"   • Payout Requests: {len(payouts)}")
        print(f"   • Wallet Transactions: {len(transactions)}")
        print(f"   • KYC Verifications: {len(kycs)}")
        
        print(f"\n🔐 Login Credentials:")
        print(f"   Finance Officer:")
        print(f"   • Email: finance@findbug.com")
        print(f"   • Password: Finance123!")
        
        print(f"\n🎯 Test the Finance Portal:")
        print(f"   1. Login as finance officer")
        print(f"   2. Navigate to /finance/dashboard")
        print(f"   3. Check all pages have real data:")
        print(f"      - Dashboard (KPIs, charts)")
        print(f"      - Payments (list, approve/reject)")
        print(f"      - Payouts (list, process)")
        print(f"      - KYC (list, approve/reject)")
        print(f"      - Transactions (all wallet activity)")
        print(f"      - Organizations (subscriptions)")
        print(f"      - Reports (generate financial reports)")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_finance_test_data()
