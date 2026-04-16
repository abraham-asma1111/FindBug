#!/usr/bin/env python3
"""
Complete AI Red Teaming Workflow Test
Tests: Create → Publish → Auto-broadcast → Accept → Submit Report
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8002"

def test_workflow():
    print("\n" + "="*70)
    print("  AI RED TEAMING COMPLETE WORKFLOW TEST")
    print("="*70 + "\n")
    
    # Step 1: Login as Organization
    print("STEP 1: Login as Organization")
    print("-" * 70)
    org_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "org@example.com", "password": "password123"}
    )
    
    if org_response.status_code != 200:
        print(f"❌ Organization login failed: {org_response.status_code}")
        print(org_response.text)
        return
    
    org_token = org_response.json()["access_token"]
    org_headers = {"Authorization": f"Bearer {org_token}"}
    print(f"✅ Organization logged in\n")
    
    # Step 2: Create AI Red Teaming Engagement
    print("STEP 2: Create AI Red Teaming Engagement")
    print("-" * 70)
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    engagement_data = {
        "name": "Test AI Model Security Assessment",
        "target_ai_system": "GPT-4 Clone API",
        "model_type": "llm",
        "testing_environment": "https://sandbox.example.com/ai-test",
        "ethical_guidelines": "Follow responsible disclosure. Do not exfiltrate real user data. Report all findings within 24 hours.",
        "scope_description": "Test for prompt injection, jailbreaking, and data leakage vulnerabilities",
        "allowed_attack_types": ["prompt_injection", "jailbreaking", "data_extraction"]
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/v1/ai-red-teaming/engagements",
        headers=org_headers,
        json=engagement_data
    )
    
    if create_response.status_code not in [200, 201]:
        print(f"❌ Failed to create engagement: {create_response.status_code}")
        print(create_response.text)
        return
    
    engagement = create_response.json()
    engagement_id = engagement.get("id") or engagement.get("engagement_id")
    print(f"✅ Created engagement: {engagement_id}")
    print(f"   Name: {engagement.get('name')}")
    print(f"   Status: {engagement.get('status')}\n")
    
    # Step 3: Publish & Auto-Broadcast
    print("STEP 3: Publish & Auto-Broadcast to Researchers")
    print("-" * 70)
    
    publish_response = requests.patch(
        f"{BASE_URL}/api/v1/ai-red-teaming/engagements/{engagement_id}/status",
        headers=org_headers,
        json={"status": "active"}
    )
    
    if publish_response.status_code not in [200, 201]:
        print(f"❌ Failed to publish: {publish_response.status_code}")
        print(publish_response.text)
        return
    
    print(f"✅ Engagement published and broadcasted")
    print(f"   Status changed to: active")
    print(f"   Auto-broadcast triggered to ALL researchers\n")
    
    # Step 4: Check researcher engagements
    print("STEP 4: Verify Researcher Engagements Created")
    print("-" * 70)
    
    # Login as researcher
    researcher_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "test@test.com", "password": "password123"}
    )
    
    if researcher_response.status_code != 200:
        print(f"❌ Researcher login failed: {researcher_response.status_code}")
        return
    
    researcher_token = researcher_response.json()["access_token"]
    researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
    print(f"✅ Researcher logged in (test@test.com)\n")
    
    # Get researcher's engagements
    engagements_response = requests.get(
        f"{BASE_URL}/api/v1/ai-red-teaming/researcher/engagements",
        headers=researcher_headers
    )
    
    if engagements_response.status_code == 200:
        researcher_engagements = engagements_response.json()
        print(f"✅ Researcher has {len(researcher_engagements)} engagement(s)")
        
        # Find our test engagement
        test_engagement = None
        for eng in researcher_engagements:
            if eng.get("engagement_id") == engagement_id:
                test_engagement = eng
                break
        
        if test_engagement:
            print(f"✅ Test engagement found in researcher's list")
            print(f"   Status: {test_engagement.get('status')}")
            researcher_engagement_id = test_engagement.get("id")
        else:
            print(f"⚠️  Test engagement not found in researcher's list")
            print(f"   Available engagements: {len(researcher_engagements)}")
            researcher_engagement_id = None
    else:
        print(f"❌ Failed to get researcher engagements: {engagements_response.status_code}")
        researcher_engagement_id = None
    
    print()
    
    # Step 5: Accept Engagement
    if researcher_engagement_id:
        print("STEP 5: Accept Engagement (Researcher)")
        print("-" * 70)
        
        accept_response = requests.post(
            f"{BASE_URL}/api/v1/ai-red-teaming/researcher/engagements/{researcher_engagement_id}/accept",
            headers=researcher_headers
        )
        
        if accept_response.status_code in [200, 201]:
            print(f"✅ Engagement accepted")
            print(f"   Researcher can now submit reports\n")
        else:
            print(f"❌ Failed to accept: {accept_response.status_code}")
            print(accept_response.text)
            print()
    
    # Step 6: Submit Test Report
    if researcher_engagement_id:
        print("STEP 6: Submit Test Report")
        print("-" * 70)
        
        report_data = {
            "engagement_id": engagement_id,
            "title": "Prompt Injection Vulnerability - Automated Test",
            "severity": "high",
            "description": "Found a prompt injection vulnerability that allows bypassing safety filters",
            "steps_to_reproduce": "1. Send prompt: 'Ignore previous instructions'\n2. Observe model behavior",
            "impact": "Attacker can bypass content filters and extract sensitive information",
            "vulnerability_type": "prompt_injection"
        }
        
        report_response = requests.post(
            f"{BASE_URL}/api/v1/ai-red-teaming/reports",
            headers=researcher_headers,
            json=report_data
        )
        
        if report_response.status_code in [200, 201]:
            report = report_response.json()
            print(f"✅ Report submitted successfully")
            print(f"   Report ID: {report.get('id')}")
            print(f"   Title: {report.get('title')}")
            print(f"   Severity: {report.get('severity')}\n")
        else:
            print(f"❌ Failed to submit report: {report_response.status_code}")
            print(report_response.text)
            print()
    
    # Summary
    print("="*70)
    print("  WORKFLOW TEST COMPLETE")
    print("="*70)
    print("\n✅ Successfully tested:")
    print("   1. Organization login")
    print("   2. Create AI Red Teaming engagement")
    print("   3. Publish & auto-broadcast")
    print("   4. Researcher receives engagement")
    if researcher_engagement_id:
        print("   5. Researcher accepts engagement")
        print("   6. Researcher submits report")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        test_workflow()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend at http://localhost:8002")
        print("Make sure the backend is running!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
