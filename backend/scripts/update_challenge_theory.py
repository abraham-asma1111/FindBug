#!/usr/bin/env python3
"""Apply simulation/challenge_theory.json to existing simulation_challenges rows."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from sqlalchemy import text
from src.core.database import SessionLocal

theory_path = Path(__file__).resolve().parent.parent.parent / "simulation" / "challenge_theory.json"
data = json.loads(theory_path.read_text(encoding="utf-8"))

db = SessionLocal()
for vuln, body in data.items():
    db.execute(
        text(
            """
            UPDATE simulation_challenges
            SET description = :description, documentation = :documentation
            WHERE vulnerability_type = :vuln
            """
        ),
        {
            "vuln": vuln,
            "description": body.get("description", ""),
            "documentation": body.get("documentation", ""),
        },
    )
db.commit()
print(f"Updated theory for {len(data)} vulnerability types.")
