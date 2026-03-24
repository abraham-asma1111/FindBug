"""
Email Template Service — Email template management and rendering (FREQ-12)
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
import re

from src.domain.models.ops import EmailTemplate
from src.core.exceptions import NotFoundException, ConflictException
from src.core.logging import get_logger

logger = get_logger(__name__)


class EmailTemplateService:
    """Service for email template management and rendering"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(
        self,
        name: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        variables: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a new email template.
        
        Args:
            name: Template name (unique identifier)
            subject: Email subject line (supports variables)
            body_html: HTML email body (supports variables)
            body_text: Plain text email body (optional)
            variables: List of variable names used in template
            
        Returns:
            Email template details
        """
        # Check for duplicate name
        existing = self.db.query(EmailTemplate).filter(
            EmailTemplate.name == name
        ).first()
        
        if existing:
            raise ConflictException(f"Email template '{name}' already exists.")
        
        # Extract variables from template if not provided
        if variables is None:
            variables = self._extract_variables(subject, body_html, body_text)
        
        # Create template
        template = EmailTemplate(
            name=name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            variables=variables,
            is_active=True
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        logger.info("Email template created", extra={
            "template_id": str(template.id),
            "name": name
        })
        
        return {
            "template_id": str(template.id),
            "name": template.name,
            "subject": template.subject,
            "variables": template.variables,
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat(),
            "message": "Email template created successfully."
        }
    
    def list_templates(
        self,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict:
        """
        List email templates.
        
        Args:
            is_active: Filter by active status (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of email templates
        """
        query = self.db.query(EmailTemplate)
        
        if is_active is not None:
            query = query.filter(EmailTemplate.is_active == is_active)
        
        query = query.order_by(EmailTemplate.name.asc())
        
        total = query.count()
        templates = query.offset(skip).limit(limit).all()
        
        return {
            "templates": [
                {
                    "template_id": str(t.id),
                    "name": t.name,
                    "subject": t.subject,
                    "variables": t.variables,
                    "is_active": t.is_active,
                    "created_at": t.created_at.isoformat(),
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None
                }
                for t in templates
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def get_template(self, template_id: Optional[str] = None, name: Optional[str] = None) -> Dict:
        """
        Get email template by ID or name.
        
        Args:
            template_id: Template ID (optional)
            name: Template name (optional)
            
        Returns:
            Email template details
        """
        if not template_id and not name:
            raise ValueError("Either template_id or name must be provided.")
        
        if template_id:
            template = self.db.query(EmailTemplate).filter(
                EmailTemplate.id == UUID(template_id)
            ).first()
        else:
            template = self.db.query(EmailTemplate).filter(
                EmailTemplate.name == name
            ).first()
        
        if not template:
            raise NotFoundException("Email template not found.")
        
        return {
            "template_id": str(template.id),
            "name": template.name,
            "subject": template.subject,
            "body_html": template.body_html,
            "body_text": template.body_text,
            "variables": template.variables,
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat() if template.updated_at else None
        }
    
    def update_template(
        self,
        template_id: str,
        subject: Optional[str] = None,
        body_html: Optional[str] = None,
        body_text: Optional[str] = None,
        variables: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Dict:
        """
        Update email template.
        
        Args:
            template_id: Template ID
            subject: New subject (optional)
            body_html: New HTML body (optional)
            body_text: New text body (optional)
            variables: New variables list (optional)
            is_active: Active status (optional)
            
        Returns:
            Updated template details
        """
        template = self.db.query(EmailTemplate).filter(
            EmailTemplate.id == UUID(template_id)
        ).first()
        
        if not template:
            raise NotFoundException("Email template not found.")
        
        # Update fields
        if subject is not None:
            template.subject = subject
        
        if body_html is not None:
            template.body_html = body_html
        
        if body_text is not None:
            template.body_text = body_text
        
        if variables is not None:
            template.variables = variables
        elif subject or body_html or body_text:
            # Re-extract variables if content changed
            template.variables = self._extract_variables(
                template.subject,
                template.body_html,
                template.body_text
            )
        
        if is_active is not None:
            template.is_active = is_active
        
        self.db.commit()
        self.db.refresh(template)
        
        logger.info("Email template updated", extra={
            "template_id": template_id
        })
        
        return {
            "template_id": str(template.id),
            "name": template.name,
            "subject": template.subject,
            "variables": template.variables,
            "is_active": template.is_active,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            "message": "Email template updated successfully."
        }
    
    def delete_template(self, template_id: str) -> Dict:
        """
        Delete email template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Deletion confirmation
        """
        template = self.db.query(EmailTemplate).filter(
            EmailTemplate.id == UUID(template_id)
        ).first()
        
        if not template:
            raise NotFoundException("Email template not found.")
        
        template_name = template.name
        
        self.db.delete(template)
        self.db.commit()
        
        logger.info("Email template deleted", extra={
            "template_id": template_id,
            "name": template_name
        })
        
        return {
            "template_id": template_id,
            "message": "Email template deleted successfully."
        }
    
    def render_template(
        self,
        template_id: Optional[str] = None,
        name: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Render email template with variables.
        
        Args:
            template_id: Template ID (optional)
            name: Template name (optional)
            variables: Variable values to substitute
            
        Returns:
            Rendered email content
        """
        # Get template
        template_data = self.get_template(template_id=template_id, name=name)
        
        if not template_data.get("is_active"):
            raise ValueError("Template is not active.")
        
        variables = variables or {}
        
        # Render subject
        subject = self._substitute_variables(template_data["subject"], variables)
        
        # Render HTML body
        body_html = self._substitute_variables(template_data["body_html"], variables)
        
        # Render text body (if exists)
        body_text = None
        if template_data.get("body_text"):
            body_text = self._substitute_variables(template_data["body_text"], variables)
        
        # Check for missing variables
        missing_vars = self._find_missing_variables(
            template_data["subject"],
            template_data["body_html"],
            template_data.get("body_text"),
            variables
        )
        
        if missing_vars:
            logger.warning("Missing template variables", extra={
                "template_id": template_data["template_id"],
                "missing_vars": missing_vars
            })
        
        return {
            "template_id": template_data["template_id"],
            "template_name": template_data["name"],
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text,
            "missing_variables": missing_vars
        }
    
    def _extract_variables(
        self,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> List[str]:
        """
        Extract variable names from template content.
        
        Variables are in format: {{variable_name}}
        
        Args:
            subject: Email subject
            body_html: HTML body
            body_text: Text body (optional)
            
        Returns:
            List of unique variable names
        """
        pattern = r'\{\{(\w+)\}\}'
        variables = set()
        
        # Extract from subject
        variables.update(re.findall(pattern, subject))
        
        # Extract from HTML body
        variables.update(re.findall(pattern, body_html))
        
        # Extract from text body
        if body_text:
            variables.update(re.findall(pattern, body_text))
        
        return sorted(list(variables))
    
    def _substitute_variables(self, content: str, variables: Dict[str, str]) -> str:
        """
        Substitute variables in content.
        
        Args:
            content: Content with variables
            variables: Variable values
            
        Returns:
            Content with substituted variables
        """
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            content = content.replace(placeholder, str(var_value))
        
        return content
    
    def _find_missing_variables(
        self,
        subject: str,
        body_html: str,
        body_text: Optional[str],
        variables: Dict[str, str]
    ) -> List[str]:
        """
        Find variables that are in template but not provided.
        
        Args:
            subject: Email subject
            body_html: HTML body
            body_text: Text body (optional)
            variables: Provided variables
            
        Returns:
            List of missing variable names
        """
        required_vars = set(self._extract_variables(subject, body_html, body_text))
        provided_vars = set(variables.keys())
        missing_vars = required_vars - provided_vars
        
        return sorted(list(missing_vars))
