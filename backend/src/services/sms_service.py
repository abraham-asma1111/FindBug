"""
SMS Service for Phone Verification
Supports Ethiopian phone numbers and international formats
"""
import os
import random
import string
import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta
from src.core.logging import get_logger

logger = get_logger(__name__)


class SMSService:
    """Service for sending SMS verification codes"""
    
    def __init__(self):
        self.mock_mode = os.getenv("SMS_MOCK_MODE", "true").lower() == "true"
        self.api_key = os.getenv("SMS_API_KEY")
        self.sender_id = os.getenv("SMS_SENDER_ID", "FindBug")
        
        # SMS provider configuration (can be configured for Ethiopian providers)
        self.provider = os.getenv("SMS_PROVIDER", "mock")  # mock, twilio, africastalking, etc.
        
        if self.mock_mode:
            logger.info("SMS Service running in MOCK MODE - codes will be logged only")
    
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """
        Generate random numeric verification code.
        
        Args:
            length: Length of code (default 6 digits)
            
        Returns:
            Numeric verification code
        """
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def format_phone_number(phone: str) -> str:
        """
        Format phone number to international format.
        
        Supports:
        - Ethiopian numbers: +251XXXXXXXXX or 09XXXXXXXX
        - International numbers: +XXXXXXXXXXXX
        
        Args:
            phone: Phone number in various formats
            
        Returns:
            Formatted phone number with country code
        """
        # Remove all non-digit characters except +
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # If starts with +, assume it's already formatted
        if phone.startswith('+'):
            return phone
        
        # Ethiopian number starting with 09
        if phone.startswith('09') and len(phone) == 10:
            return f'+251{phone[1:]}'  # +251 9XXXXXXXX
        
        # Ethiopian number starting with 9
        if phone.startswith('9') and len(phone) == 9:
            return f'+251{phone}'  # +251 9XXXXXXXX
        
        # Ethiopian number starting with 07 (Ethio Telecom)
        if phone.startswith('07') and len(phone) == 10:
            return f'+251{phone[1:]}'  # +251 7XXXXXXXX
        
        # Assume Ethiopian if 9 digits
        if len(phone) == 9:
            return f'+251{phone}'
        
        # Otherwise, add + if not present
        if not phone.startswith('+'):
            phone = f'+{phone}'
        
        return phone
    
    @staticmethod
    def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            formatted = SMSService.format_phone_number(phone)
            
            # Check minimum length
            if len(formatted) < 10:
                return False, "Phone number too short"
            
            # Check maximum length
            if len(formatted) > 16:
                return False, "Phone number too long"
            
            # Check if starts with +
            if not formatted.startswith('+'):
                return False, "Phone number must include country code"
            
            return True, None
        
        except Exception as e:
            return False, f"Invalid phone number format: {str(e)}"
    
    async def send_verification_code(
        self,
        phone_number: str,
        code: str,
        user_name: Optional[str] = None
    ) -> Dict:
        """
        Send SMS verification code.
        
        Args:
            phone_number: Phone number to send to
            code: Verification code
            user_name: Optional user name for personalization
            
        Returns:
            Dict with send status
        """
        # Format phone number
        formatted_phone = self.format_phone_number(phone_number)
        
        # Validate phone number
        is_valid, error = self.validate_phone_number(formatted_phone)
        if not is_valid:
            raise ValueError(error)
        
        # Create message
        greeting = f"Hi {user_name}, " if user_name else ""
        message = (
            f"{greeting}Your FindBug verification code is: {code}. "
            f"This code expires in 10 minutes. Do not share this code with anyone."
        )
        
        # MOCK MODE: Just log the code
        if self.mock_mode:
            logger.info(
                f"[SMS MOCK] Sending verification code to {formatted_phone}: {code}",
                extra={
                    "phone": formatted_phone,
                    "code": code,
                    "message": message
                }
            )
            
            return {
                "success": True,
                "provider": "mock",
                "phone": formatted_phone,
                "message": f"SMS sent (MOCK MODE). Code: {code}",
                "mock_code": code  # Include code in response for testing
            }
        
        # PRODUCTION MODE: Send via SMS provider
        try:
            if self.provider == "africastalking":
                return await self._send_via_africastalking(formatted_phone, message)
            elif self.provider == "twilio":
                return await self._send_via_twilio(formatted_phone, message)
            else:
                raise ValueError(f"Unsupported SMS provider: {self.provider}")
        
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}", extra={
                "phone": formatted_phone,
                "provider": self.provider
            })
            raise Exception(f"Failed to send SMS: {str(e)}")
    
    async def _send_via_africastalking(self, phone: str, message: str) -> Dict:
        """
        Send SMS via Africa's Talking (popular in Ethiopia).
        
        Setup:
        1. Sign up at https://africastalking.com
        2. Set SMS_API_KEY in environment
        3. Set SMS_SENDER_ID (your approved sender ID)
        """
        if not self.api_key:
            raise ValueError("SMS_API_KEY not configured for Africa's Talking")
        
        username = os.getenv("AFRICASTALKING_USERNAME", "sandbox")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.africastalking.com/version1/messaging",
                headers={
                    "apiKey": self.api_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                data={
                    "username": username,
                    "to": phone,
                    "message": message,
                    "from": self.sender_id
                }
            )
            
            response_text = response.text
            logger.info(f"Africa's Talking response: {response.status_code} - {response_text}")
            
            if response.status_code != 201:
                raise Exception(f"Africa's Talking API error ({response.status_code}): {response_text}")
            
            data = response.json()
            
            logger.info(f"SMS sent via Africa's Talking to {phone}")
            
            return {
                "success": True,
                "provider": "africastalking",
                "phone": phone,
                "message": "SMS sent successfully",
                "response": data
            }
    
    async def _send_via_twilio(self, phone: str, message: str) -> Dict:
        """
        Send SMS via Twilio (international provider).
        
        Setup:
        1. Sign up at https://www.twilio.com
        2. Set TWILIO_ACCOUNT_SID in environment
        3. Set TWILIO_AUTH_TOKEN in environment
        4. Set TWILIO_PHONE_NUMBER (your Twilio number)
        """
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([account_sid, auth_token, from_number]):
            raise ValueError("Twilio credentials not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
                auth=(account_sid, auth_token),
                data={
                    "To": phone,
                    "From": from_number,
                    "Body": message
                }
            )
            
            if response.status_code != 201:
                raise Exception(f"Twilio API error: {response.text}")
            
            logger.info(f"SMS sent via Twilio to {phone}")
            
            return {
                "success": True,
                "provider": "twilio",
                "phone": phone,
                "message": "SMS sent successfully"
            }
