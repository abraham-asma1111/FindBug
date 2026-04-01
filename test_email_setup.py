#!/usr/bin/env python3
"""
Test Email Configuration
Run this after setting up Gmail App Password
"""
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection():
    """Test SMTP connection with current configuration"""
    print("🧪 Testing Email Configuration")
    print("=" * 50)
    
    # Load environment variables
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_from = os.getenv('SMTP_FROM', 'noreply@findbugplatform.com')
    
    print(f"📧 SMTP Host: {smtp_host}")
    print(f"🔌 SMTP Port: {smtp_port}")
    print(f"👤 SMTP User: {smtp_user}")
    print(f"🔑 SMTP Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    print(f"📤 From Address: {smtp_from}")
    
    # Check if credentials are configured
    if not smtp_user or not smtp_password:
        print("\n❌ SMTP credentials not configured!")
        print("\n🔧 To fix this:")
        print("1. Edit backend/.env file")
        print("2. Set SMTP_USER=your-email@gmail.com")
        print("3. Set SMTP_PASSWORD=your-16-char-app-password")
        return False
    
    if smtp_user == "YOUR_EMAIL@gmail.com" or smtp_password == "YOUR_16_CHAR_APP_PASSWORD":
        print("\n❌ Please update the placeholder values in backend/.env")
        print("   SMTP_USER and SMTP_PASSWORD still have default values")
        return False
    
    # Test SMTP connection
    print(f"\n🔗 Testing SMTP connection to {smtp_host}:{smtp_port}...")
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print("✅ Connected to SMTP server")
            
            server.starttls()
            print("✅ TLS encryption enabled")
            
            server.login(smtp_user, smtp_password)
            print("✅ Authentication successful")
            
        print("\n🎉 Email configuration is working!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\n🔧 Possible fixes:")
        print("1. Check if 2-Factor Authentication is enabled on Gmail")
        print("2. Generate a new App Password from Google Account settings")
        print("3. Make sure you're using the App Password, not your regular password")
        print("4. Remove any spaces from the App Password")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False

def send_test_email():
    """Send a test email"""
    smtp_user = os.getenv('SMTP_USER')
    
    if not smtp_user or smtp_user == "YOUR_EMAIL@gmail.com":
        print("❌ Cannot send test email - SMTP_USER not configured")
        return False
    
    print(f"\n📧 Sending test email to {smtp_user}...")
    
    try:
        # Import the email service
        sys.path.append('backend/src')
        from core.email_service import EmailService
        
        # Send test OTP email
        success = EmailService.send_registration_verification_email(
            email=smtp_user,
            otp="123456",
            token="test-token-123",
            user_type="researcher"
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"   Check your inbox: {smtp_user}")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Email Setup Test")
    print("=" * 60)
    
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv('backend/.env')
        print("✅ Loaded backend/.env file")
    except ImportError:
        print("⚠️  python-dotenv not installed, loading from environment")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")
    
    # Test SMTP connection
    if test_smtp_connection():
        # If connection works, send test email
        send_test_email()
    
    print("\n" + "=" * 60)
    print("📋 Email Setup Instructions:")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification")
    print("3. Generate App Password for 'Mail'")
    print("4. Update backend/.env with your Gmail and App Password")
    print("5. Run this test again: python test_email_setup.py")

if __name__ == "__main__":
    main()