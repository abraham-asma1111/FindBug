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
            if finding.affected_component:  # Fixed: was affected_asset
                tested_assets.add(finding.affected_component)
        
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
                    'description': p.description,
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
                {
                    'name': 'Information Gathering', 
                    'order': 1, 
                    'description': 'Collect information about the target application and infrastructure',
                    'checklist': [
                        {'name': 'Search engine discovery', 'category': 'Reconnaissance'},
                        {'name': 'Fingerprint web server', 'category': 'Reconnaissance'},
                        {'name': 'Review webserver metafiles', 'category': 'Reconnaissance'},
                        {'name': 'Enumerate applications', 'category': 'Reconnaissance'},
                        {'name': 'Review webpage comments', 'category': 'Reconnaissance'}
                    ]
                },
                {
                    'name': 'Configuration Management', 
                    'order': 2, 
                    'description': 'Test configuration and deployment management',
                    'checklist': [
                        {'name': 'Test network infrastructure', 'category': 'Configuration'},
                        {'name': 'Test application platform', 'category': 'Configuration'},
                        {'name': 'Test file extensions handling', 'category': 'Configuration'},
                        {'name': 'Review old backup files', 'category': 'Configuration'}
                    ]
                },
                {
                    'name': 'Identity Management', 
                    'order': 3, 
                    'description': 'Test user registration and account provisioning',
                    'checklist': [
                        {'name': 'Test role definitions', 'category': 'Identity'},
                        {'name': 'Test user registration', 'category': 'Identity'},
                        {'name': 'Test account provisioning', 'category': 'Identity'}
                    ]
                },
                {
                    'name': 'Authentication Testing', 
                    'order': 4, 
                    'description': 'Test authentication mechanisms and bypass techniques',
                    'checklist': [
                        {'name': 'Test credentials transport', 'category': 'Authentication'},
                        {'name': 'Test default credentials', 'category': 'Authentication'},
                        {'name': 'Test weak lockout mechanism', 'category': 'Authentication'},
                        {'name': 'Test password policy', 'category': 'Authentication'},
                        {'name': 'Test remember password', 'category': 'Authentication'}
                    ]
                },
                {
                    'name': 'Authorization Testing', 
                    'order': 5, 
                    'description': 'Test authorization and access control mechanisms',
                    'checklist': [
                        {'name': 'Test path traversal', 'category': 'Authorization'},
                        {'name': 'Test privilege escalation', 'category': 'Authorization'},
                        {'name': 'Test insecure direct object references', 'category': 'Authorization'}
                    ]
                },
                {
                    'name': 'Session Management', 
                    'order': 6, 
                    'description': 'Test session handling and token management',
                    'checklist': [
                        {'name': 'Test session management schema', 'category': 'Session'},
                        {'name': 'Test cookies attributes', 'category': 'Session'},
                        {'name': 'Test session fixation', 'category': 'Session'},
                        {'name': 'Test logout functionality', 'category': 'Session'}
                    ]
                },
                {
                    'name': 'Input Validation', 
                    'order': 7, 
                    'description': 'Test input validation and injection vulnerabilities',
                    'checklist': [
                        {'name': 'Test reflected XSS', 'category': 'Input Validation'},
                        {'name': 'Test stored XSS', 'category': 'Input Validation'},
                        {'name': 'Test SQL injection', 'category': 'Input Validation'},
                        {'name': 'Test command injection', 'category': 'Input Validation'},
                        {'name': 'Test XXE injection', 'category': 'Input Validation'}
                    ]
                },
                {
                    'name': 'Error Handling', 
                    'order': 8, 
                    'description': 'Test error handling and information disclosure',
                    'checklist': [
                        {'name': 'Test error codes', 'category': 'Error Handling'},
                        {'name': 'Test stack traces', 'category': 'Error Handling'}
                    ]
                },
                {
                    'name': 'Cryptography', 
                    'order': 9, 
                    'description': 'Test cryptographic implementations and weak encryption',
                    'checklist': [
                        {'name': 'Test weak SSL/TLS ciphers', 'category': 'Cryptography'},
                        {'name': 'Test padding oracle', 'category': 'Cryptography'},
                        {'name': 'Test sensitive data in transit', 'category': 'Cryptography'}
                    ]
                },
                {
                    'name': 'Business Logic', 
                    'order': 10, 
                    'description': 'Test business logic flaws and workflow bypasses',
                    'checklist': [
                        {'name': 'Test business logic data validation', 'category': 'Business Logic'},
                        {'name': 'Test ability to forge requests', 'category': 'Business Logic'},
                        {'name': 'Test integrity checks', 'category': 'Business Logic'}
                    ]
                },
                {
                    'name': 'Client-Side Testing', 
                    'order': 11, 
                    'description': 'Test client-side security controls and DOM-based vulnerabilities',
                    'checklist': [
                        {'name': 'Test DOM-based XSS', 'category': 'Client-Side'},
                        {'name': 'Test JavaScript execution', 'category': 'Client-Side'},
                        {'name': 'Test HTML injection', 'category': 'Client-Side'}
                    ]
                }
            ],
            'PTES': [
                {
                    'name': 'Pre-Engagement', 
                    'order': 1, 
                    'description': 'Define scope, rules of engagement, and objectives',
                    'checklist': [
                        {'name': 'Define scope', 'category': 'Planning'},
                        {'name': 'Define rules of engagement', 'category': 'Planning'},
                        {'name': 'Define objectives', 'category': 'Planning'},
                        {'name': 'Obtain authorization', 'category': 'Planning'}
                    ]
                },
                {
                    'name': 'Intelligence Gathering', 
                    'order': 2, 
                    'description': 'Collect information about the target environment',
                    'checklist': [
                        {'name': 'Passive reconnaissance', 'category': 'Intelligence'},
                        {'name': 'Active reconnaissance', 'category': 'Intelligence'},
                        {'name': 'Network enumeration', 'category': 'Intelligence'},
                        {'name': 'Service enumeration', 'category': 'Intelligence'}
                    ]
                },
                {
                    'name': 'Threat Modeling', 
                    'order': 3, 
                    'description': 'Identify potential attack vectors and threats',
                    'checklist': [
                        {'name': 'Identify assets', 'category': 'Threat Modeling'},
                        {'name': 'Identify threats', 'category': 'Threat Modeling'},
                        {'name': 'Map attack vectors', 'category': 'Threat Modeling'}
                    ]
                },
                {
                    'name': 'Vulnerability Analysis', 
                    'order': 4, 
                    'description': 'Identify and analyze vulnerabilities',
                    'checklist': [
                        {'name': 'Automated scanning', 'category': 'Vulnerability Analysis'},
                        {'name': 'Manual testing', 'category': 'Vulnerability Analysis'},
                        {'name': 'Validate findings', 'category': 'Vulnerability Analysis'}
                    ]
                },
                {
                    'name': 'Exploitation', 
                    'order': 5, 
                    'description': 'Attempt to exploit identified vulnerabilities',
                    'checklist': [
                        {'name': 'Exploit vulnerabilities', 'category': 'Exploitation'},
                        {'name': 'Gain initial access', 'category': 'Exploitation'},
                        {'name': 'Document exploitation', 'category': 'Exploitation'}
                    ]
                },
                {
                    'name': 'Post Exploitation', 
                    'order': 6, 
                    'description': 'Assess impact and maintain access',
                    'checklist': [
                        {'name': 'Privilege escalation', 'category': 'Post Exploitation'},
                        {'name': 'Lateral movement', 'category': 'Post Exploitation'},
                        {'name': 'Data exfiltration', 'category': 'Post Exploitation'},
                        {'name': 'Persistence', 'category': 'Post Exploitation'}
                    ]
                },
                {
                    'name': 'Reporting', 
                    'order': 7, 
                    'description': 'Document findings and provide recommendations',
                    'checklist': [
                        {'name': 'Executive summary', 'category': 'Reporting'},
                        {'name': 'Technical findings', 'category': 'Reporting'},
                        {'name': 'Remediation recommendations', 'category': 'Reporting'},
                        {'name': 'Risk assessment', 'category': 'Reporting'}
                    ]
                }
            ],
            'NIST': [
                {
                    'name': 'Planning', 
                    'order': 1, 
                    'description': 'Plan the penetration test and define objectives',
                    'checklist': [
                        {'name': 'Define test objectives', 'category': 'Planning'},
                        {'name': 'Identify scope', 'category': 'Planning'},
                        {'name': 'Obtain authorization', 'category': 'Planning'}
                    ]
                },
                {
                    'name': 'Discovery', 
                    'order': 2, 
                    'description': 'Discover and enumerate target systems',
                    'checklist': [
                        {'name': 'Network discovery', 'category': 'Discovery'},
                        {'name': 'Service enumeration', 'category': 'Discovery'},
                        {'name': 'Vulnerability identification', 'category': 'Discovery'}
                    ]
                },
                {
                    'name': 'Attack', 
                    'order': 3, 
                    'description': 'Execute attacks and exploit vulnerabilities',
                    'checklist': [
                        {'name': 'Exploit vulnerabilities', 'category': 'Attack'},
                        {'name': 'Gain access', 'category': 'Attack'},
                        {'name': 'Escalate privileges', 'category': 'Attack'}
                    ]
                },
                {
                    'name': 'Reporting', 
                    'order': 4, 
                    'description': 'Report findings and recommendations',
                    'checklist': [
                        {'name': 'Document findings', 'category': 'Reporting'},
                        {'name': 'Provide recommendations', 'category': 'Reporting'},
                        {'name': 'Present results', 'category': 'Reporting'}
                    ]
                }
            ]
        }
        
        templates = phase_templates.get(methodology, phase_templates['PTES'])
        phases = []
        
        for template in templates:
            # Create phase
            phase = self.create_testing_phase({
                'engagement_id': engagement_id,
                'phase_name': template['name'],
                'description': template.get('description', ''),
                'phase_order': template['order'],
                'status': 'NOT_STARTED',
                'progress_percentage': 0
            })
            phases.append(phase)
            
            # Create checklist items for this phase
            for checklist_item in template.get('checklist', []):
                self.create_checklist_item({
                    'phase_id': phase.id,
                    'engagement_id': engagement_id,
                    'item_name': checklist_item['name'],
                    'category': checklist_item['category'],
                    'is_completed': False
                })
        
        return phases
