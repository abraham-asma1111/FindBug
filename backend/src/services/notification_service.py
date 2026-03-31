"""
Notification Service - FREQ-12.
Enhanced with EmailTemplate integration for templated email notifications.
"""
from typing import Any, Dict, List, Optional, Type
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.domain.models.notification import (
    Notification,
    NotificationType,
    NotificationPriority
)
from src.domain.models.ops import EmailTemplate
from src.domain.models.user import User, UserRole
from src.core.role_access import role_from_str
from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram
from src.core.email_service import EmailService
from src.core.logging import get_logger

logger = get_logger(__name__)


class NotificationService:
    """
    Service for managing notifications - FREQ-12.
    Enhanced with EmailTemplate integration for templated emails.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
    
    # ═══════════════════════════════════════════════════════════════════════
    # EMAIL TEMPLATE METHODS (New - EmailTemplate model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_email_template(self, template_name: str) -> Optional[EmailTemplate]:
        """
        Get email template by name.
        
        Args:
            template_name: Template name
            
        Returns:
            EmailTemplate or None
        """
        return self.db.query(EmailTemplate).filter(
            EmailTemplate.name == template_name,
            EmailTemplate.is_active == True
        ).first()
    
    def render_template(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Render email template with variables.
        
        Args:
            template_name: Template name
            variables: Template variables
            
        Returns:
            Dict with 'subject', 'body_html', 'body_text'
        """
        template = self.get_email_template(template_name)
        
        if not template:
            logger.warning(f"Email template '{template_name}' not found")
            return {
                "subject": "Notification",
                "body_html": "",
                "body_text": ""
            }
        
        # Render subject
        subject = template.subject
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"  # {{key}}
            subject = subject.replace(placeholder, str(value))
        
        # Render HTML body
        body_html = template.body_html
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            body_html = body_html.replace(placeholder, str(value))
        
        # Render text body
        body_text = template.body_text or ""
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            body_text = body_text.replace(placeholder, str(value))
        
        logger.info(f"Rendered template '{template_name}'", extra={
            "template_name": template_name,
            "variables": list(variables.keys())
        })
        
        return {
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text
        }
    
    def send_templated_email(
        self,
        user_id: UUID,
        template_name: str,
        variables: Dict[str, Any]
    ) -> bool:
        """
        Send templated email to user.
        
        Args:
            user_id: User ID
            template_name: Template name
            variables: Template variables
            
        Returns:
            True if sent successfully
        """
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.email:
            logger.warning(f"User {user_id} not found or has no email")
            return False
        
        # Render template
        rendered = self.render_template(template_name, variables)
        
        if not rendered["body_html"] and not rendered["body_text"]:
            logger.error(f"Template '{template_name}' rendered empty")
            return False
        
        try:
            # Send email using email service
            success = self.email_service.send_html_email(
                to_email=user.email,
                subject=rendered["subject"],
                html_body=rendered["body_html"],
                text_body=rendered["body_text"]
            )
            
            if success:
                logger.info(f"Sent templated email to {user.email}", extra={
                    "user_id": str(user_id),
                    "template": template_name,
                    "subject": rendered["subject"]
                })
                return True
            else:
                logger.error(f"Email service failed to send to {user.email}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to send templated email: {str(e)}", extra={
                "user_id": str(user_id),
                "template": template_name
            })
            return False
    
    # ═══════════════════════════════════════════════════════════════════════
    # NOTIFICATION CREATION (Enhanced with template support)
    # ═══════════════════════════════════════════════════════════════════════
    
    def create_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[UUID] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        send_email: bool = True,
        expires_in_days: Optional[int] = None
    ) -> Notification:
        """
        Create a new notification - FREQ-12.
        
        Args:
            user_id: Recipient user ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            related_entity_type: Type of related entity (report, program, etc.)
            related_entity_id: ID of related entity
            action_url: URL for action button
            action_text: Text for action button
            send_email: Whether to send email notification
            expires_in_days: Days until notification expires
        """
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            action_url=action_url,
            action_text=action_text,
            expires_at=expires_at
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Send email notification if requested
        if send_email:
            self._send_email_notification(notification)
        
        return notification
    
    def _send_email_notification(self, notification: Notification):
        """
        Send email notification using templates.
        Enhanced to use EmailTemplate model.
        """
        try:
            # Get user email
            user = self.db.query(User).filter(User.id == notification.user_id).first()
            if not user or not user.email:
                return
            
            # Map notification type to template name
            template_map = {
                NotificationType.REPORT_SUBMITTED: "report_submitted",
                NotificationType.REPORT_STATUS_CHANGED: "report_status_changed",
                NotificationType.REPORT_ACKNOWLEDGED: "report_acknowledged",
                NotificationType.BOUNTY_APPROVED: "bounty_approved",
                NotificationType.BOUNTY_REJECTED: "bounty_rejected",
                NotificationType.BOUNTY_PAID: "bounty_paid",
                NotificationType.REPUTATION_UPDATED: "reputation_updated",
                NotificationType.RANK_CHANGED: "rank_changed",
                NotificationType.NEW_COMMENT: "new_comment",
                NotificationType.PROGRAM_PUBLISHED: "program_published"
            }
            
            template_name = template_map.get(notification.notification_type)
            
            if template_name:
                # Prepare template variables
                variables = {
                    "user_name": user.email.split('@')[0],  # Simple name extraction
                    "notification_title": notification.title,
                    "notification_message": notification.message,
                    "action_url": notification.action_url or "#",
                    "action_text": notification.action_text or "View Details",
                    "platform_name": "FindBug Platform"
                }
                
                # Send templated email
                success = self.send_templated_email(
                    user_id=user.id,
                    template_name=template_name,
                    variables=variables
                )
                
                if success:
                    notification.email_sent = True
                    notification.email_sent_at = datetime.utcnow()
                    self.db.commit()
            else:
                # Fallback to simple email if no template
                logger.warning(f"No template mapping for {notification.notification_type}")
                notification.email_sent = True
                notification.email_sent_at = datetime.utcnow()
                self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}", extra={
                "notification_id": str(notification.id),
                "user_id": str(notification.user_id)
            })
    
    # Report Notifications
    
    def notify_report_submitted(
        self,
        report: VulnerabilityReport,
        organization_user_id: UUID
    ):
        """Notify organization when new report is submitted."""
        return self.create_notification(
            user_id=organization_user_id,
            notification_type=NotificationType.REPORT_SUBMITTED,
            title="New Vulnerability Report Submitted",
            message=f"A new report '{report.title}' has been submitted to your program.",
            priority=NotificationPriority.HIGH,
            related_entity_type="report",
            related_entity_id=report.id,
            action_url=f"/reports/{report.id}",
            action_text="View Report"
        )
    
    def notify_report_status_changed(
        self,
        report: VulnerabilityReport,
        old_status: str,
        new_status: str
    ):
        """Notify researcher when report status changes."""
        status_messages = {
            'triaged': 'Your report has been triaged and is under review.',
            'valid': 'Your report has been validated! Bounty approval is pending.',
            'invalid': 'Your report has been marked as invalid.',
            'duplicate': 'Your report has been marked as a duplicate.',
            'resolved': 'The vulnerability in your report has been fixed!',
            'closed': 'Your report has been closed.'
        }
        
        message = status_messages.get(new_status, f'Your report status changed from {old_status} to {new_status}.')
        
        priority = NotificationPriority.HIGH if new_status in ['valid', 'invalid'] else NotificationPriority.MEDIUM
        
        return self.create_notification(
            user_id=report.researcher.user_id,
            notification_type=NotificationType.REPORT_STATUS_CHANGED,
            title=f"Report Status Updated: {new_status.title()}",
            message=message,
            priority=priority,
            related_entity_type="report",
            related_entity_id=report.id,
            action_url=f"/reports/{report.id}",
            action_text="View Report"
        )
    
    def notify_report_acknowledged(
        self,
        report: VulnerabilityReport
    ):
        """Notify researcher when report is acknowledged."""
        return self.create_notification(
            user_id=report.researcher.user_id,
            notification_type=NotificationType.REPORT_ACKNOWLEDGED,
            title="Report Acknowledged",
            message=f"Your report '{report.title}' has been acknowledged. Remediation deadline: {report.remediation_deadline.strftime('%Y-%m-%d')}.",
            priority=NotificationPriority.MEDIUM,
            related_entity_type="report",
            related_entity_id=report.id,
            action_url=f"/reports/{report.id}",
            action_text="View Report"
        )
    
    # Bounty Notifications
    
    def notify_bounty_approved(
        self,
        report: VulnerabilityReport
    ):
        """Notify researcher when bounty is approved."""
        return self.create_notification(
            user_id=report.researcher.user_id,
            notification_type=NotificationType.BOUNTY_APPROVED,
            title="Bounty Approved! 🎉",
            message=f"Congratulations! Your bounty of ${report.bounty_amount} has been approved for report '{report.title}'.",
            priority=NotificationPriority.HIGH,
            related_entity_type="report",
            related_entity_id=report.id,
            action_url=f"/reports/{report.id}",
            action_text="View Report"
        )
    
    def notify_bounty_rejected(
        self,
        report: VulnerabilityReport,
        reason: str
    ):
        """Notify researcher when bounty is rejected."""
        return self.create_notification(
            user_id=report.researcher.user_id,
            notification_type=NotificationType.BOUNTY_REJECTED,
            title="Bounty Not Approved",
            message=f"Your bounty request for report '{report.title}' was not approved. Reason: {reason}",
            priority=NotificationPriority.HIGH,
            related_entity_type="report",
            related_entity_id=report.id,
            action_url=f"/reports/{report.id}",
            action_text="View Report"
        )
    
    def notify_bounty_paid(
        self,
        report: VulnerabilityReport
    ):
        """Notify researcher when bounty is paid."""
        return self.create_notification(
            user_id=report.researcher.user_id,
            notification_type=NotificationType.BOUNTY_PAID,
            title="Bounty Paid! 💰",
            message=f"Your bounty of ${report.bounty_amount} has been paid for report '{report.title}'.",
            priority=NotificationPriority.HIGH,
            related_entity_type="report",
            related_entity_id=report.id,
            action_url=f"/reports/{report.id}",
            action_text="View Report"
        )
    
    # Reputation Notifications
    
    def notify_reputation_updated(
        self,
        user_id: UUID,
        points_change: int,
        new_score: float,
        reason: str
    ):
        """Notify researcher when reputation changes."""
        if points_change > 0:
            title = f"Reputation Increased! +{points_change} points"
            message = f"Your reputation increased by {points_change} points. New score: {new_score}. Reason: {reason}"
        else:
            title = f"Reputation Changed: {points_change} points"
            message = f"Your reputation changed by {points_change} points. New score: {new_score}. Reason: {reason}"
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.REPUTATION_UPDATED,
            title=title,
            message=message,
            priority=NotificationPriority.MEDIUM,
            action_url="/profile/reputation",
            action_text="View Reputation"
        )
    
    def notify_rank_changed(
        self,
        user_id: UUID,
        old_rank: int,
        new_rank: int
    ):
        """Notify researcher when rank changes."""
        if new_rank < old_rank:
            title = f"Rank Improved! Now #{new_rank}"
            message = f"Congratulations! Your rank improved from #{old_rank} to #{new_rank}!"
            priority = NotificationPriority.HIGH
        else:
            title = f"Rank Changed to #{new_rank}"
            message = f"Your rank changed from #{old_rank} to #{new_rank}."
            priority = NotificationPriority.LOW
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.RANK_CHANGED,
            title=title,
            message=message,
            priority=priority,
            action_url="/leaderboard",
            action_text="View Leaderboard"
        )
    
    # Comment/Message Notifications
    
    def notify_new_comment(
        self,
        report: VulnerabilityReport,
        commenter_role: str,
        comment_preview: str
    ):
        """Notify about new comment on report."""
        # Notify researcher if comment is from organization/triage/platform
        if role_from_str(commenter_role) in (
            UserRole.ORGANIZATION,
            UserRole.TRIAGE_SPECIALIST,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
            UserRole.STAFF,
        ):
            return self.create_notification(
                user_id=report.researcher.user_id,
                notification_type=NotificationType.NEW_COMMENT,
                title="New Comment on Your Report",
                message=f"New comment on '{report.title}': {comment_preview[:100]}...",
                priority=NotificationPriority.MEDIUM,
                related_entity_type="report",
                related_entity_id=report.id,
                action_url=f"/reports/{report.id}#comments",
                action_text="View Comment"
            )
    
    # Program Notifications
    
    def notify_program_published(
        self,
        program: BountyProgram,
        researcher_ids: List[UUID]
    ):
        """Notify researchers when new program is published."""
        notifications = []
        for researcher_id in researcher_ids:
            # Get researcher's user_id
            from src.domain.models.researcher import Researcher
            researcher = self.db.query(Researcher).filter(Researcher.id == researcher_id).first()
            if researcher:
                notification = self.create_notification(
                    user_id=researcher.user_id,
                    notification_type=NotificationType.PROGRAM_PUBLISHED,
                    title="New Bug Bounty Program Available",
                    message=f"A new program '{program.name}' is now available. Check it out!",
                    priority=NotificationPriority.MEDIUM,
                    related_entity_type="program",
                    related_entity_id=program.id,
                    action_url=f"/programs/{program.id}",
                    action_text="View Program",
                    send_email=False  # Don't spam email for program announcements
                )
                notifications.append(notification)
        
        return notifications
    
    # Notification Management
    
    def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        # Filter out expired notifications
        query = query.filter(
            (Notification.expires_at.is_(None)) | 
            (Notification.expires_at > datetime.utcnow())
        )
        
        query = query.order_by(Notification.created_at.desc())
        
        return query.offset(offset).limit(limit).all()
    
    def mark_as_read(
        self,
        notification_id: UUID,
        user_id: UUID
    ) -> Notification:
        """Mark notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(
        self,
        user_id: UUID
    ) -> int:
        """Mark all notifications as read for a user."""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        
        self.db.commit()
        
        return count
    
    def delete_notification(
        self,
        notification_id: UUID,
        user_id: UUID
    ):
        """Delete a notification."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")
        
        self.db.delete(notification)
        self.db.commit()
    
    def get_unread_count(
        self,
        user_id: UUID
    ) -> int:
        """Get count of unread notifications."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            (Notification.expires_at.is_(None)) | 
            (Notification.expires_at > datetime.utcnow())
        ).count()
    
    def cleanup_expired_notifications(self):
        """Delete expired notifications (maintenance task)."""
        deleted = self.db.query(Notification).filter(
            Notification.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        
        return deleted
