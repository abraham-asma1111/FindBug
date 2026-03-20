"""
PTaaS Service - Business Logic
Implements FREQ-29, FREQ-30, FREQ-31
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from backend.src.domain.repositories.ptaas_repository import PTaaSRepository
from backend.src.domain.models.ptaas import PTaaSEngagement, PTaaSFinding, PTaaSDeliverable
from backend.src.services.audit_service import AuditService


class PTaaSService:
    """Service for PTaaS operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = PTaaSRepository(db)
        self.audit_service = AuditService(db)
    
    def create_engagement(
        self, 
        organization_id: int, 
        engagement_data: dict, 
        created_by: int
    ) -> PTaaSEngagement:
        """Create new PTaaS engagement - FREQ-29"""
        # Calculate duration
        start_date = engagement_data.get('start_date')
        end_date = engagement_data.get('end_date')
        duration_days = (end_date - start_date).days if start_date and end_date else None
        
        # Calculate pricing - FREQ-31
        base_price = Decimal(str(engagement_data.get('base_price', 0)))
        commission_rate = Decimal(str(engagement_data.get('platform_commission_rate', 15.00)))
        commission_amount = (base_price * commission_rate) / Decimal('100')
        total_price = base_price + commission_amount
        
        # Prepare engagement data
        engagement_dict = {
            'organization_id': organization_id,
            'name': engagement_data.get('name'),
            'description': engagement_data.get('description'),
            'scope': engagement_data.get('scope'),
            'testing_methodology': engagement_data.get('testing_methodology'),
            'custom_methodology_details': engagement_data.get('custom_methodology_details'),
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': duration_days,
            'compliance_requirements': engagement_data.get('compliance_requirements'),
            'compliance_notes': engagement_data.get('compliance_notes'),
            'deliverables': engagement_data.get('deliverables'),
            'pricing_model': engagement_data.get('pricing_model'),
            'base_price': base_price,
            'platform_commission_rate': commission_rate,
            'platform_commission_amount': commission_amount,
            'total_price': total_price,
            'subscription_interval': engagement_data.get('subscription_interval'),
            'team_size': engagement_data.get('team_size', 1),
            'created_by': created_by,
            'status': 'DRAFT'
        }
        
        # Handle subscription dates
        if engagement_data.get('pricing_model') == 'SUBSCRIPTION':
            engagement_dict['subscription_start_date'] = start_date
            engagement_dict['subscription_end_date'] = end_date
        
        engagement = self.repository.create_engagement(engagement_dict)
        
        # Audit log
        self.audit_service.log_action(
            user_id=created_by,
            action="CREATE_PTAAS_ENGAGEMENT",
            resource_type="PTaaSEngagement",
            resource_id=engagement.id,
            details={"engagement_name": engagement.name}
        )
        
        return engagement
    
    def get_engagement(self, engagement_id: int) -> Optional[PTaaSEngagement]:
        """Get engagement by ID"""
        return self.repository.get_engagement_by_id(engagement_id)
    
    def get_organization_engagements(self, organization_id: int) -> List[PTaaSEngagement]:
        """Get all engagements for an organization"""
        return self.repository.get_engagements_by_organization(organization_id)
    
    def update_engagement(
        self, 
        engagement_id: int, 
        update_data: dict, 
        updated_by: int
    ) -> Optional[PTaaSEngagement]:
        """Update engagement - FREQ-30"""
        # Recalculate pricing if base_price or commission_rate changed
        if 'base_price' in update_data or 'platform_commission_rate' in update_data:
            engagement = self.repository.get_engagement_by_id(engagement_id)
            if engagement:
                base_price = Decimal(str(update_data.get('base_price', engagement.base_price)))
                commission_rate = Decimal(str(update_data.get('platform_commission_rate', engagement.platform_commission_rate)))
                commission_amount = (base_price * commission_rate) / Decimal('100')
                total_price = base_price + commission_amount
                
                update_data['platform_commission_amount'] = commission_amount
                update_data['total_price'] = total_price
        
        # Recalculate duration if dates changed
        if 'start_date' in update_data or 'end_date' in update_data:
            engagement = self.repository.get_engagement_by_id(engagement_id)
            if engagement:
                start = update_data.get('start_date', engagement.start_date)
                end = update_data.get('end_date', engagement.end_date)
                update_data['duration_days'] = (end - start).days
        
        updated_engagement = self.repository.update_engagement(engagement_id, update_data)
        
        if updated_engagement:
            self.audit_service.log_action(
                user_id=updated_by,
                action="UPDATE_PTAAS_ENGAGEMENT",
                resource_type="PTaaSEngagement",
                resource_id=engagement_id,
                details={"updated_fields": list(update_data.keys())}
            )
        
        return updated_engagement
    
    def assign_researchers(
        self, 
        engagement_id: int, 
        researcher_ids: List[int], 
        assigned_by: int
    ) -> Optional[PTaaSEngagement]:
        """Assign researchers to engagement"""
        update_data = {
            'assigned_researchers': researcher_ids,
            'team_size': len(researcher_ids)
        }
        return self.update_engagement(engagement_id, update_data, assigned_by)
    
    def start_engagement(self, engagement_id: int, started_by: int) -> Optional[PTaaSEngagement]:
        """Start an engagement"""
        return self.update_engagement(
            engagement_id, 
            {'status': 'IN_PROGRESS'}, 
            started_by
        )
    
    def complete_engagement(self, engagement_id: int, completed_by: int) -> Optional[PTaaSEngagement]:
        """Complete an engagement"""
        return self.update_engagement(
            engagement_id, 
            {'status': 'COMPLETED'}, 
            completed_by
        )
    
    # Finding Management
    def create_finding(
        self, 
        finding_data: dict, 
        discovered_by: int
    ) -> PTaaSFinding:
        """Create a new finding with mandatory field validation - FREQ-35"""
        # Check if mandatory fields are complete
        mandatory_complete = self.check_mandatory_fields_complete(finding_data)
        
        finding_dict = {
            **finding_data, 
            'discovered_by': discovered_by,
            'mandatory_fields_complete': mandatory_complete,
            'template_version': '1.0',
            'status': 'SUBMITTED'
        }
        
        finding = self.repository.create_finding(finding_dict)
        
        self.audit_service.log_action(
            user_id=discovered_by,
            action="CREATE_PTAAS_FINDING",
            resource_type="PTaaSFinding",
            resource_id=finding.id,
            details={
                "severity": finding.severity,
                "engagement_id": finding.engagement_id,
                "mandatory_complete": mandatory_complete
            }
        )
        
        return finding
    
    def get_engagement_findings(self, engagement_id: int) -> List[PTaaSFinding]:
        """Get all findings for an engagement"""
        return self.repository.get_findings_by_engagement(engagement_id)
    
    def update_finding(
        self, 
        finding_id: int, 
        update_data: dict, 
        updated_by: int
    ) -> Optional[PTaaSFinding]:
        """Update a finding"""
        finding = self.repository.update_finding(finding_id, update_data)
        
        if finding:
            self.audit_service.log_action(
                user_id=updated_by,
                action="UPDATE_PTAAS_FINDING",
                resource_type="PTaaSFinding",
                resource_id=finding_id,
                details={"updated_fields": list(update_data.keys())}
            )
        
        return finding
    
    # Deliverable Management
    def submit_deliverable(
        self, 
        deliverable_data: dict, 
        submitted_by: int
    ) -> PTaaSDeliverable:
        """Submit a deliverable"""
        deliverable_dict = {**deliverable_data, 'submitted_by': submitted_by}
        deliverable = self.repository.create_deliverable(deliverable_dict)
        
        self.audit_service.log_action(
            user_id=submitted_by,
            action="SUBMIT_PTAAS_DELIVERABLE",
            resource_type="PTaaSDeliverable",
            resource_id=deliverable.id,
            details={"type": deliverable.deliverable_type, "engagement_id": deliverable.engagement_id}
        )
        
        return deliverable
    
    def get_engagement_deliverables(self, engagement_id: int) -> List[PTaaSDeliverable]:
        """Get all deliverables for an engagement"""
        return self.repository.get_deliverables_by_engagement(engagement_id)
    
    def approve_deliverable(
        self, 
        deliverable_id: int, 
        approved_by: int
    ) -> Optional[PTaaSDeliverable]:
        """Approve a deliverable"""
        deliverable = self.repository.approve_deliverable(deliverable_id, approved_by)
        
        if deliverable:
            self.audit_service.log_action(
                user_id=approved_by,
                action="APPROVE_PTAAS_DELIVERABLE",
                resource_type="PTaaSDeliverable",
                resource_id=deliverable_id,
                details={"engagement_id": deliverable.engagement_id}
            )
        
        return deliverable
    
    # Progress Updates
    def add_progress_update(
        self, 
        update_data: dict, 
        created_by: int
    ) -> Any:
        """Add progress update"""
        update_dict = {**update_data, 'created_by': created_by}
        return self.repository.create_progress_update(update_dict)
    
    def get_engagement_progress(self, engagement_id: int) -> List[Any]:
        """Get progress updates for engagement"""
        return self.repository.get_progress_updates_by_engagement(engagement_id)
    
    def calculate_subscription_renewal(
        self, 
        engagement: PTaaSEngagement
    ) -> Dict[str, Any]:
        """Calculate next subscription renewal - FREQ-31"""
        if engagement.pricing_model != 'SUBSCRIPTION':
            return {}
        
        interval_map = {
            'monthly': 30,
            'quarterly': 90,
            'yearly': 365
        }
        
        days = interval_map.get(engagement.subscription_interval, 30)
        next_renewal = engagement.subscription_start_date + timedelta(days=days)
        
        return {
            'next_renewal_date': next_renewal,
            'renewal_amount': engagement.base_price,
            'platform_commission': engagement.platform_commission_amount,
            'total_amount': engagement.total_price
        }

    # Finding Validation - FREQ-35
    def validate_finding(
        self,
        finding_id: int,
        validated_by: int,
        validated: bool,
        retest_required: bool = False,
        retest_notes: Optional[str] = None
    ) -> Optional[PTaaSFinding]:
        """
        Validate a finding - FREQ-35
        Marks finding as validated by organization/staff
        """
        update_data = {
            'validated': validated,
            'validated_by': validated_by,
            'validated_at': datetime.utcnow(),
            'retest_required': retest_required,
            'retest_notes': retest_notes
        }
        
        finding = self.repository.update_finding(finding_id, update_data)
        
        if finding:
            self.audit_service.log_action(
                user_id=validated_by,
                action="VALIDATE_PTAAS_FINDING",
                resource_type="PTaaSFinding",
                resource_id=finding_id,
                details={
                    "validated": validated,
                    "retest_required": retest_required,
                    "engagement_id": finding.engagement_id
                }
            )
        
        return finding
    
    def get_finding(self, finding_id: int) -> Optional[PTaaSFinding]:
        """Get finding by ID"""
        return self.repository.get_finding_by_id(finding_id)
    
    def check_mandatory_fields_complete(self, finding_data: dict) -> bool:
        """
        Check if all mandatory fields are complete - FREQ-35
        
        Mandatory fields:
        - proof_of_exploit
        - impact_analysis
        - remediation (with steps)
        - affected_component
        - reproduction_steps
        """
        mandatory_fields = [
            'proof_of_exploit',
            'impact_analysis',
            'remediation',
            'affected_component',
            'reproduction_steps',
            'remediation_steps',
            'technical_impact',
            'business_impact',
            'remediation_priority',
            'remediation_effort',
            'vulnerability_type'
        ]
        
        # Check all mandatory fields are present and not empty
        for field in mandatory_fields:
            value = finding_data.get(field)
            if not value:
                return False
            
            # For string fields, check minimum length
            if isinstance(value, str) and len(value.strip()) < 10:
                return False
            
            # For list fields, check not empty
            if isinstance(value, list) and len(value) == 0:
                return False
            
            # For dict fields, check not empty
            if isinstance(value, dict) and len(value) == 0:
                return False
        
        return True
    
    def get_finding_template(self) -> Dict[str, Any]:
        """
        Get structured finding template - FREQ-35
        Returns template with field descriptions and requirements
        """
        return {
            "template_version": "1.0",
            "sections": {
                "basic_information": {
                    "title": {"type": "string", "required": True, "min_length": 3},
                    "description": {"type": "string", "required": True, "min_length": 10},
                    "severity": {"type": "enum", "required": True, "values": ["Critical", "High", "Medium", "Low", "Info"]},
                    "affected_component": {"type": "string", "required": True}
                },
                "proof_of_exploit": {
                    "description": "Mandatory: Detailed proof that the vulnerability exists and can be exploited",
                    "proof_of_exploit": {"type": "text", "required": True, "min_length": 50},
                    "exploit_code": {"type": "text", "required": False},
                    "exploit_screenshots": {"type": "array", "required": False},
                    "exploit_video_url": {"type": "url", "required": False},
                    "reproduction_steps": {"type": "text", "required": True, "min_length": 20}
                },
                "impact_analysis": {
                    "description": "Mandatory: Comprehensive analysis of the vulnerability's impact",
                    "impact_analysis": {"type": "text", "required": True, "min_length": 50},
                    "business_impact": {"type": "enum", "required": True, "values": ["Critical", "High", "Medium", "Low"]},
                    "technical_impact": {
                        "type": "object",
                        "required": True,
                        "fields": {
                            "confidentiality": {"type": "enum", "values": ["High", "Low", "None"]},
                            "integrity": {"type": "enum", "values": ["High", "Low", "None"]},
                            "availability": {"type": "enum", "values": ["High", "Low", "None"]}
                        }
                    },
                    "affected_users": {"type": "string", "required": False},
                    "data_at_risk": {"type": "text", "required": False}
                },
                "remediation": {
                    "description": "Mandatory: Detailed remediation recommendations",
                    "remediation": {"type": "text", "required": True, "min_length": 50},
                    "remediation_priority": {"type": "enum", "required": True, "values": ["Immediate", "High", "Medium", "Low"]},
                    "remediation_effort": {"type": "enum", "required": True, "values": ["Low", "Medium", "High", "Very High"]},
                    "remediation_steps": {"type": "array", "required": True, "min_items": 1},
                    "code_fix_example": {"type": "text", "required": False}
                },
                "classification": {
                    "vulnerability_type": {"type": "string", "required": True},
                    "cwe_id": {"type": "string", "required": False},
                    "owasp_category": {"type": "string", "required": False},
                    "cvss_score": {"type": "decimal", "required": False, "range": [0, 10]}
                },
                "attack_vector": {
                    "attack_vector": {"type": "enum", "required": False, "values": ["Network", "Adjacent", "Local", "Physical"]},
                    "attack_complexity": {"type": "enum", "required": False, "values": ["Low", "High"]},
                    "privileges_required": {"type": "enum", "required": False, "values": ["None", "Low", "High"]},
                    "user_interaction": {"type": "enum", "required": False, "values": ["None", "Required"]}
                }
            }
        }
