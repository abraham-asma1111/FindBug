import asyncio
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.services.notification_service import NotificationService
from datetime import datetime, timedelta

def run():
    db = SessionLocal()
    service = NotificationService(db)
    
    # Get the admin
    admin = db.query(User).filter(User.role == 'admin').first()
    if not admin:
        print("No admin user found")
        return

    print(f"Seeding test notifications for {admin.email}...")

    # Clear old notifications for cleaner testing
    from sqlalchemy import text
    db.execute(text("DELETE FROM notifications WHERE user_id = :uid"), {"uid": admin.id})
    db.commit()

    # Seed 1: Critical (High priority glow)
    service.notify_admin_bounty_approved(
        report_title="Remote Code Execution via Image Upload",
        report_number="REP-1029",
        organization_name="TechCorp Global",
        bounty_amount=15000.00,
        report_id=None
    )

    # Seed 2: High (Warning glow)
    service.notify_admin_report_submitted(
        program_name="FindBug Public Program",
        report_title="SQL Injection in Login Endpoint",
        report_number="REP-1030",
        researcher_email="hacker@elite.com",
        severity="high",
        report_id=None
    )

    # Seed 3: Medium (Info glow)
    service.notify_admin_program_created(
        program_name="Mobile App VDP",
        organization_name="Fintech Solutions Ltd.",
        program_id=None
    )

    # Seed 4: Low (Success/Green glow)
    service.notify_admin_payment_processed(
        report_title="XSS in Dashboard",
        report_number="REP-0992",
        researcher_email="bounty_hunter99@gmail.com",
        amount=2500.00,
        report_id=None
    )

    # Seed 5: Triage Validation
    service.notify_admin_report_validated(
        report_title="Authentication Bypass",
        report_number="REP-1055",
        specialist_email="triage@findbug.com",
        new_status="valid",
        report_id=None
    )

    print("✅ 5 beautifully structured test notifications seeded successfully.")
    db.close()

run()
