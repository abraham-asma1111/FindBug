#!/usr/bin/env python3
"""
Script to refactor all phone/SMS references to email in the codebase.
This script updates method names, variable names, and field references.
"""

import re
from pathlib import Path

# Define replacement mappings
REPLACEMENTS = {
    # Method names
    'send_phone_verification': 'send_email_verification',
    'verify_phone_code': 'verify_email_code',
    'get_phone_verification_status': 'get_email_verification_status',
    
    # Field names (with kyc. prefix)
    'kyc.phone_number': 'kyc.email_address',
    'kyc.phone_verified': 'kyc.email_verified',
    'kyc.phone_verification_code': 'kyc.email_verification_code',
    'kyc.phone_verification_code_expires': 'kyc.email_verification_code_expires',
    'kyc.phone_verification_attempts': 'kyc.email_verification_attempts',
    'kyc.phone_verified_at': 'kyc.email_verified_at',
    
    # API parameter names (keep for backward compatibility in some places)
    '"phone_number"': '"email_address"',
    "'phone_number'": "'email_address'",
    'phone_number=': 'email_address=',
    
    # Response field names
    '"phone_verified"': '"email_verified"',
    "'phone_verified'": "'email_verified'",
    '"phone_verified_at"': '"email_verified_at"',
    "'phone_verified_at'": "'email_verified_at'",
    '"can_verify_phone"': '"can_verify_email"',
    "'can_verify_phone'": "'can_verify_email'",
    
    # Comments and strings
    'Phone number': 'Email address',
    'phone number': 'email address',
    'Phone verified': 'Email verified',
    'phone verified': 'email verified',
    'SMS verification': 'Email verification',
    'SMS Verification': 'Email Verification',
}

def refactor_file(file_path: Path):
    """Refactor a single file."""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Apply replacements
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated {file_path}")
        return True
    else:
        print(f"  ⏭️  No changes needed")
        return False

def main():
    """Main refactoring function."""
    backend_root = Path(__file__).parent
    
    # Files to refactor
    files_to_refactor = [
        backend_root / 'src' / 'services' / 'kyc_service.py',
        backend_root / 'src' / 'api' / 'v1' / 'endpoints' / 'kyc.py',
    ]
    
    updated_count = 0
    for file_path in files_to_refactor:
        if file_path.exists():
            if refactor_file(file_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Refactoring complete! Updated {updated_count} files.")

if __name__ == '__main__':
    main()
