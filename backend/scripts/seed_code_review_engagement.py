#!/usr/bin/env python3
"""
Seed a code review engagement for local E2E testing.

Usage (from backend/):
  python scripts/seed_code_review_engagement.py
  python scripts/seed_code_review_engagement.py --org-email org@example.com --researcher-email researcher@test.com
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.code_review import ReviewType
from src.services.code_review_service import CodeReviewService


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed code review engagement")
    parser.add_argument("--org-email", default="organization@example.com")
    parser.add_argument("--researcher-email", default="researcher@test.com")
    parser.add_argument("--title", default="NovaBank API security review (demo)")
    parser.add_argument(
        "--repo",
        default="https://github.com/example/novabank-api",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        org = db.query(User).filter(User.email == args.org_email).first()
        researcher = db.query(User).filter(User.email == args.researcher_email).first()

        if not org or not org.organization:
            print(f"Organization profile not found for: {args.org_email}")
            sys.exit(1)
        if not researcher or not researcher.researcher:
            print(f"Researcher profile not found for: {args.researcher_email}")
            sys.exit(1)

        service = CodeReviewService(db)
        engagement = service.create_engagement(
            organization_id=org.organization.id,
            title=args.title,
            repository_url=args.repo,
            review_type=ReviewType.SECURITY,
        )
        engagement = service.assign_reviewer(engagement.id, researcher.researcher.id)

        print("Code review engagement ready for E2E testing:")
        print(f"  engagement_id: {engagement.id}")
        print(f"  organization:  {args.org_email}")
        print(f"  researcher:    {args.researcher_email}")
        print(f"  status:        {engagement.status.value}")
        print()
        print("Researcher: /researcher/programs/code-review → Start review → Add findings → Submit report")
        print("Organization: /organization/services/code-review")
    finally:
        db.close()


if __name__ == "__main__":
    main()
