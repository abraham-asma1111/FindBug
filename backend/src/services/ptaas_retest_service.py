"""
PTaaS Retest Service - FREQ-37
Free retesting of fixed vulnerabilities
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.src.domain.models.ptaas_retest import (
    PTaaSRetestRequest, PTaaSRetestPolicy, PTaaSRetestHistory
)
from backend.src.domain.models.ptaas import PTaaSEngagement, PTaaSFinding
from backend.src.services.audit_service import AuditService


class PTaaSRetestService:
    """Service for PTaaS retest operations - FREQ-37"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    # Retest Policy Management
    def create_retest_policy(
        self,
        engagement_id: int,
        policy_data: Dict[str, Any]
    ) -> PTaaSRetestPolicy:
        """
        Create retest policy for engagement - FREQ-37
        Defines eligibility and rules for free retesting
        """
        # Check if policy already exists
        existing_policy = self.db.query(PTaaSRetestPolicy).filter(
            PTaaSRetestPolicy.engagement_id == engagement_id
        ).first()
        
        if existing_policy:
            # Update existing policy
            for key, value in policy_data.items():
                setattr(existing_policy, key, value)
            existing_policy.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_policy)
            return existing_policy
        
        # Create new policy
        policy_dict = {
            'engagement_id': engagement_id,
            **policy_data
        }
        
        policy = PTaaSRetestPolicy(**policy_dict)
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def get_retest_policy(self, engagement_id: int) -> Optional[PTaaSRetestPolicy]:
        """Get retest policy for engagement"""
        return self.db.query(PTaaSRetestPolicy).filter(
            PTaaSRetestPolicy.engagement_id == engagement_id
        ).first()
    
    def get_default_policy(self) -> Dict[str, Any]:
        """Get default retest policy - FREQ-37"""
        return {
            'retest_period_months': 12,
            'max_free_retests_per_finding': 3,
            'eligible_severities': ['Critical', 'High', 'Medium', 'Low'],
            'requires_fix_evidence': True,
            'requires_approval': False,
            'target_turnaround_days': 5,
            'allow_partial_fixes': True,
            'allow_new_findings_during_retest': True,
            'notify_on_request': True,
            'notify_on_completion': True
        }
    
    # Retest Request Management
    def request_retest(
        self,
        finding_id: int,
        requested_by: int,
        request_data: Dict[str, Any]
    ) -> PTaaSRetestRequest:
        """
        Request retest for fixed vulnerability - FREQ-37
        Organizations can request free retesting within eligibility period
        """
        # Get finding and engagement
        finding = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.id == finding_id
        ).first()
        
        if not finding:
            raise ValueError("Finding not found")
        
        # Get retest policy
        policy = self.get_retest_policy(finding.engagement_id)
        if not policy:
            # Create default policy
            policy = self.create_retest_policy(
                finding.engagement_id,
                self.get_default_policy()
            )
        
        # Check eligibility
        eligibility = self.check_retest_eligibility(finding_id, policy)
        
        if not eligibility['is_eligible']:
            raise ValueError(f"Not eligible for retest: {eligibility['reason']}")
        
        # Calculate expiration date
        expiration_date = datetime.utcnow() + timedelta(days=policy.retest_period_months * 30)
        
        # Count existing retests
        existing_retests = self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.finding_id == finding_id
        ).count()
        
        # Create retest request
        request_dict = {
            'finding_id': finding_id,
            'engagement_id': finding.engagement_id,
            'requested_by': requested_by,
            'fix_description': request_data.get('fix_description'),
            'fix_implemented_at': request_data.get('fix_implemented_at'),
            'fix_evidence': request_data.get('fix_evidence'),
            'is_eligible': True,
            'eligibility_expires_at': expiration_date,
            'is_free_retest': existing_retests < policy.max_free_retests_per_finding,
            'retest_count': existing_retests + 1,
            'status': 'APPROVED' if not policy.requires_approval else 'PENDING'
        }
        
        retest_request = PTaaSRetestRequest(**request_dict)
        self.db.add(retest_request)
        self.db.commit()
        self.db.refresh(retest_request)
        
        # Create history record
        self._create_history_record(
            retest_request.id,
            finding_id,
            'REQUESTED',
            requested_by,
            None,
            retest_request.status,
            "Retest requested"
        )
        
        # Audit log
        self.audit_service.log_action(
            user_id=requested_by,
            action="REQUEST_PTAAS_RETEST",
            resource_type="PTaaSRetestRequest",
            resource_id=retest_request.id,
            details={
                "finding_id": finding_id,
                "engagement_id": finding.engagement_id,
                "is_free": retest_request.is_free_retest
            }
        )
        
        return retest_request
    
    def check_retest_eligibility(
        self,
        finding_id: int,
        policy: PTaaSRetestPolicy
    ) -> Dict[str, Any]:
        """
        Check if finding is eligible for retest - FREQ-37
        Validates against policy rules and time limits
        """
        finding = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.id == finding_id
        ).first()
        
        if not finding:
            return {'is_eligible': False, 'reason': 'Finding not found'}
        
        # Check severity eligibility
        if policy.eligible_severities and finding.severity not in policy.eligible_severities:
            return {
                'is_eligible': False,
                'reason': f'Severity {finding.severity} not eligible for retest'
            }
        
        # Check time limit
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == finding.engagement_id
        ).first()
        
        if engagement:
            months_since_end = (datetime.utcnow() - engagement.end_date).days / 30
            if months_since_end > policy.retest_period_months:
                return {
                    'is_eligible': False,
                    'reason': f'Retest period expired ({policy.retest_period_months} months)'
                }
        
        # Check max retests
        existing_retests = self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.finding_id == finding_id
        ).count()
        
        if existing_retests >= policy.max_free_retests_per_finding:
            return {
                'is_eligible': False,
                'reason': f'Maximum free retests reached ({policy.max_free_retests_per_finding})'
            }
        
        return {
            'is_eligible': True,
            'reason': 'Eligible for free retest',
            'retests_remaining': policy.max_free_retests_per_finding - existing_retests,
            'expires_at': engagement.end_date + timedelta(days=policy.retest_period_months * 30) if engagement else None
        }
    
    def approve_retest(
        self,
        retest_id: int,
        approved_by: int
    ) -> PTaaSRetestRequest:
        """Approve retest request"""
        retest = self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.id == retest_id
        ).first()
        
        if not retest:
            raise ValueError("Retest request not found")
        
        old_status = retest.status
        retest.status = 'APPROVED'
        retest.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(retest)
        
        # Create history record
        self._create_history_record(
            retest_id,
            retest.finding_id,
            'APPROVED',
            approved_by,
            old_status,
            'APPROVED',
            "Retest approved"
        )
        
        # Audit log
        self.audit_service.log_action(
            user_id=approved_by,
            action="APPROVE_PTAAS_RETEST",
            resource_type="PTaaSRetestRequest",
            resource_id=retest_id,
            details={"finding_id": retest.finding_id}
        )
        
        return retest
    
    def assign_retest(
        self,
        retest_id: int,
        assigned_to: int,
        assigned_by: int
    ) -> PTaaSRetestRequest:
        """Assign retest to researcher"""
        retest = self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.id == retest_id
        ).first()
        
        if not retest:
            raise ValueError("Retest request not found")
        
        old_status = retest.status
        retest.assigned_to = assigned_to
        retest.assigned_at = datetime.utcnow()
        retest.status = 'IN_PROGRESS'
        retest.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(retest)
        
        # Create history record
        self._create_history_record(
            retest_id,
            retest.finding_id,
            'ASSIGNED',
            assigned_by,
            old_status,
            'IN_PROGRESS',
            f"Assigned to user {assigned_to}"
        )
        
        # Audit log
        self.audit_service.log_action(
            user_id=assigned_by,
            action="ASSIGN_PTAAS_RETEST",
            resource_type="PTaaSRetestRequest",
            resource_id=retest_id,
            details={
                "finding_id": retest.finding_id,
                "assigned_to": assigned_to
            }
        )
        
        return retest
    
    def complete_retest(
        self,
        retest_id: int,
        completed_by: int,
        result_data: Dict[str, Any]
    ) -> PTaaSRetestRequest:
        """
        Complete retest with results - FREQ-37
        Record retest outcome and evidence
        """
        retest = self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.id == retest_id
        ).first()
        
        if not retest:
            raise ValueError("Retest request not found")
        
        old_status = retest.status
        retest.retest_completed_at = datetime.utcnow()
        retest.retest_result = result_data.get('retest_result')
        retest.retest_notes = result_data.get('retest_notes')
        retest.retest_evidence = result_data.get('retest_evidence')
        retest.status = 'COMPLETED'
        retest.updated_at = datetime.utcnow()
        
        if not retest.retest_started_at:
            retest.retest_started_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(retest)
        
        # Create history record
        self._create_history_record(
            retest_id,
            retest.finding_id,
            'COMPLETED',
            completed_by,
            old_status,
            'COMPLETED',
            f"Retest completed with result: {retest.retest_result}"
        )
        
        # Audit log
        self.audit_service.log_action(
            user_id=completed_by,
            action="COMPLETE_PTAAS_RETEST",
            resource_type="PTaaSRetestRequest",
            resource_id=retest_id,
            details={
                "finding_id": retest.finding_id,
                "result": retest.retest_result
            }
        )
        
        return retest
    
    def get_retest_request(self, retest_id: int) -> Optional[PTaaSRetestRequest]:
        """Get retest request by ID"""
        return self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.id == retest_id
        ).first()
    
    def get_finding_retests(self, finding_id: int) -> List[PTaaSRetestRequest]:
        """Get all retest requests for a finding"""
        return self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.finding_id == finding_id
        ).order_by(PTaaSRetestRequest.requested_at.desc()).all()
    
    def get_engagement_retests(self, engagement_id: int) -> List[PTaaSRetestRequest]:
        """Get all retest requests for an engagement"""
        return self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.engagement_id == engagement_id
        ).order_by(PTaaSRetestRequest.requested_at.desc()).all()
    
    def get_pending_retests(self, limit: int = 50) -> List[PTaaSRetestRequest]:
        """Get pending retest requests"""
        return self.db.query(PTaaSRetestRequest).filter(
            PTaaSRetestRequest.status.in_(['PENDING', 'APPROVED'])
        ).order_by(PTaaSRetestRequest.requested_at).limit(limit).all()
    
    def get_retest_statistics(self, engagement_id: int) -> Dict[str, Any]:
        """Get retest statistics for engagement - FREQ-37"""
        retests = self.get_engagement_retests(engagement_id)
        
        stats = {
            'total_requests': len(retests),
            'pending': len([r for r in retests if r.status == 'PENDING']),
            'approved': len([r for r in retests if r.status == 'APPROVED']),
            'in_progress': len([r for r in retests if r.status == 'IN_PROGRESS']),
            'completed': len([r for r in retests if r.status == 'COMPLETED']),
            'rejected': len([r for r in retests if r.status == 'REJECTED']),
            'free_retests': len([r for r in retests if r.is_free_retest]),
            'paid_retests': len([r for r in retests if not r.is_free_retest]),
            'results': {
                'fixed': len([r for r in retests if r.retest_result == 'FIXED']),
                'not_fixed': len([r for r in retests if r.retest_result == 'NOT_FIXED']),
                'partially_fixed': len([r for r in retests if r.retest_result == 'PARTIALLY_FIXED']),
                'new_issue': len([r for r in retests if r.retest_result == 'NEW_ISSUE'])
            }
        }
        
        return stats
    
    # Helper methods
    def _create_history_record(
        self,
        retest_request_id: int,
        finding_id: int,
        activity_type: str,
        activity_by: int,
        previous_status: Optional[str],
        new_status: Optional[str],
        notes: Optional[str]
    ):
        """Create history record for retest activity"""
        history = PTaaSRetestHistory(
            retest_request_id=retest_request_id,
            finding_id=finding_id,
            activity_type=activity_type,
            activity_by=activity_by,
            previous_status=previous_status,
            new_status=new_status,
            notes=notes
        )
        self.db.add(history)
        self.db.commit()
