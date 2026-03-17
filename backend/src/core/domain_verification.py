"""
Domain Verification Service for Organizations
Similar to how Bugcrowd, HackerOne verify organization domains
"""
import dns.resolver
import httpx
import secrets
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta


class DomainVerificationService:
    """
    Service for verifying organization domain ownership
    
    Three verification methods:
    1. DNS TXT Record - Add TXT record to domain DNS
    2. Email Verification - Send code to admin@domain.com
    3. File Verification - Upload file to .well-known/findbug-verification.txt
    """
    
    VERIFICATION_PREFIX = "findbug-verification"
    
    @classmethod
    def generate_verification_token(cls) -> str:
        """Generate unique verification token"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def extract_domain_from_email(cls, email: str) -> Optional[str]:
        """Extract domain from email address"""
        if '@' not in email:
            return None
        return email.split('@')[1].lower()
    
    @classmethod
    def extract_domain_from_url(cls, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        
        # Remove protocol
        url = url.replace('https://', '').replace('http://', '')
        
        # Remove path
        domain = url.split('/')[0]
        
        # Remove port
        domain = domain.split(':')[0]
        
        # Remove www
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower()
    
    @classmethod
    def verify_dns_txt_record(cls, domain: str, verification_token: str) -> Tuple[bool, str]:
        """
        Verify domain ownership via DNS TXT record
        
        Organization must add TXT record:
        findbug-verification=<token>
        
        Args:
            domain: Domain to verify (e.g., techcorp.com)
            verification_token: Expected token value
            
        Returns:
            (success, message)
        """
        try:
            # Query DNS TXT records
            answers = dns.resolver.resolve(domain, 'TXT')
            
            expected_record = f"{cls.VERIFICATION_PREFIX}={verification_token}"
            
            for rdata in answers:
                # TXT records are returned as quoted strings
                txt_value = str(rdata).strip('"')
                
                if txt_value == expected_record:
                    return True, "Domain verified successfully via DNS TXT record"
            
            return False, f"DNS TXT record not found. Please add: {expected_record}"
            
        except dns.resolver.NXDOMAIN:
            return False, f"Domain {domain} does not exist"
        except dns.resolver.NoAnswer:
            return False, f"No TXT records found for {domain}"
        except dns.resolver.Timeout:
            return False, "DNS query timeout. Please try again."
        except Exception as e:
            return False, f"DNS verification failed: {str(e)}"
    
    @classmethod
    async def verify_file_based(cls, domain: str, verification_token: str) -> Tuple[bool, str]:
        """
        Verify domain ownership via file upload
        
        Organization must upload file to:
        https://domain.com/.well-known/findbug-verification.txt
        
        File content: <verification_token>
        
        Args:
            domain: Domain to verify
            verification_token: Expected token value
            
        Returns:
            (success, message)
        """
        verification_url = f"https://{domain}/.well-known/findbug-verification.txt"
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(verification_url)
                
                if response.status_code == 200:
                    content = response.text.strip()
                    
                    if content == verification_token:
                        return True, "Domain verified successfully via file upload"
                    else:
                        return False, "Verification file found but token doesn't match"
                else:
                    return False, f"Verification file not found at {verification_url}"
                    
        except httpx.TimeoutException:
            return False, "Request timeout. Please ensure the file is accessible."
        except Exception as e:
            return False, f"File verification failed: {str(e)}"
    
    @classmethod
    def generate_admin_email(cls, domain: str) -> str:
        """Generate admin email for email-based verification"""
        return f"admin@{domain}"
    
    @classmethod
    def validate_domain_format(cls, domain: str) -> Tuple[bool, str]:
        """Validate domain format"""
        if not domain:
            return False, "Domain cannot be empty"
        
        # Basic validation
        if ' ' in domain:
            return False, "Domain cannot contain spaces"
        
        if not '.' in domain:
            return False, "Invalid domain format"
        
        # Check for invalid characters
        valid_chars = set('abcdefghijklmnopqrstuvwxyz0123456789.-')
        if not all(c in valid_chars for c in domain.lower()):
            return False, "Domain contains invalid characters"
        
        # Check length
        if len(domain) > 253:
            return False, "Domain too long"
        
        return True, "Valid domain format"
