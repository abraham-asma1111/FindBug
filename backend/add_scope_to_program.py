#!/usr/bin/env python3
"""Quick script to add a scope to an existing program."""

import sys
from uuid import UUID
from sqlalchemy.orm import Session

# Add the src directory to the path
sys.path.insert(0, '/home/abraham/Desktop/Final-year-project/backend')

from src.core.database import SessionLocal
from src.domain.models.program import ProgramScope
from uuid import uuid4

def add_scope_to_program(program_id: str, asset_identifier: str):
    """Add a scope to a program."""
    db: Session = SessionLocal()
    
    try:
        # Create scope
        scope = ProgramScope(
            id=uuid4(),
            program_id=UUID(program_id),
            asset_type='web_app',
            asset_identifier=asset_identifier,
            is_in_scope=True,
            description=f'In-scope asset: {asset_identifier}',
            max_severity='critical'
        )
        
        db.add(scope)
        db.commit()
        db.refresh(scope)
        
        print(f"✓ Successfully added scope '{asset_identifier}' to program {program_id}")
        print(f"  Scope ID: {scope.id}")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # Add scope to the existing program
    program_id = "0b3749a2-c70e-482b-b4fe-e36c859706e7"
    asset_identifier = "*.example.com"
    
    print(f"Adding scope to program {program_id}...")
    add_scope_to_program(program_id, asset_identifier)
