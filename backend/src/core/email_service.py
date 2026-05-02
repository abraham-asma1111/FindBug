"""
Email Service - Email verification and notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from datetime import datetime, timedelta
import secrets
import hashlib
import re


class EmailService:
    """Email service for verification and notifications"""
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate secure verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    @staticmethod
    def send_email_verification_link(email: str, token: str, user_type: str) -> bool:
        """
        Send email verification link (no OTP, just click to verify)
        
        Args:
            email: User email address
            token: Verification token for the link
            user_type: 'researcher' or 'organization'
        """
        try:
            # Email configuration from environment
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from = os.getenv('SMTP_FROM', 'noreply@findbugplatform.com')
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP credentials not configured. Email not sent.")
                return False
            
            # Create verification link
            base_url = os.getenv('FRONTEND_URL', 'http://localhost:3002')
            verification_link = f"{base_url}/verify-email?token={token}&type={user_type}"
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify Your FindBug Account - Complete Registration'
            msg['From'] = smtp_from
            msg['To'] = email
            
            # Email body
            text_body = f"""
            Welcome to FindBug Platform!
            
            Complete your {user_type} registration by clicking the verification link below:
            
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            FindBug Platform Team
            Bahir Dar University
            """
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: #7C3AED; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔒 Verify Your Email</h1>
                  </div>
                  
                  <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
                    <h2 style="color: #7C3AED; margin-top: 0;">Welcome to FindBug!</h2>
                    <p>Thank you for registering as a <strong>{user_type}</strong>.</p>
                    <p>Click the button below to verify your email and complete your registration:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                      <a href="{verification_link}" 
                         style="background-color: #7C3AED; color: white; padding: 15px 30px; 
                                text-decoration: none; border-radius: 8px; display: inline-block; 
                                font-weight: bold; font-size: 16px;">
                        ✅ Verify Email Address
                      </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; text-align: center;">
                      This link expires in 24 hours
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <div style="background: #f1f3f4; padding: 15px; border-radius: 5px;">
                      <p style="margin: 0; color: #666; font-size: 14px;">
                        <strong>Can't click the button?</strong> Copy and paste this link in your browser:<br>
                        <a href="{verification_link}" style="color: #7C3AED; word-break: break-all;">{verification_link}</a>
                      </p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                      If you didn't create this account, please ignore this email.
                    </p>
                  </div>
                  
                  <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
                    <p style="margin: 0;">FindBug Platform - Bug Bounty & Security Research</p>
                    <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email verification link sent to {email}")
            print(f"   Link: {verification_link}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send verification email: {e}")
            return False
    
    @staticmethod
    def send_registration_otp_email(email: str, otp: str, first_name: str = "User") -> bool:
        """
        Send registration OTP email
        
        Args:
            email: User email address
            otp: 6-digit OTP code
            first_name: User's first name
        """
        try:
            # Email configuration from environment
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from = os.getenv('SMTP_FROM', 'noreply@findbugplatform.com')
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP credentials not configured. Email not sent.")
                return False
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify Your FindBug Account - Registration Code'
            msg['From'] = smtp_from
            msg['To'] = email
            
            # Email body
            text_body = f"""
            Welcome to FindBug Platform, {first_name}!
            
            Complete your registration by entering this verification code:
            
            VERIFICATION CODE: {otp}
            
            This code will expire in 10 minutes.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            FindBug Platform Team
            Bahir Dar University
            """
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: #7C3AED; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔒 Complete Your Registration</h1>
                  </div>
                  
                  <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
                    <h2 style="color: #7C3AED; margin-top: 0;">Welcome, {first_name}!</h2>
                    <p>Thank you for registering with FindBug Platform.</p>
                    <p>Complete your registration by entering this verification code:</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; border: 2px solid #7C3AED;">
                      <h1 style="color: #7C3AED; font-size: 36px; margin: 0; letter-spacing: 8px; font-family: monospace;">{otp}</h1>
                      <p style="color: #666; margin: 10px 0 0; font-size: 14px;">Enter this code to verify your email</p>
                    </div>
                    
                    <p style="color: #e74c3c; font-size: 14px; text-align: center;">
                      ⏰ This code expires in 10 minutes
                    </p>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                      If you didn't create this account, please ignore this email.
                    </p>
                  </div>
                  
                  <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
                    <p style="margin: 0;">FindBug Platform - Bug Bounty & Security Research</p>
                    <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ Registration OTP sent to {email}")
            print(f"   OTP: {otp} (expires in 10 minutes)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send registration OTP: {e}")
            return False
    
    @staticmethod
    def send_registration_verification_email(email: str, otp: str, token: str, user_type: str) -> bool:
        """
        Send registration verification email with OTP and backup link
        
        Args:
            email: User email address
            otp: 6-digit OTP code
            token: Backup verification token
            user_type: 'researcher' or 'organization'
        """
        try:
            # Email configuration from environment
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from = os.getenv('SMTP_FROM', 'noreply@findbugplatform.com')
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP credentials not configured. Email not sent.")
                return False
            
            # Create verification link (backup method)
            base_url = os.getenv('FRONTEND_URL', 'http://localhost:3002')
            verification_link = f"{base_url}/verify-email?token={token}&type={user_type}"
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify Your FindBug Account - Complete Registration'
            msg['From'] = smtp_from
            msg['To'] = email
            
            # Email body
            text_body = f"""
            Welcome to FindBug Platform!
            
            Complete your {user_type} registration by entering this verification code:
            
            VERIFICATION CODE: {otp}
            
            This code will expire in 10 minutes.
            
            Alternatively, you can click this link to verify:
            {verification_link}
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            FindBug Platform Team
            Bahir Dar University
            """
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: #7C3AED; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔒 Complete Your Registration</h1>
                  </div>
                  
                  <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
                    <h2 style="color: #7C3AED; margin-top: 0;">Welcome to FindBug!</h2>
                    <p>Thank you for registering as a <strong>{user_type}</strong>.</p>
                    <p>Complete your registration by entering this verification code:</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; border: 2px solid #7C3AED;">
                      <h1 style="color: #7C3AED; font-size: 36px; margin: 0; letter-spacing: 8px; font-family: monospace;">{otp}</h1>
                      <p style="color: #666; margin: 10px 0 0; font-size: 14px;">Enter this code to verify your email</p>
                    </div>
                    
                    <p style="color: #e74c3c; font-size: 14px; text-align: center;">
                      ⏰ This code expires in 10 minutes
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <div style="background: #f1f3f4; padding: 15px; border-radius: 5px;">
                      <p style="margin: 0; color: #666; font-size: 14px;">
                        <strong>Alternative method:</strong> If you can't enter the code, 
                        <a href="{verification_link}" style="color: #7C3AED;">click here to verify</a>
                      </p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                      If you didn't create this account, please ignore this email.
                    </p>
                  </div>
                  
                  <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
                    <p style="margin: 0;">FindBug Platform - Bug Bounty & Security Research</p>
                    <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ Registration verification email sent to {email}")
            print(f"   OTP: {otp} (expires in 10 minutes)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send registration email: {e}")
            return False
        """
        Send email verification link
        
        Args:
            email: User email address
            token: Verification token
            user_type: 'researcher' or 'organization'
        """
        try:
            # Email configuration from environment
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from = os.getenv('SMTP_FROM', 'noreply@bugbounty.com')
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP credentials not configured. Email not sent.")
                return False
            
            # Create verification link
            base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            verification_link = f"{base_url}/verify-email?token={token}&type={user_type}"
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify Your Bug Bounty Platform Account'
            msg['From'] = smtp_from
            msg['To'] = email
            
            # Email body
            text_body = f"""
            Welcome to Bug Bounty Platform!
            
            Please verify your email address by clicking the link below:
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            Bug Bounty Platform Team
            """
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #2563eb;">Welcome to Bug Bounty Platform!</h2>
                  <p>Thank you for registering as a {user_type}.</p>
                  <p>Please verify your email address by clicking the button below:</p>
                  <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" 
                       style="background-color: #2563eb; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                      Verify Email Address
                    </a>
                  </div>
                  <p style="color: #666; font-size: 14px;">
                    This link will expire in 24 hours.
                  </p>
                  <p style="color: #666; font-size: 14px;">
                    If you didn't create this account, please ignore this email.
                  </p>
                  <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                  <p style="color: #999; font-size: 12px;">
                    Bug Bounty Platform Team<br>
                    Bahir Dar University
                  </p>
                </div>
              </body>
            </html>
            """
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ Verification email sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_mfa_code(email: str, code: str) -> bool:
        """Send MFA code via email"""
        try:
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from = os.getenv('SMTP_FROM', 'noreply@bugbounty.com')
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP credentials not configured. Email not sent.")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your Bug Bounty Platform Verification Code'
            msg['From'] = smtp_from
            msg['To'] = email
            
            text_body = f"""
            Your verification code is: {code}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            """
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #2563eb;">Your Verification Code</h2>
                  <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <h1 style="color: #2563eb; font-size: 36px; margin: 0; letter-spacing: 5px;">{code}</h1>
                  </div>
                  <p style="color: #666; font-size: 14px;">
                    This code will expire in 10 minutes.
                  </p>
                  <p style="color: #666; font-size: 14px;">
                    If you didn't request this code, please ignore this email.
                  </p>
                </div>
              </body>
            </html>
            """
            
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ MFA code sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send MFA code: {e}")
            return False
    
    @staticmethod
    def send_kyc_verification_code(email: str, code: str, user_name: str = "User") -> bool:
        """
        Send KYC verification code via email (replaces SMS)
        
        Args:
            email: User email address
            code: 6-digit verification code
            user_name: User's first name for personalization
            
        Returns:
            True if sent successfully
        """
        try:
            # Check if mock mode is enabled
            smtp_mock_mode = os.getenv('SMTP_MOCK_MODE', 'false').lower() == 'true'
            
            if smtp_mock_mode:
                print(f"\n{'='*60}")
                print(f"📧 MOCK MODE: KYC VERIFICATION EMAIL")
                print(f"{'='*60}")
                print(f"To: {email}")
                print(f"User: {user_name}")
                print(f"Subject: Your KYC Verification Code - FindBug Platform")
                print(f"\n🔐 VERIFICATION CODE: {code}")
                print(f"\nThis code expires in 10 minutes.")
                print(f"{'='*60}\n")
                return True
            
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from = os.getenv('SMTP_FROM', 'noreply@findbugplatform.com')
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP credentials not configured. Email not sent.")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your KYC Verification Code - FindBug Platform'
            msg['From'] = smtp_from
            msg['To'] = email
            
            text_body = f"""
            Hi {user_name},
            
            Your KYC verification code is: {code}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            FindBug Platform Team
            Bahir Dar University
            """
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: #7C3AED; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔐 KYC Verification Code</h1>
                  </div>
                  
                  <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
                    <h2 style="color: #7C3AED; margin-top: 0;">Hi {user_name},</h2>
                    <p>Complete your KYC verification by entering this code:</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; border: 2px solid #7C3AED;">
                      <h1 style="color: #7C3AED; font-size: 42px; margin: 0; letter-spacing: 10px; font-family: monospace;">{code}</h1>
                      <p style="color: #666; margin: 10px 0 0; font-size: 14px;">Enter this code to verify your identity</p>
                    </div>
                    
                    <p style="color: #e74c3c; font-size: 14px; text-align: center;">
                      ⏰ This code expires in 10 minutes
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #666; font-size: 14px;">
                      If you didn't request this code, please ignore this email.
                    </p>
                  </div>
                  
                  <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
                    <p style="margin: 0;">FindBug Platform - Bug Bounty & Security Research</p>
                    <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ KYC verification code sent to {email}")
            print(f"   Code: {code} (expires in 10 minutes)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send KYC verification email: {e}")
            return False

    @staticmethod
    def send_password_reset_email(email: str, reset_token: str):
        """
        Send password reset email

        Args:
            email: User email address
            reset_token: Password reset token
        """
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

        print(f"\n{'='*60}")
        print(f"📧 PASSWORD RESET EMAIL")
        print(f"{'='*60}")
        print(f"To: {email}")
        print(f"Subject: Reset Your Password")
        print(f"\nClick the link below to reset your password:")
        print(f"{reset_link}")
        print(f"\nThis link will expire in 15 minutes.")
        print(f"If you didn't request this, please ignore this email.")
        print(f"{'='*60}\n")

        # TODO: Replace with actual email service (SendGrid, AWS SES, etc.)

    @staticmethod
    def send_html_email(
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send HTML email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback (optional)
            
        Returns:
            True if sent successfully
        """
        try:
            # Email configuration from environment
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from = os.getenv('SMTP_FROM', 'noreply@bugbounty.com')
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP credentials not configured. Email not sent.")
                return False
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_from
            msg['To'] = to_email
            
            # Add plain text part if provided
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ HTML email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send HTML email: {e}")
            return False


class BusinessEmailValidator:
    """Validate business emails for organizations"""
    
    # Common personal email domains to block
    PERSONAL_EMAIL_DOMAINS = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'aol.com', 'icloud.com', 'mail.com', 'protonmail.com',
        'yandex.com', 'zoho.com', 'gmx.com', 'live.com',
        'msn.com', 'me.com', 'inbox.com', 'fastmail.com'
    ]
    
    @staticmethod
    def is_business_email(email: str) -> tuple[bool, str]:
        """
        Check if email is a business email (not personal)
        
        Returns: (is_valid, error_message)
        """
        if not email or '@' not in email:
            return False, "Invalid email format"
        
        domain = email.split('@')[1].lower()
        
        if domain in BusinessEmailValidator.PERSONAL_EMAIL_DOMAINS:
            return False, f"Personal email domains ({domain}) are not allowed for organizations. Please use your company email."
        
        return True, ""
    
    @staticmethod
    def validate_domain_format(domain: str) -> bool:
        """Validate domain format"""
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None
