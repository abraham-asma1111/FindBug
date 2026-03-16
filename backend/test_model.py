#!/usr/bin/env python3
"""
Test script to check if Researcher model has username attribute
"""
import sys
sys.path.append('src')

from src.domain.models.researcher import Researcher

print("Researcher model attributes:")
for attr in dir(Researcher):
    if not attr.startswith('_'):
        print(f"  - {attr}")

print("\nChecking for username attribute:")
print(f"  hasattr(Researcher, 'username'): {hasattr(Researcher, 'username')}")

if hasattr(Researcher, '__table__'):
    print("\nTable columns:")
    for column in Researcher.__table__.columns:
        print(f"  - {column.name}: {column.type}")