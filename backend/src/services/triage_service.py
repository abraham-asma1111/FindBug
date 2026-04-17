"""Triage Service - FREQ-07, FREQ-08."""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.domain.models.report import (
    VulnerabilityReport,
    ReportStatusHistory
)
from src.domain.models.triage import (
    TriageQueue,
    TriageAssignment,
    ValidationResult,
    DuplicateDetection
)
from src.domain.repositories.report_repository import ReportRepository
from src.core.exceptions import NotFoundException, ForbiddenException
from src.core.logging import get_logger

logger = get_logger(__name__)


class TriageService:
    """Service for triage specialist operations with enhanced queue management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)
        
        # Initialize audit service
        from src.services.audit_service import AuditService
        self.audit_service = AuditService(db)
    
    # ═══════════════════════════════════════════════════════════════════════
    # TRIAGE QUEUE MANAGEMENT (New - using TriageQueue model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def add_to_queue(
        self,
        report_id: UUID,
        priority: int = 5
    ) -> TriageQueue:
        """
        Add report to triage queue.
        
        Args:
            report_id: Report ID
            priority: Priority level (1=highest, 10=lowest)
            
        Returns:
            TriageQueue entry
        """
        # Check if already in queue
        existing = self.db.query(TriageQueue).filter(
            TriageQueue.report_id == report_id
        ).first()
        
        if existing:
            logger.warning("Report already in queue", extra={"report_id": str(report_id)})
            return existing
        
        # Validate priority
        if priority < 1 or priority > 10:
            priority = 5  # Default to medium priority
        
        # Create queue entry
        queue_entry = TriageQueue(
            report_id=report_id,
            priority=priority,
            status="pending"
        )
        
        self.db.add(queue_entry)
        self.db.commit()
        self.db.refresh(queue_entry)
        
        logger.info("Report added to triage queue", extra={
            "report_id": str(report_id),
            "priority": priority
        })
        
        return queue_entry
    
    def get_queue_entries(
        self,
        status: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TriageQueue]:
        """
        Get triage queue entries.
        
        Args:
            status: Filter by status (pending, assigned, in_review, completed, escalated)
            assigned_to: Filter by assignee
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of queue entries
        """
        query = self.db.query(TriageQueue)
        
        if status:
            query = query.filter(TriageQueue.status == status)
        
        if assigned_to:
            query = query.filter(TriageQueue.assigned_to == assigned_to)
        
        # Order by priority (1=highest) then by creation date
        query = query.order_by(
            TriageQueue.priority.asc(),
            TriageQueue.created_at.asc()
        )
        
        return query.offset(offset).limit(limit).all()
    
    def assign_from_queue(
        self,
        queue_id: UUID,
        specialist_id: UUID
    ) -> TriageQueue:
        """
        Assign queue entry to specialist.
        
        Args:
            queue_id: Queue entry ID
            specialist_id: Specialist user ID
            
        Returns:
            Updated queue entry
        """
        queue_entry = self.db.query(TriageQueue).filter(
            TriageQueue.id == queue_id
        ).first()
        
        if not queue_entry:
            raise NotFoundException("Queue entry not found")
        
        if queue_entry.status not in ["pending", "escalated"]:
            raise ValueError(f"Cannot assign queue entry with status: {queue_entry.status}")
        
        # Update queue entry
        queue_entry.assigned_to = specialist_id
        queue_entry.assigned_at = datetime.utcnow()
        queue_entry.status = "assigned"
        
        self.db.commit()
        self.db.refresh(queue_entry)
        
        # Create assignment record
        assignment = TriageAssignment(
            report_id=queue_entry.report_id,
            specialist_id=specialist_id,
            status="pending"
        )
        
        self.db.add(assignment)
        self.db.commit()
        
        logger.info("Queue entry assigned", extra={
            "queue_id": str(queue_id),
            "specialist_id": str(specialist_id)
        })
        
        return queue_entry
    
    def update_queue_status(
        self,
        queue_id: UUID,
        status: str
    ) -> TriageQueue:
        """
        Update queue entry status.
        
        Args:
            queue_id: Queue entry ID
            status: New status
            
        Returns:
            Updated queue entry
        """
        valid_statuses = ["pending", "assigned", "in_review", "completed", "escalated"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        queue_entry = self.db.query(TriageQueue).filter(
            TriageQueue.id == queue_id
        ).first()
        
        if not queue_entry:
            raise NotFoundException("Queue entry not found")
        
        queue_entry.status = status
        self.db.commit()
        self.db.refresh(queue_entry)
        
        return queue_entry
    
    # ═══════════════════════════════════════════════════════════════════════
    # TRIAGE ASSIGNMENT TRACKING (New - using TriageAssignment model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_specialist_assignments(
        self,
        specialist_id: UUID,
        status: Optional[str] = None
    ) -> List[TriageAssignment]:
        """
        Get assignments for a specialist.
        
        Args:
            specialist_id: Specialist user ID
            status: Filter by status (pending, in_progress, completed, reassigned)
            
        Returns:
            List of assignments
        """
        query = self.db.query(TriageAssignment).filter(
            TriageAssignment.specialist_id == specialist_id
        )
        
        if status:
            query = query.filter(TriageAssignment.status == status)
        
        query = query.order_by(TriageAssignment.assigned_at.desc())
        
        return query.all()
    
    def update_assignment_status(
        self,
        assignment_id: UUID,
        status: str
    ) -> TriageAssignment:
        """
        Update assignment status.
        
        Args:
            assignment_id: Assignment ID
            status: New status (pending, in_progress, completed, reassigned)
            
        Returns:
            Updated assignment
        """
        valid_statuses = ["pending", "in_progress", "completed", "reassigned"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        assignment = self.db.query(TriageAssignment).filter(
            TriageAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise NotFoundException("Assignment not found")
        
        assignment.status = status
        
        if status == "completed":
            assignment.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
    
    def reassign_report(
        self,
        report_id: UUID,
        from_specialist_id: UUID,
        to_specialist_id: UUID
    ) -> TriageAssignment:
        """
        Reassign report to different specialist.
        
        Args:
            report_id: Report ID
            from_specialist_id: Current specialist
            to_specialist_id: New specialist
            
        Returns:
            New assignment
        """
        # Mark old assignment as reassigned
        old_assignment = self.db.query(TriageAssignment).filter(
            TriageAssignment.report_id == report_id,
            TriageAssignment.specialist_id == from_specialist_id,
            TriageAssignment.status.in_(["pending", "in_progress"])
        ).first()
        
        if old_assignment:
            old_assignment.status = "reassigned"
            old_assignment.completed_at = datetime.utcnow()
        
        # Create new assignment
        new_assignment = TriageAssignment(
            report_id=report_id,
            specialist_id=to_specialist_id,
            status="pending"
        )
        
        self.db.add(new_assignment)
        self.db.commit()
        self.db.refresh(new_assignment)
        
        # Update queue entry
        queue_entry = self.db.query(TriageQueue).filter(
            TriageQueue.report_id == report_id
        ).first()
        
        if queue_entry:
            queue_entry.assigned_to = to_specialist_id
            queue_entry.assigned_at = datetime.utcnow()
            self.db.commit()
        
        logger.info("Report reassigned", extra={
            "report_id": str(report_id),
            "from_specialist": str(from_specialist_id),
            "to_specialist": str(to_specialist_id)
        })
        
        return new_assignment
    
    # ═══════════════════════════════════════════════════════════════════════
    # VALIDATION RESULTS (New - using ValidationResult model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def create_validation_result(
        self,
        report_id: UUID,
        validator_id: UUID,
        is_valid: bool,
        severity_rating: Optional[str] = None,
        cvss_score: Optional[Decimal] = None,
        recommended_reward: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> ValidationResult:
        """
        Create validation result for report.
        
        Args:
            report_id: Report ID
            validator_id: Validator user ID
            is_valid: Whether report is valid
            severity_rating: Severity (critical, high, medium, low, informational)
            cvss_score: CVSS score (0.0-10.0)
            recommended_reward: Recommended bounty amount
            notes: Validation notes
            
        Returns:
            ValidationResult
        """
        # Validate severity
        if severity_rating and severity_rating not in ["critical", "high", "medium", "low", "informational"]:
            raise ValueError("Invalid severity rating")
        
        # Validate CVSS score
        if cvss_score is not None and (cvss_score < 0 or cvss_score > 10):
            raise ValueError("CVSS score must be between 0.0 and 10.0")
        
        # Create validation result
        validation = ValidationResult(
            report_id=report_id,
            validator_id=validator_id,
            is_valid=is_valid,
            severity_rating=severity_rating,
            cvss_score=cvss_score,
            recommended_reward=recommended_reward,
            notes=notes
        )
        
        self.db.add(validation)
        self.db.commit()
        self.db.refresh(validation)
        
        logger.info("Validation result created", extra={
            "report_id": str(report_id),
            "is_valid": is_valid,
            "severity": severity_rating
        })
        
        return validation
    
    def get_validation_result(self, report_id: UUID) -> Optional[ValidationResult]:
        """
        Get validation result for report.
        
        Args:
            report_id: Report ID
            
        Returns:
            ValidationResult or None
        """
        return self.db.query(ValidationResult).filter(
            ValidationResult.report_id == report_id
        ).first()
    
    # ═══════════════════════════════════════════════════════════════════════
    # DUPLICATE DETECTION (New - using DuplicateDetection model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def detect_duplicate(
        self,
        report_id: UUID,
        original_report_id: UUID,
        similarity_score: Optional[Decimal] = None,
        detection_method: str = "manual"
    ) -> DuplicateDetection:
        """
        Record duplicate detection.
        
        Args:
            report_id: Duplicate report ID
            original_report_id: Original report ID
            similarity_score: Similarity score (0.00-100.00)
            detection_method: Method (manual, automated, hash_match, semantic_similarity)
            
        Returns:
            DuplicateDetection record
        """
        valid_methods = ["manual", "automated", "hash_match", "semantic_similarity"]
        if detection_method not in valid_methods:
            raise ValueError(f"Invalid detection method. Must be one of: {', '.join(valid_methods)}")
        
        # Check if already detected
        existing = self.db.query(DuplicateDetection).filter(
            DuplicateDetection.report_id == report_id
        ).first()
        
        if existing:
            logger.warning("Duplicate already detected", extra={"report_id": str(report_id)})
            return existing
        
        # Create detection record
        detection = DuplicateDetection(
            report_id=report_id,
            duplicate_of=original_report_id,
            similarity_score=similarity_score,
            detection_method=detection_method
        )
        
        self.db.add(detection)
        self.db.commit()
        self.db.refresh(detection)
        
        logger.info("Duplicate detected", extra={
            "report_id": str(report_id),
            "original_id": str(original_report_id),
            "method": detection_method
        })
        
        return detection
    
    def find_potential_duplicates(
        self,
        report_id: UUID,
        threshold: float = 70.0
    ) -> List[Dict]:
        """
        Find potential duplicate reports using similarity analysis.
        
        Args:
            report_id: Report ID to check
            threshold: Similarity threshold percentage
            
        Returns:
            List of potential duplicates with similarity scores
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise NotFoundException("Report not found")
        
        # Find similar reports in same program
        similar_reports = self.find_similar_reports(report_id, limit=20)
        
        # Calculate similarity scores (simplified - in production use NLP)
        potential_duplicates = []
        
        for similar in similar_reports:
            if similar.id == report_id:
                continue
            
            # Simple similarity calculation based on title/description overlap
            # In production, use proper NLP/ML similarity algorithms
            title_similarity = self._calculate_text_similarity(
                report.title.lower(),
                similar.title.lower()
            )
            
            if title_similarity >= threshold:
                potential_duplicates.append({
                    "report_id": str(similar.id),
                    "report_number": similar.report_number,
                    "title": similar.title,
                    "similarity_score": round(title_similarity, 2),
                    "submitted_at": similar.submitted_at.isoformat(),
                    "status": similar.status
                })
        
        return potential_duplicates
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (Jaccard similarity).
        
        In production, use proper NLP libraries like spaCy or sentence-transformers.
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return (len(intersection) / len(union)) * 100
    
    # ═══════════════════════════════════════════════════════════════════════
    # EXISTING METHODS (Enhanced with new models)
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_triage_queue(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        program_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """
        Get triage queue - FREQ-07.
        
        Default: shows new and triaged reports.
        """
        query = self.db.query(VulnerabilityReport)
        
        # Filter by status
        if status:
            query = query.filter(VulnerabilityReport.status == status)
        else:
            # Default: show reports needing attention
            query = query.filter(
                VulnerabilityReport.status.in_(['new', 'triaged'])
            )
        
        # Filter by severity
        if severity:
            query = query.filter(VulnerabilityReport.assigned_severity == severity)
        
        # Filter by program
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        # Order by priority: critical first, then by submission date
        query = query.order_by(
            VulnerabilityReport.suggested_severity.desc(),
            VulnerabilityReport.submitted_at.asc()
        )
        
        return query.offset(offset).limit(limit).all()
    
    def update_triage(
        self,
        report_id: UUID,
        triage_staff_id: Optional[UUID],
        actor_user_id: UUID,
        actor_role: str,
        actor_email: str,
        status: Optional[str] = None,
        assigned_severity: Optional[str] = None,
        cvss_score: Optional[Decimal] = None,
        vrt_category: Optional[str] = None,
        triage_notes: Optional[str] = None,
        is_duplicate: Optional[bool] = None,
        duplicate_of: Optional[UUID] = None
    ) -> VulnerabilityReport:
        """
        Update report triage information - FREQ-07, FREQ-08.
        
        Enhanced with ValidationResult and queue status updates.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        # Track old status for history
        old_status = report.status
        
        # Update status if provided
        if status:
            # Validate status transition
            valid_transitions = {
                'new': ['triaged', 'invalid'],
                'triaged': ['valid', 'invalid', 'duplicate'],
                'valid': ['resolved', 'closed'],
                'invalid': [],  # Terminal state
                'duplicate': [],  # Terminal state
                'resolved': ['closed'],
                'closed': []  # Terminal state
            }
            
            if status not in valid_transitions.get(report.status, []):
                raise ValueError(f"Invalid status transition from {report.status} to {status}")
            
            report.status = status
        
        # Update severity - FREQ-08
        if assigned_severity:
            if assigned_severity not in ['critical', 'high', 'medium', 'low']:
                raise ValueError("Invalid severity. Must be: critical, high, medium, or low")
            report.assigned_severity = assigned_severity
        
        # Update CVSS score
        if cvss_score is not None:
            if cvss_score < 0 or cvss_score > 10:
                raise ValueError("CVSS score must be between 0.0 and 10.0")
            report.cvss_score = cvss_score
        
        # Update VRT category
        if vrt_category:
            report.vrt_category = vrt_category
        
        # Update triage notes
        if triage_notes:
            report.triage_notes = triage_notes
        
        # Mark as duplicate
        if is_duplicate is not None:
            report.is_duplicate = is_duplicate
            if is_duplicate and duplicate_of:
                # Verify original report exists
                original = self.report_repo.get_by_id(duplicate_of)
                if not original:
                    raise ValueError("Original report not found")
                report.duplicate_of = duplicate_of
                report.duplicate_detected_at = datetime.utcnow()
                report.status = 'duplicate'
                
                # Create duplicate detection record
                self.detect_duplicate(
                    report_id=report_id,
                    original_report_id=duplicate_of,
                    detection_method="manual"
                )
        
        # Set triage information
        if triage_staff_id is not None:
            report.triaged_by = triage_staff_id
            report.triaged_at = datetime.utcnow()
            
            # Update assignment status
            assignment = self.db.query(TriageAssignment).filter(
                TriageAssignment.report_id == report_id,
                TriageAssignment.specialist_id == triage_staff_id,
                TriageAssignment.status == "in_progress"
            ).first()
            
            if assignment:
                assignment.status = "completed"
                assignment.completed_at = datetime.utcnow()
        
        report.updated_at = datetime.utcnow()
        report.last_activity_at = datetime.utcnow()
        
        # Save changes
        report = self.report_repo.update(report)
        
        # Create validation result if severity/CVSS provided
        if (assigned_severity or cvss_score) and triage_staff_id:
            existing_validation = self.get_validation_result(report_id)
            if not existing_validation:
                self.create_validation_result(
                    report_id=report_id,
                    validator_id=triage_staff_id,
                    is_valid=(status == "valid" if status else True),
                    severity_rating=assigned_severity,
                    cvss_score=cvss_score,
                    notes=triage_notes
                )
        
        # Update queue status
        queue_entry = self.db.query(TriageQueue).filter(
            TriageQueue.report_id == report_id
        ).first()
        
        if queue_entry:
            if status in ["valid", "invalid", "duplicate", "closed"]:
                queue_entry.status = "completed"
            elif status == "triaged":
                queue_entry.status = "in_review"
            self.db.commit()
        
        # Add to status history if status changed
        if status and status != old_status:
            self.report_repo.add_status_history(
                ReportStatusHistory(
                    report_id=report_id,
                    from_status=old_status,
                    to_status=status,
                    change_reason=triage_notes or f"Status changed by triage specialist",
                    changed_by=actor_user_id,
                )
            )
            
            # Send notification to researcher (FREQ-12)
            from src.services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            notification_service.notify_report_status_changed(
                report=report,
                old_status=old_status,
                new_status=status
            )
            
            # Log audit trail (FREQ-17)
            self.audit_service.log_report_status_changed(
                report_id=report_id,
                old_status=old_status,
                new_status=status,
                changed_by_id=actor_user_id,
                changed_by_role=actor_role,
                changed_by_email=actor_email,
                reason=triage_notes,
            )
        
        return report
    
    def mark_as_duplicate(
        self,
        report_id: UUID,
        original_report_id: UUID,
        triage_staff_id: Optional[UUID],
        actor_user_id: UUID,
        similarity_score: Optional[Decimal] = None
    ) -> VulnerabilityReport:
        """
        Mark report as duplicate - BR-07.
        
        Enhanced with DuplicateDetection model.
        
        Applies business rule:
        - First valid report receives full bounty
        - Duplicate reports receive 50% if submitted within 24 hours
        - Otherwise, no reward
        """
        report = self.report_repo.get_by_id(report_id)
        original = self.report_repo.get_by_id(original_report_id)
        
        if not report:
            raise ValueError("Report not found")
        if not original:
            raise ValueError("Original report not found")
        
        # Check if reports are for the same program
        if report.program_id != original.program_id:
            raise ValueError("Reports must be from the same program")
        
        # Calculate time difference
        time_diff = report.submitted_at - original.submitted_at
        within_24_hours = time_diff.total_seconds() <= 86400  # 24 hours in seconds
        
        # Update report
        report.is_duplicate = True
        report.duplicate_of = original_report_id
        report.duplicate_detected_at = datetime.utcnow()
        report.status = 'duplicate'
        if triage_staff_id is not None:
            report.triaged_by = triage_staff_id
            report.triaged_at = datetime.utcnow()
        
        # Add note about duplicate bounty eligibility
        if within_24_hours:
            report.triage_notes = f"Duplicate of {original.report_number}. Eligible for 50% bounty (submitted within 24 hours)."
        else:
            report.triage_notes = f"Duplicate of {original.report_number}. Not eligible for bounty (submitted after 24 hours)."
        
        report = self.report_repo.update(report)
        
        # Create duplicate detection record
        self.detect_duplicate(
            report_id=report_id,
            original_report_id=original_report_id,
            similarity_score=similarity_score,
            detection_method="manual"
        )
        
        # Update queue status
        queue_entry = self.db.query(TriageQueue).filter(
            TriageQueue.report_id == report_id
        ).first()
        
        if queue_entry:
            queue_entry.status = "completed"
            self.db.commit()
        
        # Add to history
        self.report_repo.add_status_history(
            ReportStatusHistory(
                report_id=report_id,
                from_status=report.status,
                to_status='duplicate',
                change_reason=f"Marked as duplicate of {original.report_number}",
                changed_by=actor_user_id,
            )
        )
        
        logger.info("Report marked as duplicate", extra={
            "report_id": str(report_id),
            "original_id": str(original_report_id),
            "within_24h": within_24_hours
        })
        
        return report
    
    def find_similar_reports(
        self,
        report_id: UUID,
        limit: int = 10
    ) -> List[VulnerabilityReport]:
        """
        Find similar reports for duplicate detection - FREQ-07.
        
        Uses title and description similarity.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        return self.report_repo.search_similar_reports(
            program_id=report.program_id,
            title=report.title,
            description=report.description,
            limit=limit
        )
    
    def acknowledge_report(
        self,
        report_id: UUID,
        acknowledged_by: UUID
    ) -> VulnerabilityReport:
        """
        Acknowledge report - BR-10.
        
        Organizations must acknowledge within 24 hours.
        Sets 90-day remediation deadline.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        if report.acknowledged_at:
            raise ValueError("Report already acknowledged")
        
        now = datetime.utcnow()
        
        # Check if acknowledged within 24 hours
        time_since_submission = now - report.submitted_at
        if time_since_submission.total_seconds() > 86400:  # 24 hours
            # Log warning but still allow acknowledgment
            pass
        
        # Set acknowledgment and deadline
        report.acknowledged_at = now
        report.remediation_deadline = now + timedelta(days=90)  # BR-10: 90 days
        report.updated_at = now
        report.last_activity_at = now
        
        report = self.report_repo.update(report)
        
        # Add to history
        self.report_repo.add_status_history(
            ReportStatusHistory(
                report_id=report_id,
                from_status=report.status,
                to_status=report.status,
                change_reason="Report acknowledged",
                changed_by=acknowledged_by
            )
        )
        
        # Send notification to researcher (FREQ-12)
        from src.services.notification_service import NotificationService
        notification_service = NotificationService(self.db)
        notification_service.notify_report_acknowledged(report=report)
        
        return report
    
    def resolve_report(
        self,
        report_id: UUID,
        resolved_by: UUID,
        resolution_notes: Optional[str] = None
    ) -> VulnerabilityReport:
        """
        Mark report as resolved - FREQ-07.
        
        Indicates vulnerability has been fixed.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        if report.status not in ['valid', 'triaged']:
            raise ValueError("Only valid or triaged reports can be resolved")
        
        old_status = report.status
        
        # Update report
        report.status = 'resolved'
        report.resolved_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        report.last_activity_at = datetime.utcnow()
        
        if resolution_notes:
            report.triage_notes = (report.triage_notes or "") + f"\n\nResolution: {resolution_notes}"
        
        report = self.report_repo.update(report)
        
        # Add to history
        self.report_repo.add_status_history(
            ReportStatusHistory(
                report_id=report_id,
                from_status=old_status,
                to_status='resolved',
                change_reason=resolution_notes or "Vulnerability fixed",
                changed_by=resolved_by
            )
        )
        
        return report
    
    def get_statistics(
        self,
        program_id: Optional[UUID] = None
    ) -> dict:
        """Get triage statistics - FREQ-15."""
        stats = self.report_repo.get_statistics(program_id=program_id)
        
        # Add severity breakdown
        query = self.db.query(VulnerabilityReport)
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        severity_stats = {
            'critical': query.filter(VulnerabilityReport.assigned_severity == 'critical').count(),
            'high': query.filter(VulnerabilityReport.assigned_severity == 'high').count(),
            'medium': query.filter(VulnerabilityReport.assigned_severity == 'medium').count(),
            'low': query.filter(VulnerabilityReport.assigned_severity == 'low').count(),
        }
        
        stats['by_severity'] = severity_stats
        
        return stats
    
    def get_report_history(
        self,
        report_id: UUID
    ) -> List[ReportStatusHistory]:
        """Get report status history - FREQ-17."""
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        return self.report_repo.get_status_history(report_id)
    
    def get_triage_statistics_enhanced(
        self,
        program_id: Optional[UUID] = None,
        specialist_id: Optional[UUID] = None
    ) -> Dict:
        """
        Get enhanced triage statistics with queue and assignment metrics.
        
        Args:
            program_id: Filter by program (optional)
            specialist_id: Filter by specialist (optional)
            
        Returns:
            Comprehensive statistics dictionary
        """
        stats = self.get_statistics(program_id=program_id)
        
        # Queue statistics
        queue_query = self.db.query(TriageQueue)
        if program_id:
            queue_query = queue_query.join(VulnerabilityReport).filter(
                VulnerabilityReport.program_id == program_id
            )
        
        stats['queue'] = {
            'pending': queue_query.filter(TriageQueue.status == "pending").count(),
            'assigned': queue_query.filter(TriageQueue.status == "assigned").count(),
            'in_review': queue_query.filter(TriageQueue.status == "in_review").count(),
            'completed': queue_query.filter(TriageQueue.status == "completed").count(),
            'escalated': queue_query.filter(TriageQueue.status == "escalated").count(),
            'total': queue_query.count()
        }
        
        # Assignment statistics
        assignment_query = self.db.query(TriageAssignment)
        if specialist_id:
            assignment_query = assignment_query.filter(
                TriageAssignment.specialist_id == specialist_id
            )
        
        stats['assignments'] = {
            'pending': assignment_query.filter(TriageAssignment.status == "pending").count(),
            'in_progress': assignment_query.filter(TriageAssignment.status == "in_progress").count(),
            'completed': assignment_query.filter(TriageAssignment.status == "completed").count(),
            'reassigned': assignment_query.filter(TriageAssignment.status == "reassigned").count(),
            'total': assignment_query.count()
        }
        
        # Validation statistics
        validation_query = self.db.query(ValidationResult)
        if program_id:
            validation_query = validation_query.join(VulnerabilityReport).filter(
                VulnerabilityReport.program_id == program_id
            )
        
        stats['validations'] = {
            'valid': validation_query.filter(ValidationResult.is_valid == True).count(),
            'invalid': validation_query.filter(ValidationResult.is_valid == False).count(),
            'total': validation_query.count()
        }
        
        # Duplicate detection statistics
        duplicate_query = self.db.query(DuplicateDetection)
        if program_id:
            duplicate_query = duplicate_query.join(VulnerabilityReport).filter(
                VulnerabilityReport.program_id == program_id
            )
        
        stats['duplicates'] = {
            'manual': duplicate_query.filter(DuplicateDetection.detection_method == "manual").count(),
            'automated': duplicate_query.filter(DuplicateDetection.detection_method == "automated").count(),
            'hash_match': duplicate_query.filter(DuplicateDetection.detection_method == "hash_match").count(),
            'semantic': duplicate_query.filter(DuplicateDetection.detection_method == "semantic_similarity").count(),
            'total': duplicate_query.count()
        }
        
        return stats

    # ═══════════════════════════════════════════════════════════════════════
    # TRIAGE TEMPLATES METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_templates(
        self,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get triage response templates."""
        # For now, return mock data. In production, create TriageTemplate model
        templates = [
            {
                "id": "1",
                "name": "validation_accepted",
                "title": "Report Validated",
                "content": "Thank you for your submission. We have validated this vulnerability and it has been accepted.",
                "category": "validation",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "2",
                "name": "validation_rejected",
                "title": "Report Rejected",
                "content": "Thank you for your submission. After review, we have determined this does not meet our criteria.",
                "category": "rejection",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "3",
                "name": "duplicate_found",
                "title": "Duplicate Report",
                "content": "This vulnerability has already been reported. Please see the original report for details.",
                "category": "duplicate",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "4",
                "name": "need_more_info",
                "title": "Additional Information Needed",
                "content": "We need more information to validate this report. Please provide additional details.",
                "category": "need_info",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        if is_active is not None:
            templates = [t for t in templates if t["is_active"] == is_active]
        
        return templates[offset:offset + limit]
    
    def create_template(
        self,
        name: str,
        title: str,
        content: str,
        category: str,
        created_by: UUID
    ) -> Dict:
        """Create triage template."""
        # Mock implementation - in production, save to database
        template = {
            "id": str(UUID("00000000-0000-0000-0000-000000000001")),
            "name": name,
            "title": title,
            "content": content,
            "category": category,
            "is_active": True,
            "created_by": str(created_by),
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info("Template created", extra={"name": name, "category": category})
        return template
    
    def get_template(self, template_id: UUID) -> Dict:
        """Get template by ID."""
        # Mock implementation
        templates = self.get_templates()
        for template in templates:
            if template["id"] == str(template_id):
                return template
        
        raise ValueError("Template not found")
    
    def update_template(
        self,
        template_id: UUID,
        name: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict:
        """Update template."""
        # Mock implementation
        template = self.get_template(template_id)
        
        if name:
            template["name"] = name
        if title:
            template["title"] = title
        if content:
            template["content"] = content
        if category:
            template["category"] = category
        if is_active is not None:
            template["is_active"] = is_active
        
        template["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info("Template updated", extra={"template_id": str(template_id)})
        return template
    
    def delete_template(self, template_id: UUID):
        """Delete template."""
        # Mock implementation
        logger.info("Template deleted", extra={"template_id": str(template_id)})
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # TRIAGE RESEARCHERS METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_researchers_with_metrics(
        self,
        search: Optional[str] = None,
        sort_by: str = "reports_count",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get researchers with triage metrics."""
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        
        query = self.db.query(
            Researcher,
            User,
            func.count(VulnerabilityReport.id).label('total_reports'),
            func.sum(func.case((VulnerabilityReport.status == 'valid', 1), else_=0)).label('valid_reports'),
            func.sum(func.case((VulnerabilityReport.status == 'invalid', 1), else_=0)).label('invalid_reports'),
            func.sum(func.case((VulnerabilityReport.is_duplicate == True, 1), else_=0)).label('duplicate_reports')
        ).join(
            User, Researcher.user_id == User.id
        ).outerjoin(
            VulnerabilityReport, VulnerabilityReport.researcher_id == Researcher.id
        ).group_by(Researcher.id, User.id)
        
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        # Sort
        if sort_by == "reports_count":
            query = query.order_by(func.count(VulnerabilityReport.id).desc())
        elif sort_by == "valid_reports":
            query = query.order_by(func.sum(func.case((VulnerabilityReport.status == 'valid', 1), else_=0)).desc())
        elif sort_by == "invalid_reports":
            query = query.order_by(func.sum(func.case((VulnerabilityReport.status == 'invalid', 1), else_=0)).desc())
        
        results = query.offset(offset).limit(limit).all()
        
        researchers = []
        for researcher, user, total, valid, invalid, duplicates in results:
            researchers.append({
                "id": str(researcher.id),
                "user_id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "reputation_score": researcher.reputation_score or 0,
                "total_reports": total or 0,
                "valid_reports": valid or 0,
                "invalid_reports": invalid or 0,
                "duplicate_reports": duplicates or 0,
                "validity_rate": round((valid / total * 100) if total > 0 else 0, 2)
            })
        
        return researchers
    
    def get_researcher_detail(self, researcher_id: UUID) -> Dict:
        """Get researcher triage details."""
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        
        researcher = self.db.query(Researcher).filter(Researcher.id == researcher_id).first()
        if not researcher:
            raise ValueError("Researcher not found")
        
        user = self.db.query(User).filter(User.id == researcher.user_id).first()
        
        # Get report statistics
        reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id
        ).all()
        
        total = len(reports)
        valid = sum(1 for r in reports if r.status == 'valid')
        invalid = sum(1 for r in reports if r.status == 'invalid')
        duplicates = sum(1 for r in reports if r.is_duplicate)
        pending = sum(1 for r in reports if r.status in ['new', 'triaged'])
        
        # Get severity breakdown
        severity_breakdown = {
            'critical': sum(1 for r in reports if r.assigned_severity == 'critical'),
            'high': sum(1 for r in reports if r.assigned_severity == 'high'),
            'medium': sum(1 for r in reports if r.assigned_severity == 'medium'),
            'low': sum(1 for r in reports if r.assigned_severity == 'low')
        }
        
        return {
            "id": str(researcher.id),
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "reputation_score": researcher.reputation_score or 0,
            "rank": researcher.rank,
            "total_reports": total,
            "valid_reports": valid,
            "invalid_reports": invalid,
            "duplicate_reports": duplicates,
            "pending_reports": pending,
            "validity_rate": round((valid / total * 100) if total > 0 else 0, 2),
            "severity_breakdown": severity_breakdown,
            "total_earnings": float(researcher.total_earnings or 0)
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # TRIAGE PROGRAMS METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_programs_with_metrics(
        self,
        search: Optional[str] = None,
        sort_by: str = "pending_count",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get programs with triage metrics."""
        from src.domain.models.program import Program
        
        query = self.db.query(
            Program,
            func.count(VulnerabilityReport.id).label('total_reports'),
            func.sum(func.case((VulnerabilityReport.status.in_(['new', 'triaged']), 1), else_=0)).label('pending_reports'),
            func.sum(func.case((VulnerabilityReport.status == 'valid', 1), else_=0)).label('valid_reports')
        ).outerjoin(
            VulnerabilityReport, VulnerabilityReport.program_id == Program.id
        ).group_by(Program.id)
        
        if search:
            query = query.filter(Program.name.ilike(f"%{search}%"))
        
        # Sort
        if sort_by == "pending_count":
            query = query.order_by(func.sum(func.case((VulnerabilityReport.status.in_(['new', 'triaged']), 1), else_=0)).desc())
        elif sort_by == "total_reports":
            query = query.order_by(func.count(VulnerabilityReport.id).desc())
        
        results = query.offset(offset).limit(limit).all()
        
        programs = []
        for program, total, pending, valid in results:
            programs.append({
                "id": str(program.id),
                "name": program.name,
                "status": program.status,
                "total_reports": total or 0,
                "pending_reports": pending or 0,
                "valid_reports": valid or 0,
                "created_at": program.created_at.isoformat() if program.created_at else None
            })
        
        return programs
    
    def get_program_detail(self, program_id: UUID) -> Dict:
        """Get program triage details."""
        from src.domain.models.program import Program
        
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise ValueError("Program not found")
        
        # Get report statistics
        reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id == program_id
        ).all()
        
        total = len(reports)
        pending = sum(1 for r in reports if r.status in ['new', 'triaged'])
        valid = sum(1 for r in reports if r.status == 'valid')
        invalid = sum(1 for r in reports if r.status == 'invalid')
        duplicates = sum(1 for r in reports if r.is_duplicate)
        resolved = sum(1 for r in reports if r.status == 'resolved')
        
        # Get severity breakdown
        severity_breakdown = {
            'critical': sum(1 for r in reports if r.assigned_severity == 'critical'),
            'high': sum(1 for r in reports if r.assigned_severity == 'high'),
            'medium': sum(1 for r in reports if r.assigned_severity == 'medium'),
            'low': sum(1 for r in reports if r.assigned_severity == 'low')
        }
        
        # Calculate average triage time
        triaged_reports = [r for r in reports if r.triaged_at and r.submitted_at]
        avg_triage_time = None
        if triaged_reports:
            total_time = sum((r.triaged_at - r.submitted_at).total_seconds() for r in triaged_reports)
            avg_triage_time = round(total_time / len(triaged_reports) / 3600, 2)  # in hours
        
        return {
            "id": str(program.id),
            "name": program.name,
            "status": program.status,
            "total_reports": total,
            "pending_reports": pending,
            "valid_reports": valid,
            "invalid_reports": invalid,
            "duplicate_reports": duplicates,
            "resolved_reports": resolved,
            "validity_rate": round((valid / total * 100) if total > 0 else 0, 2),
            "severity_breakdown": severity_breakdown,
            "avg_triage_time_hours": avg_triage_time,
            "created_at": program.created_at.isoformat() if program.created_at else None
        }
