"""Create a test bounty payment for platform wallet testing."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    from src.services.payment_service import PaymentService
    from src.domain.models.user import User
    from src.domain.models.report import VulnerabilityReport
    
    # Get a valid report
    report = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.status == "valid"
    ).first()
    
    if not report:
        print("❌ No valid reports found")
        print("   Create and validate a vulnerability report first")
        exit(1)
    
    print(f"✅ Found valid report: {report.id}")
    print(f"   Title: {report.title}")
    
    # Get finance officer
    finance_user = db.query(User).filter(User.email == "finance@findbug.com").first()
    if not finance_user:
        print("❌ Finance officer not found")
        exit(1)
    
    # Create bounty payment
    payment_service = PaymentService(db)
    
    bounty_amount = Decimal("1000.00")  # 1000 ETB bounty
    
    print(f"\n🔄 Creating bounty payment...")
    print(f"   Bounty Amount: {bounty_amount} ETB")
    print(f"   Expected Commission: {bounty_amount * Decimal('0.45')} ETB (45%)")
    print(f"   Expected Researcher Amount: {bounty_amount * Decimal('0.85')} ETB (85%)")
    
    payment = payment_service.create_bounty_payment(
        report_id=report.id,
        bounty_amount=bounty_amount,
        approved_by=finance_user.id
    )
    
    print(f"\n✅ Bounty Payment Created!")
    print(f"   Payment ID: {payment.payment_id}")
    print(f"   Transaction ID: {payment.transaction_id}")
    print(f"   Researcher Amount: {payment.researcher_amount} ETB")
    print(f"   Commission Amount: {payment.commission_amount} ETB")
    print(f"   Total Amount: {payment.total_amount} ETB")
    print(f"   Status: {payment.status}")
    
    print(f"\n💡 Now run: python3 test_platform_wallet.py")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
