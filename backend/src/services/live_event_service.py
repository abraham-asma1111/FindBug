"""
Live Hacking Events Service
Implements FREQ-43, FREQ-44: Event Management and Real-time Metrics
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.domain.models.live_event import (
    LiveHackingEvent,
    EventParticipation,
    EventInvitation,
    EventMetrics,
    EventStatus,
    ParticipationStatus,
    InvitationStatus
)
from src.domain.models.report import VulnerabilityReport

logger = logging.getLogger(__name__)


class LiveEventService:
    """Service for managing live hacking events"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_event(
        self,
        organization_id: UUID,
        name: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        max_participants: Optional[int] = None,
        prize_pool: Optional[Decimal] = None,
        scope_description: Optional[str] = None,
        target_assets: Optional[str] = None,
        reward_policy: Optional[str] = None
    ) -> LiveHackingEvent:
        """
        Create new live hacking event
        
        Args:
            organization_id: Organization UUID
            name: Event name
            description: Event description
            start_time: Event start time
            end_time: Event end time
            max_participants: Maximum participants
            prize_pool: Total prize pool
            scope_description: Scope description
            target_assets: Target assets (JSON)
            reward_policy: Reward policy
            
        Returns:
            Created event
        """
        # Validate time window
        if end_time <= start_time:
            raise ValueError("End time must be after start time")
        
        if start_time < datetime.now(timezone.utc):
            raise ValueError("Start time must be in the future")
        
        event = LiveHackingEvent(
            organization_id=organization_id,
            name=name,
            description=description,
            status=EventStatus.DRAFT,
            start_time=start_time,
            end_time=end_time,
            max_participants=max_participants,
            prize_pool=prize_pool,
            scope_description=scope_description,
            target_assets=target_assets,
            reward_policy=reward_policy
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Initialize metrics
        metrics = EventMetrics(event_id=event.id)
        self.db.add(metrics)
        self.db.commit()
        
        logger.info(f"Created live event {event.id} for org {organization_id}")
        return event
    
    def get_event(self, event_id: UUID) -> Optional[LiveHackingEvent]:
        """Get event by ID"""
        return self.db.query(LiveHackingEvent).filter(
            LiveHackingEvent.id == event_id
        ).first()
    
    def list_events(
        self,
        organization_id: Optional[UUID] = None,
        status: Optional[EventStatus] = None,
        active_only: bool = False
    ) -> List[LiveHackingEvent]:
        """List events with filters"""
        query = self.db.query(LiveHackingEvent)
        
        if organization_id:
            query = query.filter(LiveHackingEvent.organization_id == organization_id)
        
        if status:
            query = query.filter(LiveHackingEvent.status == status)
        
        if active_only:
            now = datetime.now(timezone.utc)
            query = query.filter(
                and_(
                    LiveHackingEvent.start_time <= now,
                    LiveHackingEvent.end_time >= now,
                    LiveHackingEvent.status == EventStatus.ACTIVE
                )
            )
        
        return query.order_by(LiveHackingEvent.start_time.desc()).all()
    
    def update_event_status(
        self,
        event_id: UUID,
        status: EventStatus
    ) -> LiveHackingEvent:
        """Update event status"""
        event = self.get_event(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")
        
        # Validate state transitions
        valid_transitions = {
            EventStatus.DRAFT: [EventStatus.SCHEDULED],
            EventStatus.SCHEDULED: [EventStatus.ACTIVE, EventStatus.DRAFT],
            EventStatus.ACTIVE: [EventStatus.CLOSED],
            EventStatus.CLOSED: [EventStatus.ARCHIVED],
            EventStatus.ARCHIVED: []
        }
        
        if status not in valid_transitions.get(event.status, []):
            raise ValueError(
                f"Invalid transition from {event.status} to {status}"
            )
        
        event.status = status
        event.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(event)
        
        logger.info(f"Updated event {event_id} status to {status}")
        return event
    
    def invite_researchers(
        self,
        event_id: UUID,
        researcher_ids: List[UUID],
        expires_in_days: int = 7
    ) -> List[EventInvitation]:
        """
        Invite researchers to event
        
        Args:
            event_id: Event UUID
            researcher_ids: List of researcher UUIDs
            expires_in_days: Invitation expiry in days
            
        Returns:
            List of created invitations
        """
        event = self.get_event(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")
        
        if event.status not in [EventStatus.DRAFT, EventStatus.SCHEDULED]:
            raise ValueError("Can only invite researchers to draft or scheduled events")
        
        invitations = []
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        
        for researcher_id in researcher_ids:
            # Check if already invited
            existing = self.db.query(EventInvitation).filter(
                and_(
                    EventInvitation.event_id == event_id,
                    EventInvitation.researcher_id == researcher_id
                )
            ).first()
            
            if existing:
                logger.warning(f"Researcher {researcher_id} already invited to event {event_id}")
                continue
            
            invitation = EventInvitation(
                event_id=event_id,
                researcher_id=researcher_id,
                status=InvitationStatus.PENDING,
                expires_at=expires_at
            )
            
            self.db.add(invitation)
            invitations.append(invitation)
            
            # Create participation record
            participation = EventParticipation(
                event_id=event_id,
                researcher_id=researcher_id,
                status=ParticipationStatus.INVITED
            )
            self.db.add(participation)
        
        self.db.commit()
        
        # Update metrics
        self._update_invitation_metrics(event_id)
        
        logger.info(f"Invited {len(invitations)} researchers to event {event_id}")
        return invitations
    
    def respond_to_invitation(
        self,
        invitation_id: UUID,
        researcher_id: UUID,
        accept: bool
    ) -> EventInvitation:
        """
        Respond to event invitation
        
        Args:
            invitation_id: Invitation UUID
            researcher_id: Researcher UUID
            accept: True to accept, False to decline
            
        Returns:
            Updated invitation
        """
        invitation = self.db.query(EventInvitation).filter(
            EventInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            raise ValueError(f"Invitation {invitation_id} not found")
        
        if invitation.researcher_id != researcher_id:
            raise ValueError("Invitation does not belong to this researcher")
        
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError(f"Invitation already {invitation.status}")
        
        # Check expiry
        if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
            invitation.status = InvitationStatus.EXPIRED
            self.db.commit()
            raise ValueError("Invitation has expired")
        
        # Update invitation
        invitation.status = InvitationStatus.ACCEPTED if accept else InvitationStatus.DECLINED
        invitation.responded_at = datetime.now(timezone.utc)
        
        # Update participation
        participation = self.db.query(EventParticipation).filter(
            and_(
                EventParticipation.event_id == invitation.event_id,
                EventParticipation.researcher_id == researcher_id
            )
        ).first()
        
        if participation:
            participation.status = ParticipationStatus.ACCEPTED if accept else ParticipationStatus.DECLINED
        
        self.db.commit()
        self.db.refresh(invitation)
        
        # Update metrics
        self._update_invitation_metrics(invitation.event_id)
        
        logger.info(f"Researcher {researcher_id} {'accepted' if accept else 'declined'} invitation {invitation_id}")
        return invitation
    
    def start_event(self, event_id: UUID) -> LiveHackingEvent:
        """Start event (transition to active)"""
        event = self.update_event_status(event_id, EventStatus.ACTIVE)
        
        # Update all accepted participations to active
        self.db.query(EventParticipation).filter(
            and_(
                EventParticipation.event_id == event_id,
                EventParticipation.status == ParticipationStatus.ACCEPTED
            )
        ).update({"status": ParticipationStatus.ACTIVE})
        
        self.db.commit()
        
        # Update metrics
        self._update_participation_metrics(event_id)
        
        logger.info(f"Started event {event_id}")
        return event
    
    def close_event(self, event_id: UUID) -> LiveHackingEvent:
        """Close event (transition to closed)"""
        event = self.update_event_status(event_id, EventStatus.CLOSED)
        
        # Update all active participations to completed
        self.db.query(EventParticipation).filter(
            and_(
                EventParticipation.event_id == event_id,
                EventParticipation.status == ParticipationStatus.ACTIVE
            )
        ).update({
            "status": ParticipationStatus.COMPLETED,
            "completed_at": datetime.now(timezone.utc)
        })
        
        self.db.commit()
        
        # Calculate final rankings
        self._calculate_rankings(event_id)
        
        # Update final metrics
        self._update_all_metrics(event_id)
        
        logger.info(f"Closed event {event_id}")
        return event
    
    def submit_finding(
        self,
        event_id: UUID,
        researcher_id: UUID,
        report_id: UUID
    ):
        """
        Link vulnerability report to event and calculate score
        
        Args:
            event_id: Event UUID
            researcher_id: Researcher UUID
            report_id: Report UUID
        """
        event = self.get_event(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")
        
        if event.status != EventStatus.ACTIVE:
            raise ValueError("Event is not active")
        
        # Check if researcher is participating
        participation = self.db.query(EventParticipation).filter(
            and_(
                EventParticipation.event_id == event_id,
                EventParticipation.researcher_id == researcher_id,
                EventParticipation.status == ParticipationStatus.ACTIVE
            )
        ).first()
        
        if not participation:
            raise ValueError("Researcher is not actively participating in this event")
        
        # Link report to event
        report = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == report_id
        ).first()
        
        if report:
            report.event_id = event_id
            participation.submissions_count += 1
            self.db.commit()
            
            # Calculate and update score
            self.update_researcher_score(
                event_id=event_id,
                researcher_id=researcher_id,
                report_id=report_id,
                severity=report.severity
            )
            
            # Update metrics in real-time
            self._update_submission_metrics(event_id)
            
            logger.info(f"Linked report {report_id} to event {event_id} and updated score")
    
    def get_event_metrics(self, event_id: UUID) -> Optional[EventMetrics]:
        """Get real-time event metrics"""
        return self.db.query(EventMetrics).filter(
            EventMetrics.event_id == event_id
        ).first()
    
    def get_leaderboard(
        self,
        event_id: UUID,
        limit: int = 10
    ) -> List[EventParticipation]:
        """Get event leaderboard"""
        return self.db.query(EventParticipation).filter(
            EventParticipation.event_id == event_id
        ).order_by(
            EventParticipation.rank.asc().nullslast(),
            EventParticipation.score.desc()
        ).limit(limit).all()
    
    def get_researcher_events(
        self,
        researcher_id: UUID,
        status: Optional[ParticipationStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get events for researcher"""
        query = self.db.query(
            LiveHackingEvent, EventParticipation
        ).join(
            EventParticipation,
            EventParticipation.event_id == LiveHackingEvent.id
        ).filter(
            EventParticipation.researcher_id == researcher_id
        )
        
        if status:
            query = query.filter(EventParticipation.status == status)
        
        results = query.all()
        
        return [
            {
                "event": event,
                "participation": participation
            }
            for event, participation in results
        ]
    
    def _update_invitation_metrics(self, event_id: UUID):
        """Update invitation metrics"""
        metrics = self.get_event_metrics(event_id)
        if not metrics:
            return
        
        invitations = self.db.query(EventInvitation).filter(
            EventInvitation.event_id == event_id
        ).all()
        
        metrics.total_invited = len(invitations)
        metrics.total_accepted = sum(
            1 for inv in invitations if inv.status == InvitationStatus.ACCEPTED
        )
        
        if metrics.total_invited > 0:
            metrics.participation_rate = Decimal(
                (metrics.total_accepted / metrics.total_invited) * 100
            ).quantize(Decimal('0.01'))
        
        metrics.last_updated = datetime.now(timezone.utc)
        self.db.commit()
    
    def _update_participation_metrics(self, event_id: UUID):
        """Update participation metrics"""
        metrics = self.get_event_metrics(event_id)
        if not metrics:
            return
        
        participations = self.db.query(EventParticipation).filter(
            EventParticipation.event_id == event_id
        ).all()
        
        metrics.total_active = sum(
            1 for p in participations if p.status == ParticipationStatus.ACTIVE
        )
        
        metrics.last_updated = datetime.now(timezone.utc)
        self.db.commit()
    
    def _update_submission_metrics(self, event_id: UUID):
        """Update submission metrics in real-time"""
        metrics = self.get_event_metrics(event_id)
        if not metrics:
            return
        
        # Get all submissions for this event
        submissions = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.event_id == event_id
        ).all()
        
        metrics.total_submissions = len(submissions)
        
        # Count by status
        metrics.valid_submissions = sum(
            1 for s in submissions if s.status in ['triaged', 'accepted', 'resolved']
        )
        metrics.invalid_submissions = sum(
            1 for s in submissions if s.status in ['rejected', 'invalid']
        )
        metrics.duplicate_submissions = sum(
            1 for s in submissions if s.status == 'duplicate'
        )
        
        # Count by severity
        metrics.critical_bugs = sum(1 for s in submissions if s.severity == 'critical')
        metrics.high_bugs = sum(1 for s in submissions if s.severity == 'high')
        metrics.medium_bugs = sum(1 for s in submissions if s.severity == 'medium')
        metrics.low_bugs = sum(1 for s in submissions if s.severity == 'low')
        metrics.info_bugs = sum(1 for s in submissions if s.severity == 'info')
        
        # Calculate rewards
        total_rewards = sum(
            s.bounty_amount for s in submissions if s.bounty_amount
        )
        metrics.total_rewards_paid = total_rewards
        
        if metrics.valid_submissions > 0:
            metrics.average_reward = total_rewards / metrics.valid_submissions
        
        metrics.last_updated = datetime.now(timezone.utc)
        self.db.commit()
    
    def _update_all_metrics(self, event_id: UUID):
        """Update all metrics"""
        self._update_invitation_metrics(event_id)
        self._update_participation_metrics(event_id)
        self._update_submission_metrics(event_id)
    
    def _calculate_rankings(self, event_id: UUID):
        """Calculate final rankings based on score"""
        participations = self.db.query(EventParticipation).filter(
            EventParticipation.event_id == event_id
        ).order_by(EventParticipation.score.desc()).all()
        
        for rank, participation in enumerate(participations, start=1):
            participation.rank = rank
        
        self.db.commit()
        logger.info(f"Calculated rankings for event {event_id}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # SCORING ALGORITHM
    # ═══════════════════════════════════════════════════════════════════════
    
    def calculate_finding_score(
        self,
        event_id: UUID,
        report_id: UUID,
        severity: str
    ) -> int:
        """
        Calculate score for a finding with bonuses
        
        Base points by severity:
        - Critical: 100 points
        - High: 50 points
        - Medium: 25 points
        - Low: 10 points
        - Info: 5 points
        
        Bonuses:
        - First blood (first to find this vulnerability): +50%
        - Speed bonus (submitted in first hour): +25%
        - Uniqueness bonus (unique vulnerability type): +20%
        - Duplicate: 0 points
        
        Args:
            event_id: Event UUID
            report_id: Report UUID
            severity: Vulnerability severity
            
        Returns:
            Total score with bonuses
        """
        # Base points by severity
        base_points = {
            'critical': 100,
            'high': 50,
            'medium': 25,
            'low': 10,
            'info': 5
        }
        
        score = base_points.get(severity.lower(), 0)
        
        if score == 0:
            return 0
        
        # Get report details
        report = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == report_id
        ).first()
        
        if not report:
            return score
        
        # Get event
        event = self.get_event(event_id)
        if not event:
            return score
        
        # Check for duplicate
        similar_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.event_id == event_id,
            VulnerabilityReport.id != report_id,
            VulnerabilityReport.title.ilike(f"%{report.title}%")
        ).first()
        
        if similar_reports:
            logger.info(f"Duplicate finding detected for report {report_id}")
            return 0  # Duplicate gets 0 points
        
        # First blood bonus (+50%)
        is_first_blood = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.event_id == event_id,
            VulnerabilityReport.severity == severity,
            VulnerabilityReport.created_at < report.created_at
        ).count() == 0
        
        if is_first_blood:
            score = int(score * 1.5)
            logger.info(f"First blood bonus applied to report {report_id}")
        
        # Speed bonus (+25% if submitted in first hour)
        time_since_start = (report.created_at - event.start_time).total_seconds() / 3600
        if time_since_start <= 1:
            score = int(score * 1.25)
            logger.info(f"Speed bonus applied to report {report_id}")
        
        # Uniqueness bonus (+20% if unique vulnerability type)
        vulnerability_type = report.vulnerability_type or "unknown"
        similar_types = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.event_id == event_id,
            VulnerabilityReport.id != report_id,
            VulnerabilityReport.vulnerability_type == vulnerability_type
        ).count()
        
        if similar_types == 0:
            score = int(score * 1.2)
            logger.info(f"Uniqueness bonus applied to report {report_id}")
        
        return score
    
    def update_researcher_score(
        self,
        event_id: UUID,
        researcher_id: UUID,
        report_id: UUID,
        severity: str
    ):
        """
        Update researcher's score after finding submission
        
        Args:
            event_id: Event UUID
            researcher_id: Researcher UUID
            report_id: Report UUID
            severity: Vulnerability severity
        """
        # Calculate score
        score = self.calculate_finding_score(event_id, report_id, severity)
        
        # Update participation
        participation = self.db.query(EventParticipation).filter(
            and_(
                EventParticipation.event_id == event_id,
                EventParticipation.researcher_id == researcher_id
            )
        ).first()
        
        if participation:
            participation.score += score
            
            # Update valid submissions count if not duplicate
            if score > 0:
                participation.valid_submissions_count += 1
            
            self.db.commit()
            
            # Recalculate rankings in real-time
            self._calculate_rankings(event_id)
            
            logger.info(f"Updated score for researcher {researcher_id} in event {event_id}: +{score} points")
    
    # ═══════════════════════════════════════════════════════════════════════
    # PRIZE DISTRIBUTION
    # ═══════════════════════════════════════════════════════════════════════
    
    def distribute_prizes(
        self,
        event_id: UUID,
        approved_by: UUID
    ) -> List[Dict[str, Any]]:
        """
        Distribute prizes to top performers
        
        Prize distribution:
        - 1st place: 40% of prize pool
        - 2nd place: 25% of prize pool
        - 3rd place: 15% of prize pool
        - 4th-10th place: 20% split equally (2.86% each)
        
        Args:
            event_id: Event UUID
            approved_by: User ID who approved distribution
            
        Returns:
            List of prize distributions
        """
        event = self.get_event(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")
        
        if event.status != EventStatus.CLOSED:
            raise ValueError("Can only distribute prizes for closed events")
        
        if not event.prize_pool or event.prize_pool <= 0:
            raise ValueError("Event has no prize pool")
        
        # Get top 10 participants
        top_participants = self.db.query(EventParticipation).filter(
            EventParticipation.event_id == event_id,
            EventParticipation.score > 0
        ).order_by(EventParticipation.score.desc()).limit(10).all()
        
        if not top_participants:
            logger.warning(f"No participants with score > 0 for event {event_id}")
            return []
        
        # Prize distribution percentages
        prize_percentages = {
            1: Decimal("0.40"),  # 40%
            2: Decimal("0.25"),  # 25%
            3: Decimal("0.15"),  # 15%
        }
        
        # 4th-10th split 20% equally
        remaining_percentage = Decimal("0.20")
        remaining_count = min(len(top_participants) - 3, 7)  # Max 7 people (4th-10th)
        if remaining_count > 0:
            per_person_percentage = remaining_percentage / remaining_count
            for rank in range(4, min(11, len(top_participants) + 1)):
                prize_percentages[rank] = per_person_percentage
        
        # Distribute prizes
        distributions = []
        from src.services.payment_service import PaymentService
        payment_service = PaymentService(self.db)
        
        for participation in top_participants:
            rank = participation.rank
            if not rank or rank > 10:
                continue
            
            # Calculate prize amount
            percentage = prize_percentages.get(rank, Decimal("0"))
            prize_amount = event.prize_pool * percentage
            
            # Update participation
            participation.prize_amount = prize_amount
            
            # Create bounty payment (this will handle commission structure)
            # Note: For live events, we create a special bounty payment without a report
            try:
                # Create a dummy report ID or use event_id as reference
                # In production, you might want to create a special payment type for event prizes
                payment = payment_service.create_bounty_payment(
                    report_id=None,  # No specific report for event prizes
                    bounty_amount=prize_amount,
                    approved_by=approved_by
                )
                
                # Link payment to event
                payment.event_id = event_id
                payment.researcher_id = participation.researcher_id
                
                distributions.append({
                    "rank": rank,
                    "researcher_id": participation.researcher_id,
                    "prize_amount": prize_amount,
                    "payment_id": payment.payment_id
                })
                
                logger.info(f"Prize distributed to rank {rank}: {prize_amount} ETB")
                
            except Exception as e:
                logger.error(f"Failed to create payment for rank {rank}: {str(e)}")
                continue
        
        self.db.commit()
        
        logger.info(f"Distributed prizes for event {event_id} to {len(distributions)} participants")
        return distributions
    
    # ═══════════════════════════════════════════════════════════════════════
    # EVENT AUTOMATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def auto_start_scheduled_events(self):
        """
        Auto-start events that have reached their start time
        
        This should be called by a background task (Celery/cron)
        """
        now = datetime.now(timezone.utc)
        
        # Find scheduled events that should start
        events_to_start = self.db.query(LiveHackingEvent).filter(
            and_(
                LiveHackingEvent.status == EventStatus.SCHEDULED,
                LiveHackingEvent.start_time <= now
            )
        ).all()
        
        started_count = 0
        for event in events_to_start:
            try:
                self.start_event(event.id)
                started_count += 1
                logger.info(f"Auto-started event {event.id}")
            except Exception as e:
                logger.error(f"Failed to auto-start event {event.id}: {str(e)}")
        
        return started_count
    
    def auto_close_expired_events(self):
        """
        Auto-close events that have reached their end time
        
        This should be called by a background task (Celery/cron)
        """
        now = datetime.now(timezone.utc)
        
        # Find active events that should close
        events_to_close = self.db.query(LiveHackingEvent).filter(
            and_(
                LiveHackingEvent.status == EventStatus.ACTIVE,
                LiveHackingEvent.end_time <= now
            )
        ).all()
        
        closed_count = 0
        for event in events_to_close:
            try:
                self.close_event(event.id)
                closed_count += 1
                logger.info(f"Auto-closed event {event.id}")
            except Exception as e:
                logger.error(f"Failed to auto-close event {event.id}: {str(e)}")
        
        return closed_count
    
    def send_event_notifications(
        self,
        event_id: UUID,
        notification_type: str,
        message: str
    ):
        """
        Send notifications to event participants
        
        Args:
            event_id: Event UUID
            notification_type: Type of notification (event_start, event_close, etc.)
            message: Notification message
        """
        # Get all active participants
        participations = self.db.query(EventParticipation).filter(
            and_(
                EventParticipation.event_id == event_id,
                EventParticipation.status.in_([
                    ParticipationStatus.ACCEPTED,
                    ParticipationStatus.ACTIVE
                ])
            )
        ).all()
        
        # TODO: Integrate with notification service
        # For now, just log
        logger.info(f"Sending {notification_type} notification to {len(participations)} participants")
        
        return len(participations)
