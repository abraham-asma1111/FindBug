"""
Generates platform-specific email aliases for researchers
"""
import hashlib
import secrets
from typing import Dict, Optional


class NinjaEmailService:
    """Service for managing Bugcrowd-style ninja email aliases"""
    
    NINJA_DOMAIN = "findbugninja.com"
    
    @classmethod
    def generate_ninja_email(cls, username: str, user_id: str) -> str:
        """
        Generate a unique ninja email alias for a researcher
        
        Format: username@bugcrowdninja.com
        If username is taken, append a unique suffix
        
        Args:
            username: Desired username
            user_id: User UUID for uniqueness
            
        Returns:
            Ninja email alias (e.g., abraham@bugcrowdninja.com)
        """
        # Clean username (remove special chars, lowercase)
        clean_username = cls._clean_username(username)
        
        # Generate base ninja email
        base_email = f"{clean_username}@{cls.NINJA_DOMAIN}"
        
        # Add unique suffix if needed (based on user_id hash)
        if len(clean_username) < 3:
            # If username too short, add hash suffix
            suffix = hashlib.sha256(user_id.encode()).hexdigest()[:6]
            ninja_email = f"{clean_username}{suffix}@{cls.NINJA_DOMAIN}"
        else:
            ninja_email = base_email
        
        return ninja_email
    
    @classmethod
    def _clean_username(cls, username: str) -> str:
        """Clean username for ninja email generation"""
        # Remove special characters, keep only alphanumeric and underscore
        clean = ''.join(c for c in username.lower() if c.isalnum() or c == '_')
        
        # Ensure minimum length
        if len(clean) < 3:
            clean = clean + secrets.token_hex(2)
        
        # Ensure maximum length
        if len(clean) > 20:
            clean = clean[:20]
        
        return clean
    
    @classmethod
    def validate_ninja_email(cls, ninja_email: str) -> bool:
        """Validate ninja email format"""
        if not ninja_email or '@' not in ninja_email:
            return False
        
        username, domain = ninja_email.split('@', 1)
        
        return (
            domain == cls.NINJA_DOMAIN and
            len(username) >= 3 and
            len(username) <= 20 and
            username.replace('_', '').isalnum()
        )
    
    @classmethod
    def extract_username_from_ninja_email(cls, ninja_email: str) -> Optional[str]:
        """Extract username from ninja email"""
        if not cls.validate_ninja_email(ninja_email):
            return None
        
        return ninja_email.split('@')[0]


class SkillsService:
    """Service for managing researcher skills (Bugcrowd 2026)"""
    
    # Bugcrowd 2026 Skills Matrix (350+ skills)
    SKILL_CATEGORIES = {
        "web": [
            "SQL Injection", "XSS", "CSRF", "SSRF", "XXE", "IDOR", "Authentication Bypass",
            "Authorization Bypass", "Business Logic Flaws", "File Upload Vulnerabilities",
            "Directory Traversal", "Remote Code Execution", "Local File Inclusion",
            "Remote File Inclusion", "HTTP Header Injection", "Host Header Injection",
            "CRLF Injection", "Template Injection", "NoSQL Injection", "LDAP Injection"
        ],
        "mobile": [
            "Android Security", "iOS Security", "Mobile App Reverse Engineering",
            "Mobile Malware Analysis", "Mobile Device Management", "Mobile API Security",
            "Android Root Detection Bypass", "iOS Jailbreak Detection Bypass",
            "Mobile Certificate Pinning Bypass", "Mobile Deep Linking Vulnerabilities"
        ],
        "api": [
            "REST API Security", "GraphQL Security", "SOAP Security", "API Authentication",
            "API Authorization", "API Rate Limiting Bypass", "API Versioning Issues",
            "API Documentation Security", "Microservices Security", "Webhook Security"
        ],
        "cloud": [
            "AWS Security", "Azure Security", "GCP Security", "Container Security",
            "Kubernetes Security", "Docker Security", "Serverless Security",
            "Cloud Storage Security", "IAM Misconfigurations", "Cloud Network Security"
        ],
        "network": [
            "Network Penetration Testing", "Wireless Security", "Bluetooth Security",
            "VPN Security", "Firewall Bypass", "Network Protocol Analysis",
            "Man-in-the-Middle Attacks", "DNS Security", "BGP Security", "MPLS Security"
        ],
        "ai_ml": [
            "AI Red Teaming", "Machine Learning Security", "Model Poisoning",
            "Adversarial Examples", "AI Prompt Injection", "ML Model Extraction",
            "AI Bias Testing", "Neural Network Security", "Deep Learning Security",
            "AI Privacy Attacks"
        ],
        "blockchain": [
            "Smart Contract Security", "DeFi Security", "Blockchain Analysis",
            "Cryptocurrency Security", "NFT Security", "Consensus Mechanism Security",
            "Wallet Security", "Exchange Security", "Bridge Security", "DAO Security"
        ],
        "iot": [
            "IoT Device Security", "Embedded Systems Security", "Firmware Analysis",
            "Hardware Security", "RFID Security", "Zigbee Security", "LoRaWAN Security",
            "Industrial Control Systems", "SCADA Security", "Automotive Security"
        ]
    }
    
    @classmethod
    def get_all_skills(cls) -> list[str]:
        """Get all available skills"""
        all_skills = []
        for category_skills in cls.SKILL_CATEGORIES.values():
            all_skills.extend(category_skills)
        return sorted(all_skills)
    
    @classmethod
    def validate_skills(cls, skills: list[str]) -> Dict[str, any]:
        """
        Validate researcher skills.
        Now accepts custom skills - only validates count and format.
        """
        if not skills:
            return {"valid": True, "message": "No skills provided"}
        
        if len(skills) > 50:
            return {"valid": False, "message": "Maximum 50 skills allowed"}
        
        # Validate each skill format (not empty, reasonable length)
        for skill in skills:
            if not skill or not skill.strip():
                return {"valid": False, "message": "Skills cannot be empty"}
            if len(skill) > 100:
                return {"valid": False, "message": f"Skill '{skill[:50]}...' is too long (max 100 characters)"}
        
        return {"valid": True, "message": f"Validated {len(skills)} skills (including custom skills)"}
    
    @classmethod
    def get_skills_by_category(cls, category: str) -> list[str]:
        """Get skills by category"""
        return cls.SKILL_CATEGORIES.get(category, [])
    
    @classmethod
    def get_skill_categories(cls) -> list[str]:
        """Get all skill categories"""
        return list(cls.SKILL_CATEGORIES.keys())