"""Add test attachments to reports for testing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport, ReportAttachment
from datetime import datetime
import uuid

def add_test_attachments():
    """Add test attachments to existing reports."""
    db: Session = SessionLocal()
    
    try:
        # Get first 3 reports
        reports = db.query(VulnerabilityReport).limit(3).all()
        
        if not reports:
            print("No reports found in database")
            return
        
        attachment_count = 0
        
        for report in reports:
            # Add 2-3 attachments per report
            attachments = [
                {
                    "filename": "screenshot_vulnerability.png",
                    "original_filename": "screenshot_vulnerability.png",
                    "file_type": "image/png",
                    "file_size": 245678,
                    "storage_path": f"/uploads/reports/{report.id}/screenshot_vulnerability.png",
                    "is_safe": True
                },
                {
                    "filename": "proof_of_concept.mp4",
                    "original_filename": "proof_of_concept.mp4",
                    "file_type": "video/mp4",
                    "file_size": 5234567,
                    "storage_path": f"/uploads/reports/{report.id}/proof_of_concept.mp4",
                    "is_safe": True
                },
                {
                    "filename": "technical_details.pdf",
                    "original_filename": "technical_details.pdf",
                    "file_type": "application/pdf",
                    "file_size": 123456,
                    "storage_path": f"/uploads/reports/{report.id}/technical_details.pdf",
                    "is_safe": True
                }
            ]
            
            for att_data in attachments:
                attachment = ReportAttachment(
                    id=uuid.uuid4(),
                    report_id=report.id,
                    uploaded_by=report.researcher.user_id if report.researcher else None,
                    uploaded_at=datetime.utcnow(),
                    scanned_at=datetime.utcnow(),
                    **att_data
                )
                db.add(attachment)
                attachment_count += 1
            
            print(f"Added {len(attachments)} attachments to report {report.report_number}")
        
        db.commit()
        print(f"\n✅ Successfully added {attachment_count} test attachments to {len(reports)} reports")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_attachments()
