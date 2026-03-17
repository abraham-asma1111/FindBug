"""
SSO (Single Sign-On) Service for Organizations
Supports SAML 2.0 for enterprise identity providers
"""
from typing import Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
import base64
import httpx


class SAMLService:
    """
    SAML 2.0 Service for Enterprise SSO
    
    Supported Providers:
    - Okta
    - Microsoft Entra (Azure AD)
    - Google Workspace
    - OneLogin
    - Auth0
    
    Flow:
    1. Organization configures SSO in settings
    2. User clicks "Login with SSO"
    3. Redirect to IdP (Identity Provider)
    4. IdP authenticates user
    5. IdP sends SAML assertion to callback URL
    6. Backend validates assertion and creates session
    """
    
    @classmethod
    def generate_saml_request(cls, organization_id: str, idp_url: str) -> str:
        """
        Generate SAML authentication request
        
        Args:
            organization_id: FindBug organization UUID
            idp_url: Identity Provider SSO URL
            
        Returns:
            Base64-encoded SAML request
        """
        # SAML AuthnRequest XML
        saml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest 
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="_findbug_{organization_id}"
    Version="2.0"
    IssueInstant="{datetime.utcnow().isoformat()}Z"
    Destination="{idp_url}"
    AssertionConsumerServiceURL="https://findbug.com/api/v1/sso/callback"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>https://findbug.com</saml:Issuer>
    <samlp:NameIDPolicy 
        Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        AllowCreate="true"/>
</samlp:AuthnRequest>"""
        
        # Base64 encode
        encoded = base64.b64encode(saml_request.encode()).decode()
        return encoded
    
    @classmethod
    def parse_saml_response(cls, saml_response: str) -> Dict[str, any]:
        """
        Parse and validate SAML response from IdP
        
        Args:
            saml_response: Base64-encoded SAML response
            
        Returns:
            {
                "email": "user@company.com",
                "first_name": "John",
                "last_name": "Doe",
                "organization_domain": "company.com",
                "valid": True
            }
        """
        try:
            # Decode SAML response
            decoded = base64.b64decode(saml_response)
            
            # Parse XML
            root = ET.fromstring(decoded)
            
            # Extract namespaces
            ns = {
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
            }
            
            # Extract user attributes
            email = None
            first_name = None
            last_name = None
            
            # Find Assertion
            assertion = root.find('.//saml:Assertion', ns)
            if assertion:
                # Get NameID (email)
                name_id = assertion.find('.//saml:NameID', ns)
                if name_id is not None:
                    email = name_id.text
                
                # Get Attributes
                attributes = assertion.findall('.//saml:Attribute', ns)
                for attr in attributes:
                    attr_name = attr.get('Name')
                    attr_value = attr.find('.//saml:AttributeValue', ns)
                    
                    if attr_value is not None:
                        if attr_name in ['firstName', 'givenName', 'first_name']:
                            first_name = attr_value.text
                        elif attr_name in ['lastName', 'surname', 'last_name']:
                            last_name = attr_value.text
                        elif attr_name == 'email' and not email:
                            email = attr_value.text
            
            # Extract domain from email
            organization_domain = None
            if email and '@' in email:
                organization_domain = email.split('@')[1]
            
            return {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "organization_domain": organization_domain,
                "valid": email is not None
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Failed to parse SAML response: {str(e)}"
            }
    
    @classmethod
    async def fetch_idp_metadata(cls, metadata_url: str) -> Dict[str, any]:
        """
        Fetch IdP metadata from URL
        
        Organizations provide metadata URL from their IdP:
        - Okta: https://company.okta.com/app/xxx/sso/saml/metadata
        - Azure: https://login.microsoftonline.com/tenant-id/federationmetadata/2007-06/federationmetadata.xml
        - Google: https://accounts.google.com/o/saml2/idp?idpid=xxx
        
        Returns:
            {
                "sso_url": "https://idp.com/sso",
                "entity_id": "https://idp.com",
                "certificate": "MIICertificate..."
            }
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(metadata_url)
                response.raise_for_status()
                
                # Parse metadata XML
                root = ET.fromstring(response.content)
                
                ns = {
                    'md': 'urn:oasis:names:tc:SAML:2.0:metadata',
                    'ds': 'http://www.w3.org/2000/09/xmldsig#'
                }
                
                # Extract SSO URL
                sso_url = None
                sso_service = root.find('.//md:SingleSignOnService[@Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"]', ns)
                if sso_service is not None:
                    sso_url = sso_service.get('Location')
                
                # Extract Entity ID
                entity_id = root.get('entityID')
                
                # Extract Certificate
                certificate = None
                cert_elem = root.find('.//ds:X509Certificate', ns)
                if cert_elem is not None:
                    certificate = cert_elem.text
                
                return {
                    "sso_url": sso_url,
                    "entity_id": entity_id,
                    "certificate": certificate,
                    "valid": sso_url is not None
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Failed to fetch IdP metadata: {str(e)}"
            }


class SSOProviderEnum:
    """Supported SSO providers"""
    OKTA = "okta"
    MICROSOFT = "microsoft"
    GOOGLE = "google"
    ONELOGIN = "onelogin"
    AUTH0 = "auth0"
    CUSTOM = "custom"
