#!/usr/bin/env python3
"""Delete duplicate template from database."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.domain.models.triage import TriageTemplate

# Create database connection
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Find and delete templates with name 'xsss'
    templates = db.query(TriageTemplate).filter(TriageTemplate.name == 'xsss').all()
    
    print(f"Found {len(templates)} template(s) with name 'xsss'")
    
    for template in templates:
        print(f"Deleting template: {template.id} - {template.name} - {template.title}")
        db.delete(template)
    
    db.commit()
    print("Templates deleted successfully")
    
    # List all templates
    all_templates = db.query(TriageTemplate).all()
    print(f"\nRemaining templates: {len(all_templates)}")
    for t in all_templates:
        print(f"  - {t.name}: {t.title} ({t.category})")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
