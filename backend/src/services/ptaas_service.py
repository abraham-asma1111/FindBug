"""
PTaaS Service - Business Logic
Implements FREQ-29, FREQ-30, FREQ-31
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from src.domain.repositories.ptaas_repository import PTaaSRepository
from src.domain.models.ptaas import PTaaSEngagement, PTaaSFinding, PTaaSDeliverable
from src.domain.models.ptaas_retest import PTaaSRetestRequest
from src.services.audit_service import AuditService
from src.services.notification_service import NotificationService
from src.domain.models.notification import NotificationType, NotificationPriority


class PTaaSService:
    """Service for PTaaS operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = PTaaSRepository(db)
        self.audit_service = AuditService(db)
        self.notification_service = NotificationService(db)
    
    def create_engagement(
        self, 
        organization_id: UUID, 
        engagement_data: dict, 
        created_by: UUID
    ) -> PTaaSEngagement:
        """Create new PTaaS engagement - FREQ-29"""
        # Calculate duration
        start_date = engagement_data.get('start_date')
        end_date = engagement_data.get('end_date')
        duration_days = (end_date - start_date).days if start_date and end_date else None
        
        # Calculate pricing - FREQ-31
        base_price = Decimal(str(engagement_data.get('base_price', 0)))
        commission_rate = Decimal(str(engagement_data.get('platform_commission_rate', 30.00)))
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
            action_type="CREATE_PTAAS_ENGAGEMENT",
            action_category="ptaas",
            target_type="PTaaSEngagement",
            description=f"PTaaS engagement created: {engagement.name}",
            actor_id=created_by,
            target_id=engagement.id,
            metadata={"engagement_name": engagement.name}
        )
        
        return engagement
    
    def get_engagement(self, engagement_id: UUID) -> Optional[PTaaSEngagement]:
        """Get engagement by ID"""
        return self.repository.get_engagement_by_id(engagement_id)
    
    def get_organization_engagements(self, organization_id: UUID) -> List[PTaaSEngagement]:
        """Get all engagements for an organization"""
        return self.repository.get_engagements_by_organization(organization_id)
    
    def update_engagement(
        self, 
        engagement_id: UUID, 
        update_data: dict, 
        updated_by: UUID
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
                action_type="UPDATE_PTAAS_ENGAGEMENT",
                action_category="ptaas",
                target_type="PTaaSEngagement",
                description=f"PTaaS engagement updated",
                actor_id=updated_by,
                target_id=engagement_id,
                metadata={"updated_fields": list(update_data.keys())}
            )
        
        return updated_engagement
    
    def assign_researchers(
        self, 
        engagement_id: UUID, 
        researcher_ids: List[UUID], 
        assigned_by: UUID
    ) -> Optional[PTaaSEngagement]:
        """
        Assign researchers to engagement
        ADDS to existing team (not replacing)
        """
        # Get current engagement
        engagement = self.repository.get_engagement_by_id(engagement_id)
        if not engagement:
            return None
        
        # Get existing researchers
        existing_researchers = engagement.assigned_researchers or []
        
        # Convert new researcher IDs to strings
        new_researcher_ids = [str(rid) for rid in researcher_ids]
        
        # Combine existing and new researchers (remove duplicates)
        all_researchers = list(set(existing_researchers + new_researcher_ids))
        
        # Update with combined list
        update_data = {
            'assigned_researchers': all_researchers,
            'team_size': len(all_researchers)
        }
        
        updated_engagement = self.update_engagement(engagement_id, update_data, assigned_by)
        
        # Log the addition
        if updated_engagement:
            self.audit_service.log_action(
                action_type="ASSIGN_PTAAS_RESEARCHERS",
                action_category="ptaas",
                target_type="PTaaSEngagement",
                description=f"Researchers added to team: {len(new_researcher_ids)} new, {len(all_researchers)} total",
                actor_id=assigned_by,
                target_id=engagement_id,
                metadata={
                    "new_researchers": len(new_researcher_ids),
                    "total_researchers": len(all_researchers),
                    "researcher_ids": all_researchers
                }
            )
        
        return updated_engagement
    
    def start_engagement(self, engagement_id: UUID, started_by: UUID) -> Optional[PTaaSEngagement]:
        """Start an engagement"""
        return self.update_engagement(
            engagement_id, 
            {'status': 'IN_PROGRESS'}, 
            started_by
        )
    
    def complete_engagement(self, engagement_id: UUID, completed_by: UUID) -> Optional[PTaaSEngagement]:
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
        discovered_by: UUID
    ) -> PTaaSFinding:
        """Create a new finding with mandatory field validation - FREQ-35"""
        from datetime import datetime
        
        # Check if mandatory fields are complete
        mandatory_complete = self.check_mandatory_fields_complete(finding_data)
        
        finding_dict = {
            **finding_data, 
            'discovered_by': discovered_by,
            'discovered_at': datetime.utcnow(),  # Set timestamp
            'mandatory_fields_complete': mandatory_complete,
            'template_version': '1.0',
            'status': 'SUBMITTED'
        }
        
        finding = self.repository.create_finding(finding_dict)
        
        self.audit_service.log_action(
            action_type="CREATE_PTAAS_FINDING",
            action_category="ptaas",
            target_type="PTaaSFinding",
            description=f"PTaaS finding created: {finding.severity}",
            actor_id=discovered_by,
            target_id=finding.id,
            metadata={
                "severity": finding.severity,
                "engagement_id": str(finding.engagement_id),
                "mandatory_complete": mandatory_complete
            }
        )
        
        return finding
    
    def get_engagement_findings(self, engagement_id: UUID) -> List[PTaaSFinding]:
        """Get all findings for an engagement"""
        return self.repository.get_findings_by_engagement(engagement_id)
    
    def update_finding(
        self, 
        finding_id: UUID, 
        update_data: dict, 
        updated_by: UUID
    ) -> Optional[PTaaSFinding]:
        """Update a finding"""
        finding = self.repository.update_finding(finding_id, update_data)
        
        if finding:
            self.audit_service.log_action(
                action_type="UPDATE_PTAAS_FINDING",
                action_category="ptaas",
                target_type="PTaaSFinding",
                description=f"PTaaS finding updated",
                actor_id=updated_by,
                target_id=finding_id,
                metadata={"updated_fields": list(update_data.keys())}
            )
        
        return finding
    
    # Deliverable Management
    def submit_deliverable(
        self, 
        deliverable_data: dict, 
        submitted_by: UUID
    ) -> PTaaSDeliverable:
        """Submit a deliverable"""
        deliverable_dict = {**deliverable_data, 'submitted_by': submitted_by}
        deliverable = self.repository.create_deliverable(deliverable_dict)
        
        self.audit_service.log_action(
            action_type="SUBMIT_PTAAS_DELIVERABLE",
            action_category="ptaas",
            target_type="PTaaSDeliverable",
            description=f"PTaaS deliverable submitted: {deliverable.deliverable_type}",
            actor_id=submitted_by,
            target_id=deliverable.id,
            metadata={"type": deliverable.deliverable_type, "engagement_id": str(deliverable.engagement_id)}
        )
        
        return deliverable
    
    def get_engagement_deliverables(self, engagement_id: UUID) -> List[PTaaSDeliverable]:
        """Get all deliverables for an engagement"""
        return self.repository.get_deliverables_by_engagement(engagement_id)
    
    def approve_deliverable(
        self, 
        deliverable_id: UUID, 
        approved_by: UUID
    ) -> Optional[PTaaSDeliverable]:
        """Approve a deliverable"""
        deliverable = self.repository.approve_deliverable(deliverable_id, approved_by)
        
        if deliverable:
            self.audit_service.log_action(
                action_type="APPROVE_PTAAS_DELIVERABLE",
                action_category="ptaas",
                target_type="PTaaSDeliverable",
                description=f"PTaaS deliverable approved",
                actor_id=approved_by,
                target_id=deliverable_id,
                metadata={"engagement_id": str(deliverable.engagement_id)}
            )
        
        return deliverable
    
    # Progress Updates
    def add_progress_update(
        self, 
        update_data: dict, 
        created_by: UUID
    ) -> Any:
        """Add progress update"""
        update_dict = {**update_data, 'created_by': created_by}
        return self.repository.create_progress_update(update_dict)
    
    def get_engagement_progress(self, engagement_id: UUID) -> List[Any]:
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
        finding_id: UUID,
        validated_by: UUID,
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
                action_type="VALIDATE_PTAAS_FINDING",
                action_category="ptaas",
                target_type="PTaaSFinding",
                description=f"PTaaS finding validated: {validated}",
                actor_id=validated_by,
                target_id=finding_id,
                metadata={
                    "validated": validated,
                    "retest_required": retest_required,
                    "engagement_id": str(finding.engagement_id)
                }
            )
        
        return finding
    
    def get_finding(self, finding_id: UUID) -> Optional[PTaaSFinding]:
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

    # Retest and Workflow Additions
    def request_retest(self, finding_id: UUID, requested_by: UUID, fix_description: str) -> Optional[PTaaSFinding]:
        """Request a retest for a fixed finding (Org -> Researcher)"""
        finding = self.get_finding(finding_id)
        if not finding:
            return None

        # Update finding status
        update_data = {
            'status': 'RETEST_REQUESTED',
            'retest_required': True
        }
        updated_finding = self.update_finding(finding_id, update_data, requested_by)

        # Create Retest Request record
        retest_request = PTaaSRetestRequest(
            finding_id=finding_id,
            engagement_id=finding.engagement_id,
            requested_by=requested_by,
            fix_description=fix_description,
            status='PENDING'
        )
        self.db.add(retest_request)
        self.db.commit()

        # Notify researcher
        if finding.discovered_by:
            self.notification_service.create_notification(
                user_id=finding.discovered_by,
                notification_type=NotificationType.REPORT_STATUS_CHANGED,
                title="Retest Requested for PTaaS Finding",
                message=f"Organization requested a retest for finding '{finding.title}'.",
                priority=NotificationPriority.HIGH,
                related_entity_type="ptaas_finding",
                related_entity_id=finding.id,
                action_url=f"/researcher/programs/ptaas/{finding.engagement_id}/findings/{finding.id}"
            )

        return updated_finding

    def submit_retest_result(self, finding_id: UUID, researcher_id: UUID, is_fixed: bool, retest_notes: str) -> Optional[PTaaSFinding]:
        """Submit a retest result (Researcher -> Org)"""
        finding = self.get_finding(finding_id)
        if not finding:
            return None

        # Update finding status
        new_status = 'VERIFIED' if is_fixed else 'IN_PROGRESS'
        update_data = {
            'status': new_status,
            'retest_notes': retest_notes,
            'retest_required': False if is_fixed else True
        }
        updated_finding = self.update_finding(finding_id, update_data, researcher_id)

        # Update latest pending retest request
        retest_request = self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.finding_id == finding_id,
            PTaaSRetestRequest.status == 'PENDING'
        ).order_by(PTaaSRetestRequest.created_at.desc()).first()

        if retest_request:
            retest_request.status = 'COMPLETED'
            retest_request.retest_completed_at = datetime.utcnow()
            retest_request.retest_result = 'FIXED' if is_fixed else 'NOT_FIXED'
            retest_request.retest_notes = retest_notes
            self.db.commit()

        # Notify engagement owner / org
        engagement = self.get_engagement(finding.engagement_id)
        if engagement and engagement.created_by:
            status_str = "fixed" if is_fixed else "not fixed"
            self.notification_service.create_notification(
                user_id=engagement.created_by,
                notification_type=NotificationType.REPORT_STATUS_CHANGED,
                title=f"Retest Result: {status_str.upper()}",
                message=f"Researcher verified finding '{finding.title}' is {status_str}.",
                priority=NotificationPriority.HIGH,
                related_entity_type="ptaas_finding",
                related_entity_id=finding.id,
                action_url=f"/organization/services/ptaas/{finding.engagement_id}/findings/{finding.id}"
            )

        return updated_finding

    def approve_ptaas_bounty(
        self,
        finding_id: UUID,
        approved_by_user_id: UUID,
        organization_user_id: UUID,
    ) -> Optional[PTaaSFinding]:
        """
        Organization approves PTaaS bounty: wallet debit + finance queue (same as bug bounty).
        Researcher is paid by Finance after payment status is processed — not instant credit here.
        """
        from decimal import Decimal
        import uuid as uuid_lib
        from datetime import datetime
        from src.services.wallet_service import WalletService
        from src.services.payment_service import PaymentService
        from src.domain.models.bounty_payment import BountyPayment
        from src.domain.models.user import User as UserModel

        finding = self.get_finding(finding_id)
        if not finding:
            return None

        engagement = self.get_engagement(finding.engagement_id)
        if not engagement:
            raise ValueError("Engagement not found")

        status_upper = (finding.status or "").upper()
        if status_upper not in ("VALIDATED", "VERIFIED") and not finding.validated:
            raise ValueError(
                "Only validated findings can receive bounty approval. "
                f"Current status: {finding.status}"
            )

        if not finding.bounty_amount or Decimal(str(finding.bounty_amount)) <= 0:
            from src.services.ptaas_bounty_utils import calculate_ptaas_bounty_amount
            calculated = calculate_ptaas_bounty_amount(
                engagement.base_price,
                finding.severity,
            )
            if calculated is None:
                raise ValueError(
                    "Bounty amount is not set. Complete triage validation first or set engagement base price."
                )
            finding.bounty_amount = calculated
            finding.bounty_status = "pending"
            self.db.commit()
            self.db.refresh(finding)

        if finding.bounty_status in ("approved", "paid"):
            raise ValueError("Bounty has already been approved for this finding")

        existing_payment = self.db.query(BountyPayment).filter(
            BountyPayment.ptaas_finding_id == finding_id,
            BountyPayment.status.in_(["approved", "processing", "completed", "pending"]),
        ).first()
        if existing_payment and existing_payment.status in ("approved", "processing", "completed"):
            raise ValueError("Bounty payment already approved for this finding")

        bounty_amount = Decimal(str(finding.bounty_amount))
        commission = bounty_amount * Decimal("0.30")
        total_cost = bounty_amount + commission

        wallet_service = WalletService(self.db)
        payment_service = PaymentService(self.db)

        org_wallet = wallet_service.get_or_create_wallet(
            owner_id=organization_user_id,
            owner_type="organization",
        )
        if org_wallet.available_balance < total_cost:
            raise ValueError(
                f"Insufficient wallet balance. Required: {float(total_cost)} ETB, "
                f"Available: {float(org_wallet.available_balance)} ETB"
            )

        saga_id = f"PTAAS-BOUNTY-{uuid_lib.uuid4().hex[:12].upper()}"

        try:
            platform_user = self.db.query(UserModel).filter(UserModel.role == "admin").first()
            if not platform_user:
                platform_user = self.db.query(UserModel).filter(
                    UserModel.role == "finance_officer"
                ).first()
            if not platform_user:
                raise ValueError("Platform wallet user not found")

            wallet_service.debit_wallet(
                owner_id=organization_user_id,
                owner_type="organization",
                amount=total_cost,
                saga_id=saga_id,
                from_reserved=False,
                reference_type="ptaas_bounty_approval",
                reference_id=finding_id,
            )

            wallet_service.credit_wallet(
                owner_id=platform_user.id,
                owner_type="platform",
                amount=total_cost,
                saga_id=saga_id,
                reference_type="ptaas_bounty_approval",
                reference_id=finding_id,
            )
            if not existing_payment:
                payment = payment_service.create_ptaas_bounty_payment(
                    finding_id=finding_id,
                    bounty_amount=bounty_amount,
                    approved_by=approved_by_user_id,
                    commit=False,
                )
            else:
                payment = existing_payment

            payment.status = "approved"
            payment.approved_by = approved_by_user_id
            payment.approved_at = datetime.utcnow()

            finding.bounty_status = "approved"
            finding.bounty_approved_by = approved_by_user_id
            finding.bounty_approved_at = datetime.utcnow()
            finding.status = "CLOSED"

            self.db.commit()
            self.db.refresh(finding)
            payment_service._add_payment_history(
                payment_id=payment.payment_id,
                previous_status="pending",
                new_status="approved",
                changed_by=approved_by_user_id,
                notes="PTaaS bounty approved by organization — finance payout queue",
            )
        except Exception:
            self.db.rollback()
            raise

        self.audit_service.log_action(
            action_type="APPROVE_PTAAS_BOUNTY",
            action_category="finance",
            target_type="PTaaSFinding",
            description="PTaaS bounty approved — sent to finance for payout processing",
            actor_id=approved_by_user_id,
            target_id=finding_id,
            metadata={
                "engagement_id": str(finding.engagement_id),
                "bounty_amount": float(bounty_amount),
                "payment_id": str(payment.payment_id),
            },
        )

        if finding.discovered_by:
            self.notification_service.create_notification(
                user_id=finding.discovered_by,
                notification_type=NotificationType.BOUNTY_APPROVED,
                title="PTaaS bounty approved",
                message=(
                    f"Bounty of {float(bounty_amount):,.2f} ETB approved for '{finding.title}'. "
                    "Finance will process payout."
                ),
                priority=NotificationPriority.HIGH,
                related_entity_type="ptaas_finding",
                related_entity_id=finding.id,
                action_url=f"/researcher/programs/ptaas/{finding.engagement_id}/findings/{finding.id}",
            )

        return finding
