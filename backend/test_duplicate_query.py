#!/usr/bin/env python3
"""Test the duplicate count query directly."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, func, case
from sqlalchemy.orm import sessionmaker
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.user import User

DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("\n=== Testing SQLAlchemy Query ===")

# Build the exact same query as the endpoint
query = db.query(
    Researcher.id,
    Researcher.username,
    Researcher.reputation_score,
    User.email,
    func.count(VulnerabilityReport.id).label('total_reports'),
    func.sum(case((VulnerabilityReport.status == 'valid', 1), else_=0)).label('valid_reports'),
    func.sum(case((VulnerabilityReport.is_duplicate == True, 1), else_=0)).label('duplicate_reports'),
    func.sum(case((VulnerabilityReport.status == 'invalid', 1), else_=0)).label('invalid_reports')
).join(
    User, Researcher.user_id == User.id
).outerjoin(
    VulnerabilityReport, Researcher.id == VulnerabilityReport.researcher_id
).group_by(
    Researcher.id, Researcher.username, Researcher.reputation_score, User.email
)

results = query.all()

print(f"\nTotal researchers: {len(results)}")
print(f"\nFirst 5 researchers with reports:")
count = 0
for r in results:
    if r.total_reports > 0:
        spam_score = ((r.duplicate_reports or 0) + (r.invalid_reports or 0)) / r.total_reports * 100 if r.total_reports > 0 else 0
        print(f"\n{r.username} ({r.email})")
        print(f"  Total: {r.total_reports}")
        print(f"  Valid: {r.valid_reports}")
        print(f"  Duplicates: {r.duplicate_reports}")
        print(f"  Invalid: {r.invalid_reports}")
        print(f"  Spam Score: {spam_score:.1f}%")
        count += 1
        if count >= 5:
            break

db.close()
