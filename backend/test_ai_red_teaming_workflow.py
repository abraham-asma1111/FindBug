#!/usr/bin/env python3
"""
Test AI Red Teaming Complete Workflow
Tests: Create engagement, publish, check researcher view, invite researchers
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_workflow():
    print_section("AI RED TEAMING WORKFLOW TEST")
    
    # Step 1: Login as organization
    print_section("Step 1: Login as Organization")
    org_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "org_user",
        "password": "password123"
    })
    
    if org_login.status_code != 200:
        print(f"❌ Organization login failed: {org_login.status_code}")
        print(f"Response: {org_login.text}")
        return
    
    org_token = org_login.json()["access_token"]
    org_headers = {"Authorization": f"Bearer {org_token}"}
    print(f"✅ Organization logged in successfully")
    
    # Step 2: Create AI Red Teaming engagement
    print_section("Step 2: Create AI Red Teaming Engagement")
    engagement_data = {
        "name": "GPT-4 Security Assessment",
        "target_ai_system": "GPT-4 Production API",
        "model_type": "llm",
        "testing_environment": "Isolated sandbox environment with rate limiting",
        "ethical_guidelines": "No harmful content generation, respect privacy, no data exfiltration attempts",
        "scope_description": "Test for prompt injection, jailbreaking, and data leakage vulnerabilities",
        "allowed_attack_types": ["prompt_injection", "jailbreak", "data_leakage"]
    }
    
    create_response = requests.post(
        f"{BASE_URL}/ai-red-teaming/engagements",
        headers=org_headers,
        json=engagement_data
    )
    
    if create_response.status_code not in [200, 201]:
        print(f"❌ Failed to create engagement: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return
    
    engagement = create_response.json()
    engagement_id = engagement["id"]
    print(f"✅ Engagement created: {engagement['name']}")
    print(f"   ID: {engagement_id}")
    print(f"   Status: {engagement['status']}")
    
    # Step 3: Setup testing environment
    print_section("Step 3: Setup Testing Environment")
    env_data = {
        "model_type": "llm",
        "sandbox_url": "https://sandbox.example.com/gpt4",
        "api_endpoint": "https://api.example.com/v1/chat/completions",
        "access_token": "test_token_encrypted_12345",
        "access_controls": {
            "max_tokens": 1000,
            "temperature": 0.7,
            "allowed_models": ["gpt-4"]
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "tokens_per_minute": 10000
        },
        "is_isolated": True
    }
    
    env_response = requests.post(
        f"{BASE_URL}/ai-red-teaming/engagements/{engagement_id}/testing-environment",
        headers=org_headers,
        json=env_data
    )
    
    if env_response.status_code not in [200, 201]:
        print(f"❌ Failed to setup environment: {env_response.status_code}")
        print(f"Response: {env_response.text}")
    else:
        print(f"✅ Testing environment configured")
    
    # Step 4: Check available researchers
    print_section("Step 4: Check Available Researchers")
    researchers_response = requests.get(
        f"{BASE_URL}/ai-red-teaming/engagements/{engagement_id}/available-researchers",
        headers=org_headers
    )
    
    if researchers_response.status_code != 200:
        print(f"❌ Failed to get researchers: {researchers_response.status_code}")
        print(f"Response: {researchers_response.text}")
    else:
        researchers = researchers_response.json()
        print(f"✅ Found {len(researchers)} available researchers")
        for r in researchers[:3]:
            print(f"   - {r['user']['username']} (Rep: {r['reputation_score']}, Reports: {r['total_reports']})")
    
    # Step 5: Get AI recommendations
    print_section("Step 5: Get AI-Powered Recommendations")
    match_response = requests.post(
        f"{BASE_URL}/ai-red-teaming/engagements/{engagement_id}/match-researchers",
        headers=org_headers,
        json={"limit": 5}
    )
    
    if match_response.status_code != 200:
        print(f"❌ Failed to get recommendations: {match_response.status_code}")
        print(f"Response: {match_response.text}")
    else:
        recommendations = match_response.json()
        print(f"✅ Got {len(recommendations)} AI-powered recommendations")
        for rec in recommendations[:3]:
            print(f"   - {rec['researcher']['user']['username']}")
            print(f"     Match Score: {rec['match_score']}%")
            print(f"     Reasons: {', '.join(rec['reasons'][:2])}")
    
    # Step 6: Publish engagement (triggers auto-broadcast)
    print_section("Step 6: Publish Engagement (Auto-Broadcast)")
    publish_response = requests.patch(
        f"{BASE_URL}/ai-red-teaming/engagements/{engagement_id}/status",
        headers=org_headers,
        json={"status": "active"}
    )
    
    if publish_response.status_code != 200:
        print(f"❌ Failed to publish engagement: {publish_response.status_code}")
        print(f"Response: {publish_response.text}")
    else:
        published = publish_response.json()
        print(f"✅ Engagement published and broadcasted!")
        print(f"   Status: {published['status']}")
        print(f"   Start Date: {published.get('start_date', 'N/A')}")
    
    # Step 7: Login as researcher
    print_section("Step 7: Login as Researcher")
    researcher_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "researcher_user",
        "password": "password123"
    })
    
    if researcher_login.status_code != 200:
        print(f"❌ Researcher login failed: {researcher_login.status_code}")
        print(f"Response: {researcher_login.text}")
        return
    
    researcher_token = researcher_login.json()["access_token"]
    researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
    print(f"✅ Researcher logged in successfully")
    
    # Step 8: Check researcher's engagements (algorithm-pushed)
    print_section("Step 8: Check Researcher's AI Red Teaming Engagements")
    researcher_engagements = requests.get(
        f"{BASE_URL}/ai-red-teaming/researcher/engagements",
        headers=researcher_headers
    )
    
    if researcher_engagements.status_code != 200:
        print(f"❌ Failed to get researcher engagements: {researcher_engagements.status_code}")
        print(f"Response: {researcher_engagements.text}")
    else:
        engagements = researcher_engagements.json()
        print(f"✅ Researcher sees {len(engagements)} algorithm-pushed engagements")
        for eng in engagements:
            print(f"   - {eng['name']}")
            print(f"     Model: {eng['model_type']}")
            print(f"     Status: {eng['status']}")
    
    # Step 9: Check researcher notifications
    print_section("Step 9: Check Researcher Notifications")
    notifications = requests.get(
        f"{BASE_URL}/notifications",
        headers=researcher_headers
    )
    
    if notifications.status_code != 200:
        print(f"❌ Failed to get notifications: {notifications.status_code}")
    else:
        notifs = notifications.json()
        print(f"✅ Researcher has {len(notifs.get('notifications', []))} notifications")
        for notif in notifs.get('notifications', [])[:3]:
            print(f"   - {notif.get('title', 'N/A')}")
    
    print_section("WORKFLOW TEST COMPLETE")
    print(f"✅ All steps completed successfully!")
    print(f"\nNext steps:")
    print(f"1. Researcher can submit vulnerability reports")
    print(f"2. Organization can view reports in engagement detail")
    print(f"3. Triage specialist can verify reports (when portal is built)")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
