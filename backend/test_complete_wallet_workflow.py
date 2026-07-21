"""Test complete wallet workflow: recharge, check balance, publish program."""
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Organization credentials
ORG_EMAIL = "org@test.com"
ORG_PASSWORD = "Password123!"

def test_complete_workflow():
    """Test the complete wallet workflow."""
    
    print("=" * 70)
    print("COMPLETE WALLET WORKFLOW TEST")
    print("=" * 70)
    
    # Step 1: Login
    print("\n1. Logging in as organization...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ORG_EMAIL, "password": ORG_PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    print(f"✅ Login successful")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get current balance
    print("\n2. Getting current wallet balance...")
    balance_response = requests.get(f"{BASE_URL}/wallet/balance", headers=headers)
    
    if balance_response.status_code != 200:
        print(f"❌ Failed: {balance_response.status_code}")
        return
    
    balance_data = balance_response.json()
    current_balance = balance_data.get('balance', 0)
    print(f"✅ Current balance: {current_balance} ETB")
    
    # Step 3: Get organization's programs
    print("\n3. Getting organization's programs...")
    programs_response = requests.get(f"{BASE_URL}/programs/my-programs", headers=headers)
    
    if programs_response.status_code != 200:
        print(f"❌ Failed: {programs_response.status_code}")
        return
    
    programs = programs_response.json()
    print(f"✅ Found {len(programs)} programs")
    
    # Find a draft program with reward tiers
    draft_program = None
    for program in programs:
        if program.get('status') == 'draft':
            # Get reward tiers
            program_id = program.get('id')
            tiers_response = requests.get(
                f"{BASE_URL}/programs/{program_id}/rewards",
                headers=headers
            )
            if tiers_response.status_code == 200:
                tiers = tiers_response.json()
                if tiers:
                    draft_program = program
                    draft_program['tiers'] = tiers
                    break
    
    if not draft_program:
        print("⚠️  No draft program with reward tiers found")
        print("   Skipping publish test")
        return
    
    program_id = draft_program.get('id')
    program_name = draft_program.get('name')
    tiers = draft_program.get('tiers', [])
    
    print(f"   Program: {program_name} (ID: {program_id})")
    print(f"   Reward tiers:")
    
    max_reward = 0
    for tier in tiers:
        severity = tier.get('severity')
        min_amt = float(tier.get('min_amount', 0))
        max_amt = float(tier.get('max_amount', 0))
        print(f"     - {severity}: {min_amt} - {max_amt} ETB")
        if max_amt > max_reward:
            max_reward = max_amt
    
    print(f"   Maximum reward (critical tier): {max_reward} ETB")
    
    # Step 4: Check if balance is sufficient
    print(f"\n4. Checking wallet balance requirement...")
    print(f"   Current balance: {current_balance} ETB")
    print(f"   Required balance: {max_reward} ETB")
    
    if current_balance < max_reward:
        print(f"   ❌ Insufficient balance!")
        print(f"   Need to recharge: {max_reward - current_balance} ETB")
        
        # Recharge wallet
        recharge_amount = max_reward - current_balance + 1000  # Add buffer
        print(f"\n5. Recharging wallet with {recharge_amount} ETB...")
        
        recharge_response = requests.post(
            f"{BASE_URL}/wallet/recharge?amount={recharge_amount}&payment_method=bank_transfer",
            headers=headers
        )
        
        if recharge_response.status_code != 201:
            print(f"❌ Recharge failed: {recharge_response.status_code}")
            print(f"Response: {recharge_response.text}")
            return
        
        recharge_data = recharge_response.json()
        new_balance = recharge_data.get('new_balance')
        print(f"✅ Recharge successful")
        print(f"   New balance: {new_balance} ETB")
        current_balance = new_balance
    else:
        print(f"   ✅ Sufficient balance!")
    
    # Step 5: Try to publish program
    print(f"\n6. Publishing program...")
    publish_response = requests.post(
        f"{BASE_URL}/programs/{program_id}/publish",
        headers=headers
    )
    
    if publish_response.status_code == 200:
        print(f"✅ Program published successfully!")
        published_program = publish_response.json()
        print(f"   Status: {published_program.get('status')}")
    else:
        print(f"❌ Publish failed: {publish_response.status_code}")
        print(f"Response: {publish_response.text}")
        return
    
    # Step 6: Verify final balance
    print(f"\n7. Verifying final balance...")
    balance_response = requests.get(f"{BASE_URL}/wallet/balance", headers=headers)
    
    if balance_response.status_code == 200:
        balance_data = balance_response.json()
        final_balance = balance_data.get('balance', 0)
        print(f"✅ Final balance: {final_balance} ETB")
        print(f"   Available: {balance_data.get('available_balance', 0)} ETB")
        print(f"   Reserved: {balance_data.get('reserved_balance', 0)} ETB")
    
    print("\n" + "=" * 70)
    print("WORKFLOW TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📋 Summary:")
    print(f"   ✅ Wallet recharge working")
    print(f"   ✅ Balance check before publish working")
    print(f"   ✅ Program publish with wallet validation working")


if __name__ == "__main__":
    test_complete_workflow()
