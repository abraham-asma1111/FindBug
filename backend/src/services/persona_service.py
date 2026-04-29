"""
Persona KYC Integration Service
Handles communication with Persona API for identity verification
"""
import os
import httpx
from typing import Dict, Optional
from datetime import datetime
from src.core.logging import get_logger

logger = get_logger(__name__)


class PersonaService:
    """Service for Persona API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("PERSONA_API_KEY")
        self.environment = os.getenv("PERSONA_ENVIRONMENT", "sandbox")
        self.base_url = "https://withpersona.com/api/v1"
        self.mock_mode = os.getenv("PERSONA_MOCK_MODE", "false").lower() == "true"
        
        # Template IDs from environment
        self.template_researcher = os.getenv("PERSONA_TEMPLATE_RESEARCHER")
        self.template_organization = os.getenv("PERSONA_TEMPLATE_ORGANIZATION")
        
        if not self.api_key and not self.mock_mode:
            logger.warning("PERSONA_API_KEY not set - Persona integration disabled")
        
        if self.mock_mode:
            logger.info("Persona MOCK MODE enabled - simulating verification flow")
    
    def get_template_id(self, user_role: str) -> str:
        """Get the appropriate Persona template ID based on user role"""
        if user_role == "researcher":
            return self.template_researcher
        elif user_role == "organization":
            return self.template_organization
        else:
            raise ValueError(f"No Persona template configured for role: {user_role}")
    
    async def create_inquiry(self, user_id: str, user_role: str, reference_id: str) -> Dict:
        """
        Create a new Persona inquiry
        
        Args:
            user_id: Internal user ID
            user_role: User role (researcher/organization)
            reference_id: Reference ID for tracking
            
        Returns:
            Dict with inquiry_id and other details
        """
        # MOCK MODE: Simulate inquiry creation
        if self.mock_mode:
            import uuid
            mock_inquiry_id = f"inq_mock_{uuid.uuid4().hex[:16]}"
            template_id = self.get_template_id(user_role)
            
            logger.info(f"[MOCK] Created Persona inquiry: {mock_inquiry_id}")
            return {
                "inquiry_id": mock_inquiry_id,
                "status": "created",
                "template_id": template_id
            }
        
        if not self.api_key:
            raise ValueError("Persona API key not configured")
        
        template_id = self.get_template_id(user_role)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Persona-Version": "2023-01-05"
        }
        
        payload = {
            "data": {
                "type": "inquiry",
                "attributes": {
                    "inquiry-template-id": template_id,
                    "reference-id": reference_id,
                    "note": f"KYC verification for user {user_id}"
                }
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/inquiries",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Created Persona inquiry: {data['data']['id']}")
                return {
                    "inquiry_id": data["data"]["id"],
                    "status": data["data"]["attributes"]["status"],
                    "template_id": template_id,
                    "session_token": data.get("meta", {}).get("session-token"),
                    "one_time_link": data.get("meta", {}).get("one-time-link")
                }
        except httpx.HTTPError as e:
            logger.error(f"Failed to create Persona inquiry: {str(e)}")
            raise ValueError(f"Failed to create Persona inquiry: {str(e)}")
    
    async def get_inquiry_status(self, inquiry_id: str) -> Dict:
        """
        Get the status of a Persona inquiry
        
        Args:
            inquiry_id: Persona inquiry ID
            
        Returns:
            Dict with inquiry status and details
        """
        if not self.api_key:
            raise ValueError("Persona API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Persona-Version": "2023-01-05"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/inquiries/{inquiry_id}",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                attributes = data["data"]["attributes"]
                
                return {
                    "inquiry_id": data["data"]["id"],
                    "status": attributes["status"],
                    "created_at": attributes.get("created-at"),
                    "completed_at": attributes.get("completed-at"),
                    "decision": attributes.get("decision"),
                    "fields": attributes.get("fields", {})
                }
        except httpx.HTTPError as e:
            logger.error(f"Failed to get Persona inquiry status: {str(e)}")
            raise ValueError(f"Failed to get Persona inquiry status: {str(e)}")
    
    async def verify_inquiry(self, inquiry_id: str) -> bool:
        """
        Verify if a Persona inquiry is approved
        
        Args:
            inquiry_id: Persona inquiry ID
            
        Returns:
            True if inquiry is approved, False otherwise
        """
        try:
            status_data = await self.get_inquiry_status(inquiry_id)
            
            # Persona can return different status values:
            # - "approved" means the inquiry is approved
            # - "completed" with decision="approved" also means approved
            status = status_data["status"]
            decision = status_data.get("decision")
            
            is_approved = (
                status == "approved" or 
                status == "completed" or
                (status == "completed" and decision == "approved")
            )
            
            logger.info(f"Inquiry {inquiry_id} - Status: {status}, Decision: {decision}, Approved: {is_approved}")
            
            return is_approved
        except Exception as e:
            logger.error(f"Failed to verify inquiry {inquiry_id}: {str(e)}")
            return False
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Persona webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Signature from Persona-Signature header
            
        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib
        
        webhook_secret = os.getenv("PERSONA_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.warning("PERSONA_WEBHOOK_SECRET not set - webhook verification disabled")
            return True  # Allow in development
        
        # Compute HMAC
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
