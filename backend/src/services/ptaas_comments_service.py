"""
PTaaS Comments Service - Step 9
Handles comments and attachments for findings
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.models.ptaas_dashboard import PTaaSCollaborationUpdate
from src.services.notification_service import NotificationService


class PTaaSCommentsService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
    
    def add_comment(
        self,
        finding_id: UUID,
        user_id: UUID,
        content: str,
        attachments: Optional[List[str]] = None
    ) -> PTaaSCollaborationUpdate:
        """Add comment to finding"""
        # Get engagement_id from finding
        from src.domain.models.ptaas import PTaaSFinding, PTaaSEngagement
        finding = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.id == finding_id
        ).first()
        
        if not finding:
            raise ValueError("Finding not found")
        
        comment = PTaaSCollaborationUpdate(
            engagement_id=finding.engagement_id,
            update_type="COMMENT",
            content=content,
            created_by=user_id,
            related_finding_id=finding_id,
            attachments=attachments or [],
            priority="NORMAL"
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        
        # Send notification to finding owner and assigned users
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == finding.engagement_id
        ).first()
        
        if engagement:
            # Notify organization
            self.notification_service.create_notification(
                user_id=engagement.organization_id,
                notification_type="ptaas_comment",
                title="New Comment on Finding",
                message=f"New comment added to finding: {finding.title}",
                related_id=str(finding_id),
                priority="NORMAL"
            )
            
            # Notify assigned researcher if exists
            if finding.assigned_to and finding.assigned_to != user_id:
                self.notification_service.create_notification(
                    user_id=finding.assigned_to,
                    notification_type="ptaas_comment",
                    title="New Comment on Your Finding",
                    message=f"New comment on finding: {finding.title}",
                    related_id=str(finding_id),
                    priority="NORMAL"
                )
        
        return comment
    
    def get_comments(
        self,
        finding_id: UUID,
        limit: int = 100
    ) -> List[PTaaSCollaborationUpdate]:
        """Get all comments for a finding"""
        comments = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.related_finding_id == finding_id,
            PTaaSCollaborationUpdate.update_type == "COMMENT"
        ).order_by(
            PTaaSCollaborationUpdate.created_at.desc()
        ).limit(limit).all()
        
        return comments
    
    def update_comment(
        self,
        comment_id: UUID,
        content: str,
        user_id: UUID
    ) -> Optional[PTaaSCollaborationUpdate]:
        """Update comment content"""
        comment = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.id == comment_id
        ).first()
        
        if not comment:
            return None
        
        # Verify user owns the comment
        if comment.created_by != user_id:
            raise PermissionError("You can only edit your own comments")
        
        comment.content = content
        self.db.commit()
        self.db.refresh(comment)
        
        return comment
    
    def delete_comment(
        self,
        comment_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a comment"""
        comment = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.id == comment_id
        ).first()
        
        if not comment:
            return False
        
        # Verify user owns the comment
        if comment.created_by != user_id:
            raise PermissionError("You can only delete your own comments")
        
        self.db.delete(comment)
        self.db.commit()
        
        return True
    
    def add_attachment(
        self,
        finding_id: UUID,
        file_url: str,
        file_name: str,
        uploaded_by: UUID
    ) -> PTaaSCollaborationUpdate:
        """Add attachment to finding"""
        from src.domain.models.ptaas import PTaaSFinding
        finding = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.id == finding_id
        ).first()
        
        if not finding:
            raise ValueError("Finding not found")
        
        attachment = PTaaSCollaborationUpdate(
            engagement_id=finding.engagement_id,
            update_type="ATTACHMENT",
            content=f"Uploaded file: {file_name}",
            created_by=uploaded_by,
            related_finding_id=finding_id,
            attachments=[file_url],
            priority="NORMAL"
        )
        
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        
        return attachment
    
    def get_attachments(
        self,
        finding_id: UUID
    ) -> List[PTaaSCollaborationUpdate]:
        """Get all attachments for a finding"""
        attachments = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.related_finding_id == finding_id,
            PTaaSCollaborationUpdate.update_type == "ATTACHMENT"
        ).order_by(
            PTaaSCollaborationUpdate.created_at.desc()
        ).all()
        
        return attachments
    
    def mention_users(
        self,
        comment_id: UUID,
        user_ids: List[UUID]
    ) -> PTaaSCollaborationUpdate:
        """Add user mentions to a comment"""
        comment = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.id == comment_id
        ).first()
        
        if not comment:
            raise ValueError("Comment not found")
        
        comment.mentioned_users = user_ids
        self.db.commit()
        self.db.refresh(comment)
        
        # Send notifications to mentioned users
        for user_id in user_ids:
            if user_id != comment.created_by:  # Don't notify the commenter
                self.notification_service.create_notification(
                    user_id=user_id,
                    notification_type="ptaas_mention",
                    title="You were mentioned in a comment",
                    message=f"You were mentioned in a PTaaS finding comment",
                    related_id=str(comment.related_finding_id),
                    priority="HIGH"
                )
        
        return comment
