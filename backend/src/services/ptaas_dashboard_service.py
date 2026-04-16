"""
PTaaS Dashboard Service - FREQ-34
Real-time progress tracking and collaboration
"""
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime
from src.domain.models.ptaas import PTaaSEngagement, PTaaSFinding, PTaaSProgressUpdate
from src.domain.models.ptaas_dashboard import (
    PTaaSTestingPhase, PTaaSChecklistItem, PTaaSCollaborationUpdate, PTaaSMilestone
)


class PTaaSDashboardService:
    """Service for PTaaS dashboard operations - FREQ-34"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_engagement_dashboard(self, engagement_id: UUID) -> Dict:
        """
        Get comprehensive dashboard data for engagement - FREQ-34 + Step 7 Enhancement
        
        Returns:
        - Engagement overview
        - KPI metrics (active researchers, findings by severity, asset coverage)
        - Testing phases with progress
        - Methodology checklists
        - Emerging findings
        - Collaboration updates
        - Team information
        """
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        # Calculate overall progress
        phases = self.db.query(PTaaSTestingPhase).filter(
            PTaaSTestingPhase.engagement_id == engagement_id
        ).order_by(PTaaSTestingPhase.phase_order).all()
        
        if phases:
            overall_progress = sum(p.progress_percentage for p in phases) / len(phases)
        else:
            overall_progress = 0
        
        # Get findings summary
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).all()
        
        findings_summary = {
            'total': len(findings),
            'critical': len([f for f in findings if f.severity == 'Critical']),
            'high': len([f for f in findings if f.severity == 'High']),
            'medium': len([f for f in findings if f.severity == 'Medium']),
            'low': len([f for f in findings if f.severity == 'Low']),
            'info': len([f for f in findings if f.severity == 'Info']),
            'recent': [
                {
                    'id': f.id,
                    'title': f.title,
                    'severity': f.severity,
                    'discovered_at': f.discovered_at.isoformat() if f.discovered_at else None
                }
                for f in sorted(findings, key=lambda x: x.discovered_at or datetime.min, reverse=True)[:5]
            ]
        }
        
        # Get recent collaboration updates
        updates = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.engagement_id == engagement_id
        ).order_by(PTaaSCollaborationUpdate.created_at.desc()).limit(10).all()
        
        # Calculate KPI metrics for Step 7
        # Active researchers count
        assigned_researchers = engagement.assigned_researchers or []
        active_researchers_count = len(assigned_researchers)
        
        # Asset coverage calculation
        in_scope_targets = []
        if engagement.scope and isinstance(engagement.scope, dict):
            in_scope_targets = engagement.scope.get('in_scope_targets', [])
        
        # Get unique assets tested (from findings)
        tested_assets = set()
        for finding in findings:
            if finding.affected_asset:
                tested_assets.add(finding.affected_asset)
        
        total_assets = len(in_scope_targets) if in_scope_targets else 0
        tested_assets_count = len(tested_assets)
        asset_coverage_percentage = (tested_assets_count / total_assets * 100) if total_assets > 0 else 0
        
        # KPI Metrics
        kpi_metrics = {
            'active_researchers': active_researchers_count,
            'total_findings': len(findings),
            'findings_by_severity': {
                'critical': findings_summary['critical'],
                'high': findings_summary['high'],
                'medium': findings_summary['medium'],
                'low': findings_summary['low'],
                'info': findings_summary['info']
            },
            'asset_coverage': {
                'in_scope_assets': in_scope_targets,
                'tested_assets': list(tested_assets),
                'tested': tested_assets_count,
                'total': total_assets,
                'percentage': round(asset_coverage_percentage, 2)
            },
            'overall_progress': round(overall_progress, 2)
        }
        
        return {
            'engagement': {
                'id': engagement.id,
                'name': engagement.name,
                'status': engagement.status,
                'methodology': engagement.testing_methodology,
                'start_date': engagement.start_date.isoformat() if engagement.start_date else None,
                'end_date': engagement.end_date.isoformat() if engagement.end_date else None,
                'duration_days': engagement.duration_days,
                'overall_progress': round(overall_progress, 2)
            },
            'kpi_metrics': kpi_metrics,
            'phases': [
                {
                    'id': p.id,
                    'name': p.phase_name,
                    'order': p.phase_order,
                    'status': p.status,
                    'progress': p.progress_percentage,
                    'started_at': p.started_at.isoformat() if p.started_at else None,
                    'completed_at': p.completed_at.isoformat() if p.completed_at else None
                }
                for p in phases
            ],
            'findings': findings_summary,
            'collaboration': [
                {
                    'id': u.id,
                    'type': u.update_type,
                    'title': u.title,
                    'content': u.content[:200] + '...' if len(u.content) > 200 else u.content,
                    'priority': u.priority,
                    'is_pinned': u.is_pinned,
                    'created_at': u.created_at.isoformat()
                }
                for u in updates
            ],
            'team': {
                'size': engagement.team_size,
                'assigned_researchers': assigned_researchers
            }
        }
    
    # Testing Phase Management
    def create_testing_phase(self, phase_data: Dict) -> PTaaSTestingPhase:
        """Create testing phase - FREQ-34"""
        phase = PTaaSTestingPhase(**phase_data)
        self.db.add(phase)
        self.db.commit()
        self.db.refresh(phase)
        return phase
    
    def update_phase_progress(self, phase_id: UUID, progress: int, status: Optional[str] = None) -> PTaaSTestingPhase:
        """Update phase progress - FREQ-34"""
        phase = self.db.query(PTaaSTestingPhase).filter(PTaaSTestingPhase.id == phase_id).first()
        if phase:
            phase.progress_percentage = progress
            if status:
                phase.status = status
            if progress == 100 and not phase.completed_at:
                phase.completed_at = datetime.utcnow()
            phase.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(phase)
        return phase
    
    # Checklist Management
    def create_checklist_item(self, item_data: Dict) -> PTaaSChecklistItem:
        """Create checklist item - FREQ-34"""
        item = PTaaSChecklistItem(**item_data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def complete_checklist_item(self, item_id: UUID, completed_by: UUID, notes: Optional[str] = None) -> PTaaSChecklistItem:
        """Mark checklist item as complete - FREQ-34"""
        item = self.db.query(PTaaSChecklistItem).filter(PTaaSChecklistItem.id == item_id).first()
        if item:
            item.is_completed = True
            item.completed_by = completed_by
            item.completed_at = datetime.utcnow()
            if notes:
                item.notes = notes
            self.db.commit()
            self.db.refresh(item)
            
            # Update phase progress
            self._update_phase_progress_from_checklist(item.phase_id)
        return item
    
    def _update_phase_progress_from_checklist(self, phase_id: UUID):
        """Auto-update phase progress based on checklist completion"""
        items = self.db.query(PTaaSChecklistItem).filter(
            PTaaSChecklistItem.phase_id == phase_id
        ).all()
        
        if items:
            completed = len([i for i in items if i.is_completed])
            progress = int((completed / len(items)) * 100)
            self.update_phase_progress(phase_id, progress)
    
    def get_phase_checklist(self, phase_id: UUID) -> List[PTaaSChecklistItem]:
        """Get checklist for phase - FREQ-34"""
        return self.db.query(PTaaSChecklistItem).filter(
            PTaaSChecklistItem.phase_id == phase_id
        ).order_by(PTaaSChecklistItem.category, PTaaSChecklistItem.id).all()
    
    # Collaboration Updates
    def add_collaboration_update(self, update_data: Dict) -> PTaaSCollaborationUpdate:
        """Add collaboration update - FREQ-34"""
        update = PTaaSCollaborationUpdate(**update_data)
        self.db.add(update)
        self.db.commit()
        self.db.refresh(update)
        return update
    
    def get_collaboration_updates(
        self, 
        engagement_id: UUID, 
        update_type: Optional[str] = None,
        limit: int = 50
    ) -> List[PTaaSCollaborationUpdate]:
        """Get collaboration updates - FREQ-34"""
        query = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.engagement_id == engagement_id
        )
        
        if update_type:
            query = query.filter(PTaaSCollaborationUpdate.update_type == update_type)
        
        return query.order_by(
            PTaaSCollaborationUpdate.is_pinned.desc(),
            PTaaSCollaborationUpdate.created_at.desc()
        ).limit(limit).all()
    
    def pin_update(self, update_id: UUID) -> PTaaSCollaborationUpdate:
        """Pin collaboration update - FREQ-34"""
        update = self.db.query(PTaaSCollaborationUpdate).filter(
            PTaaSCollaborationUpdate.id == update_id
        ).first()
        if update:
            update.is_pinned = True
            self.db.commit()
            self.db.refresh(update)
        return update
    
    # Milestone Management
    def create_milestone(self, milestone_data: Dict) -> PTaaSMilestone:
        """Create milestone - FREQ-34"""
        milestone = PTaaSMilestone(**milestone_data)
        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)
        return milestone
    
    def complete_milestone(self, milestone_id: UUID) -> PTaaSMilestone:
        """Mark milestone as complete - FREQ-34"""
        milestone = self.db.query(PTaaSMilestone).filter(
            PTaaSMilestone.id == milestone_id
        ).first()
        if milestone:
            milestone.status = 'COMPLETED'
            milestone.completed_date = datetime.utcnow()
            self.db.commit()
            self.db.refresh(milestone)
        return milestone
    
    def get_engagement_milestones(self, engagement_id: UUID) -> List[PTaaSMilestone]:
        """Get milestones for engagement - FREQ-34"""
        return self.db.query(PTaaSMilestone).filter(
            PTaaSMilestone.engagement_id == engagement_id
        ).order_by(PTaaSMilestone.target_date).all()
    
    # Initialize engagement with default phases
    def initialize_engagement_phases(self, engagement_id: UUID, methodology: str) -> List[PTaaSTestingPhase]:
        """Initialize testing phases based on methodology - FREQ-34"""
        phase_templates = {
            'OWASP': [
                {'name': 'Information Gathering', 'order': 1},
                {'name': 'Configuration Management', 'order': 2},
                {'name': 'Identity Management', 'order': 3},
                {'name': 'Authentication Testing', 'order': 4},
                {'name': 'Authorization Testing', 'order': 5},
                {'name': 'Session Management', 'order': 6},
                {'name': 'Input Validation', 'order': 7},
                {'name': 'Error Handling', 'order': 8},
                {'name': 'Cryptography', 'order': 9},
                {'name': 'Business Logic', 'order': 10},
                {'name': 'Client-Side Testing', 'order': 11}
            ],
            'PTES': [
                {'name': 'Pre-Engagement', 'order': 1},
                {'name': 'Intelligence Gathering', 'order': 2},
                {'name': 'Threat Modeling', 'order': 3},
                {'name': 'Vulnerability Analysis', 'order': 4},
                {'name': 'Exploitation', 'order': 5},
                {'name': 'Post Exploitation', 'order': 6},
                {'name': 'Reporting', 'order': 7}
            ],
            'NIST': [
                {'name': 'Planning', 'order': 1},
                {'name': 'Discovery', 'order': 2},
                {'name': 'Attack', 'order': 3},
                {'name': 'Reporting', 'order': 4}
            ]
        }
        
        templates = phase_templates.get(methodology, phase_templates['PTES'])
        phases = []
        
        for template in templates:
            phase = self.create_testing_phase({
                'engagement_id': engagement_id,
                'phase_name': template['name'],
                'phase_order': template['order'],
                'status': 'NOT_STARTED',
                'progress_percentage': 0
            })
            phases.append(phase)
        
        return phases
