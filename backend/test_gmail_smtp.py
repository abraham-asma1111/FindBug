#!/usr/bin/env python3
"""
Test Gmail SMTP Connection
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail SMTP Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "abrahamasmamaw44@gmail.com"
SMTP_PASSWORD = "wzmcxfhomzmicthc"  # Your App Password
TEST_EMAIL = "abrahambecon@gmail.com"

print("=" * 60)
print("Gmail SMTP Connection Test")
print("=" * 60)
print(f"SMTP Host: {SMTP_HOST}")
print(f"SMTP Port: {SMTP_PORT}")
print(f"SMTP User: {SMTP_USER}")
print(f"Password Length: {len(SMTP_PASSWORD)} characters")
print(f"Test Email: {TEST_EMAIL}")
print("=" * 60)

try:
    print("\n1. Connecting to Gmail SMTP server...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    print("   ✅ Connected successfully")
    
    print("\n2. Starting TLS encryption...")
    server.starttls()
    print("   ✅ TLS started successfully")
    
    print("\n3. Attempting login...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("   ✅ Login successful!")
    
    print("\n4. Sending test email...")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Test Email from FindBug Platform'
    msg['From'] = SMTP_USER
    msg['To'] = TEST_EMAIL
    
    text_body = "This is a test email to verify Gmail SMTP configuration."
    html_body = """
    <html>
      <body>
        <h2>Test Email</h2>
        <p>This is a test email to verify Gmail SMTP configuration.</p>
        <p>If you received this, your Gmail SMTP is working correctly!</p>
      </body>
    </html>
    """
    
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    server.send_message(msg)
    print("   ✅ Test email sent successfully!")
    
    server.quit()
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Gmail SMTP is working!")
    print("=" * 60)
    print(f"\nCheck your inbox at {TEST_EMAIL}")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION FAILED: {e}")
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING STEPS:")
    print("=" * 60)
    print("1. Verify your Gmail App Password is correct")
    print("   - Go to: https://myaccount.google.com/apppasswords")
    print("   - Generate a NEW App Password")
    print("   - Copy it WITHOUT spaces (16 characters)")
    print("")
    print("2. Make sure 2-Step Verification is enabled")
    print("   - Go to: https://myaccount.google.com/security")
    print("   - Enable 2-Step Verification if not already enabled")
    print("")
    print("3. Current password in .env file:")
    print(f"   SMTP_PASSWORD={SMTP_PASSWORD}")
    print(f"   Length: {len(SMTP_PASSWORD)} characters (should be 16)")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull error details:")
    import traceback
    traceback.print_exc()
