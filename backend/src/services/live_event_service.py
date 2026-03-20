"""
Live Hacking Events Service
Implements FREQ-43, FREQ-44: Event Management and Real-time Metrics
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.src.domain.models.live_event import (
    LiveHackingEvent,
    EventParticipation,
    EventInvitation,
    EventMetrics,
    EventStatus,
    ParticipationStatus,
    InvitationStatus
)
from backend.src.domain.models.report import VulnerabilityReport

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
        
        if start_time < datetime.utcnow():
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
            now = datetime.utcnow()
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
        event.updated_at = datetime.utcnow()
        
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
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
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
        if invitation.expires_at and invitation.expires_at < datetime.utcnow():
            invitation.status = InvitationStatus.EXPIRED
            self.db.commit()
            raise ValueError("Invitation has expired")
        
        # Update invitation
        invitation.status = InvitationStatus.ACCEPTED if accept else InvitationStatus.DECLINED
        invitation.responded_at = datetime.utcnow()
        
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
            "completed_at": datetime.utcnow()
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
        Link vulnerability report to event
        
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
            
            # Update metrics in real-time
            self._update_submission_metrics(event_id)
            
            logger.info(f"Linked report {report_id} to event {event_id}")
    
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
        
        metrics.last_updated = datetime.utcnow()
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
        
        metrics.last_updated = datetime.utcnow()
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
        
        metrics.last_updated = datetime.utcnow()
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
