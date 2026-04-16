#!/usr/bin/env python3
"""
Complete test of the researcher endpoint
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.researcher import Researcher
from src.domain.models.user import User
from src.domain.models.matching import ResearcherProfile

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_query():
    print("\n" + "="*60)
    print("  TESTING RESEARCHER QUERY")
    print("="*60 + "\n")
    
    db = SessionLocal()
    try:
        # Query exactly like the endpoint does
        from sqlalchemy import func, or_
        
        query = db.query(Researcher).join(
            User,
            Researcher.user_id == User.id
        ).outerjoin(
            ResearcherProfile,
            Researcher.id == ResearcherProfile.researcher_id
        ).filter(
            Researcher.is_active == True
        )
        
        researchers = query.limit(100).all()
        
        print(f"✅ Found {len(researchers)} active researchers\n")
        
        if researchers:
            print("First 3 researchers:")
            for idx, researcher in enumerate(researchers[:3], 1):
                print(f"\n{idx}. Researcher ID: {researcher.id}")
                print(f"   User Email: {researcher.user.email}")
                print(f"   Username (derived): {researcher.user.email.split('@')[0]}")
                print(f"   Reputation: {researcher.reputation_score}")
                print(f"   Total Reports: {researcher.total_reports}")
                print(f"   Verified Reports: {researcher.verified_reports}")
                print(f"   Active: {researcher.is_active}")
                print(f"   Bio: {researcher.bio or 'None'}")
                
                # Check profile
                if hasattr(researcher, 'profile') and researcher.profile:
                    profile = researcher.profile
                    print(f"   Has Profile: Yes")
                    print(f"   Profile Experience: {profile.experience_years if hasattr(profile, 'experience_years') else 'N/A'}")
                    print(f"   Profile Skills: {profile.skills if hasattr(profile, 'skills') else []}")
                else:
                    print(f"   Has Profile: No")
        
        # Format like the endpoint does
        print("\n" + "-"*60)
        print("FORMATTED OUTPUT (like API response):")
        print("-"*60 + "\n")
        
        result = []
        for researcher in researchers[:3]:
            profile_data = None
            if hasattr(researcher, 'profile') and researcher.profile:
                profile = researcher.profile
                profile_data = {
                    'experience_years': profile.experience_years if hasattr(profile, 'experience_years') else 0,
                    'skills': profile.skills if hasattr(profile, 'skills') and profile.skills else [],
                    'specializations': profile.specializations if hasattr(profile, 'specializations') and profile.specializations else [],
                    'bio': researcher.bio
                }
            else:
                profile_data = {
                    'experience_years': 0,
                    'skills': [],
                    'specializations': [],
                    'bio': researcher.bio
                }
            
            result.append({
                'id': str(researcher.id),
                'user': {
                    'username': researcher.user.email.split('@')[0],
                    'email': researcher.user.email
                },
                'reputation_score': float(researcher.reputation_score),
                'total_reports': researcher.total_reports,
                'verified_reports': researcher.verified_reports,
                'profile': profile_data
            })
        
        import json
        print(json.dumps(result, indent=2))
        
        print("\n" + "="*60)
        print(f"  SUCCESS! Query returns {len(researchers)} researchers")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
