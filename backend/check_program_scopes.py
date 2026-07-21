#!/usr/bin/env python3
"""Check scopes for a program."""

import sys
sys.path.insert(0, '/home/abraham/Desktop/Final-year-project/backend')

from src.core.database import SessionLocal
from src.domain.models.program import BountyProgram, ProgramScope
from uuid import UUID

def check_program_scopes(program_id: str):
    """Check scopes for a program."""
    db = SessionLocal()
    
    try:
        # Get program
        program = db.query(BountyProgram).filter(
            BountyProgram.id == UUID(program_id)
        ).first()
        
        if not program:
            print(f"✗ Program {program_id} not found")
            return
        
        print(f"✓ Program found: {program.name}")
        print(f"  Status: {program.status}")
        print(f"  Type: {program.type}")
        
        # Get scopes
        scopes = db.query(ProgramScope).filter(
            ProgramScope.program_id == UUID(program_id)
        ).all()
        
        print(f"\n  Scopes ({len(scopes)}):")
        for scope in scopes:
            print(f"    - {scope.asset_identifier} ({scope.asset_type})")
            print(f"      In scope: {scope.is_in_scope}")
            print(f"      Max severity: {scope.max_severity}")
        
    finally:
        db.close()


if __name__ == "__main__":
    program_id = "0b3749a2-c70e-482b-b4fe-e36c859706e7"
    check_program_scopes(program_id)
