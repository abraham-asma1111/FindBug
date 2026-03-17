"""
KYC Service using Persona Identity Verification
Similar to how LinkedIn, Coinbase, and Stripe use Persona for identity verification
"""
import httpx
from typing import Dict, Optional
from datetime import datetime
import os


class PersonaKYCService:
    """
    Persona Identity Verification Service
    
    Persona provides:
    - Government ID verification (passport, driver's license, national ID)
    - Biometric liveness detection (3D selfie with anti-spoofing)
    - Real-time verification results
    - Webhook notifications for verification status
    
    Flow:
    1. Backend creates Persona inquiry session
    2. Frontend loads Persona SDK with inquiry_id
    3. User completes verification (ID + selfie) in browser/mobile
    4. Persona sends webhook to backend with results
    5. Backend updates researcher KYC status
    """
    
    BASE_URL = "https://withpersona.com/api/v1"
    
    def __init__(self):
        self.api_key = os.getenv("PERSONA_API_KEY")
        if not self.api_key:
            raise ValueError("PERSONA_API_KEY not configured")
    
    def create_inquiry(self, researcher_id: str, email: str, first_name: str, last_name: str) -> Dict[str, any]:
        """
        Create a Persona inquiry session for KYC verification
        
        Args:
            researcher_id: FindBug researcher UUID
            email: Researcher email
            first_name: First name
            last_name: Last name
            
        Returns:
            {
                "inquiry_id": "inq_xxx",
                "session_token": "sess_xxx",
                "status": "created"
            }
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Persona-Version": "2023-01-05"
        }
        
        payload = {
            "data": {
                "attributes": {
                    "inquiry-template-id": os.getenv("PERSONA_TEMPLATE_ID", "itmpl_xxx"),
                    "reference-id": researcher_id,  # Link to our researcher
                    "fields": {
                        "name-first": first_name,
                        "name-last": last_name,
                        "email-address": email
                    }
                }
            }
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.BASE_URL}/inquiries",
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                inquiry_data = data.get("data", {})
                
                return {
                    "inquiry_id": inquiry_data.get("id"),
                    "session_token": inquiry_data.get("attributes", {}).get("session-token"),
                    "status": inquiry_data.get("attributes", {}).get("status"),
                    "created_at": datetime.utcnow().isoformat()
                }
            
        except httpx.HTTPError as e:
            raise Exception(f"Failed to create Persona inquiry: {str(e)}")
    
    def get_inquiry_status(self, inquiry_id: str) -> Dict[str, any]:
        """
        Get the status of a Persona inquiry
        
        Returns:
            {
                "inquiry_id": "inq_xxx",
                "status": "completed|failed|pending",
                "verification_status": "passed|failed",
                "document_type": "passport|drivers_license|national_id",
                "verified_at": "2026-03-17T10:30:00Z"
            }
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Persona-Version": "2023-01-05"
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.BASE_URL}/inquiries/{inquiry_id}",
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                inquiry = data.get("data", {})
                attributes = inquiry.get("attributes", {})
                
                return {
                    "inquiry_id": inquiry.get("id"),
                    "status": attributes.get("status"),
                    "verification_status": attributes.get("decision"),
                    "document_type": attributes.get("fields", {}).get("selected-id-class"),
                    "verified_at": attributes.get("completed-at"),
                    "reference_id": attributes.get("reference-id")  # Our researcher_id
                }
            
        except httpx.HTTPError as e:
            raise Exception(f"Failed to get inquiry status: {str(e)}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Persona webhook signature for security
        
        Persona signs webhooks with HMAC-SHA256
        """
        import hmac
        import hashlib
        
        webhook_secret = os.getenv("PERSONA_WEBHOOK_SECRET")
        if not webhook_secret:
            return False
        
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_webhook(self, webhook_data: Dict) -> Dict[str, any]:
        """
        Process Persona webhook notification
        
        Webhook events:
        - inquiry.completed - Verification finished
        - inquiry.failed - Verification failed
        - inquiry.expired - Session expired
        
        Returns:
            {
                "researcher_id": "uuid",
                "kyc_status": "verified|rejected|pending",
                "inquiry_id": "inq_xxx",
                "document_type": "passport"
            }
        """
        event_type = webhook_data.get("data", {}).get("type")
        attributes = webhook_data.get("data", {}).get("attributes", {})
        
        inquiry_id = webhook_data.get("data", {}).get("id")
        researcher_id = attributes.get("reference-id")
        status = attributes.get("status")
        decision = attributes.get("decision")
        
        # Map Persona decision to our KYC status
        kyc_status_map = {
            "approved": "verified",
            "declined": "rejected",
            "needs_review": "pending"
        }
        
        kyc_status = kyc_status_map.get(decision, "pending")
        
        return {
            "researcher_id": researcher_id,
            "kyc_status": kyc_status,
            "inquiry_id": inquiry_id,
            "document_type": attributes.get("fields", {}).get("selected-id-class"),
            "verified_at": attributes.get("completed-at") if kyc_status == "verified" else None
        }


class KYCStatusEnum:
    """KYC verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
