"""
Domain Models Package
Export all SQLAlchemy models
"""
from .user import User, UserRole
from .researcher import Researcher
from .organization import Organization
from .staff import Staff
from .staff_profiles import TriageSpecialist, Administrator, FinancialOfficer
from .kyc import KYCVerification
from .security_log import SecurityEvent, LoginHistory
from .triage import TriageQueue, TriageAssignment, ValidationResult, DuplicateDetection
from .payment_extended import PayoutRequest, Transaction, PaymentGateway, PaymentHistory, PaymentMethod
from .ops import WebhookEndpoint, WebhookLog, EmailTemplate, DataExport, ComplianceReport
from .program import BountyProgram, ProgramScope, RewardTier, ProgramInvitation, ProgramParticipation
from .report import VulnerabilityReport, ReportAttachment, ReportComment, ReportStatusHistory
from .notification import Notification, NotificationType, NotificationPriority
from .analytics import ResearcherMetrics, OrganizationMetrics, PlatformMetrics, AnalyticsReport
from .ptaas import PTaaSEngagement, PTaaSFinding, PTaaSDeliverable, PTaaSProgressUpdate
from .ptaas_dashboard import PTaaSTestingPhase, PTaaSChecklistItem, PTaaSCollaborationUpdate, PTaaSMilestone
from .ptaas_triage import PTaaSFindingTriage, PTaaSExecutiveReport, PTaaSFindingPrioritization
from .ptaas_retest import PTaaSRetestRequest, PTaaSRetestPolicy, PTaaSRetestHistory
from .matching import MatchingConfiguration, ResearcherAssignment
from .code_review import CodeReviewEngagement, CodeReviewFinding
from .integration import (
    ExternalIntegration,
    SyncLog,
    IntegrationFieldMapping,
    IntegrationWebhookEvent,
    IntegrationTemplate,
    IntegrationType,
    IntegrationStatus,
    SyncAction,
    SyncStatus,
    TransformationType
)
from .live_event import (
    LiveHackingEvent,
    EventParticipation,
    EventInvitation,
    EventMetrics,
    EventStatus,
    ParticipationStatus,
    InvitationStatus
)
from .ai_red_teaming import (
    AIRedTeamingEngagement,
    AITestingEnvironment,
    AIVulnerabilityReport,
    AIFindingClassification,
    AISecurityReport,
    AIModelType,
    EngagementStatus,
    AIAttackType,
    AIClassification,
    ReportStatus
)
from .message import Message, Conversation
from .bounty_payment import BountyPayment, Wallet, WalletTransaction
from .subscription import (
    OrganizationSubscription,
    SubscriptionPayment,
    SubscriptionTierPricing,
    SubscriptionTier,
    SubscriptionStatus
)
from .simulation import (
    SimulationChallenge,
    SimulationInstance,
    SimulationProgress,
    SimulationReport,
    SimulationSolution,
    SimulationSolutionComment,
    SimulationSolutionLike,
    SimulationLeaderboard
)

__all__ = [
    # Core user models
    "User", "UserRole",
    "Researcher",
    "Organization",
    "Staff",
    # Staff role profiles (new)
    "TriageSpecialist", "Administrator", "FinancialOfficer",
    # KYC & security (new)
    "KYCVerification",
    "SecurityEvent", "LoginHistory",
    # Triage workflow (new)
    "TriageQueue", "TriageAssignment", "ValidationResult", "DuplicateDetection",
    # Payment completeness (new)
    "PayoutRequest", "Transaction", "PaymentGateway", "PaymentHistory", "PaymentMethod",
    # Ops tables (new)
    "WebhookEndpoint", "WebhookLog", "EmailTemplate", "DataExport", "ComplianceReport",
    # Bug bounty core
    "BountyProgram", "ProgramScope", "RewardTier", "ProgramInvitation", "ProgramParticipation",
    "VulnerabilityReport", "ReportAttachment", "ReportComment", "ReportStatusHistory",
    # Notifications
    "Notification", "NotificationType", "NotificationPriority",
    # Analytics
    "ResearcherMetrics", "OrganizationMetrics", "PlatformMetrics", "AnalyticsReport",
    # PTaaS
    "PTaaSEngagement", "PTaaSFinding", "PTaaSDeliverable", "PTaaSProgressUpdate",
    "PTaaSTestingPhase", "PTaaSChecklistItem", "PTaaSCollaborationUpdate", "PTaaSMilestone",
    "PTaaSFindingTriage", "PTaaSExecutiveReport", "PTaaSFindingPrioritization",
    "PTaaSRetestRequest", "PTaaSRetestPolicy", "PTaaSRetestHistory",
    # Matching
    "MatchingConfiguration", "ResearcherAssignment",
    # Code review
    "CodeReviewEngagement", "CodeReviewFinding",
    # Integrations
    "ExternalIntegration", "SyncLog", "IntegrationFieldMapping", "IntegrationWebhookEvent",
    "IntegrationTemplate", "IntegrationType", "IntegrationStatus",
    "SyncAction", "SyncStatus", "TransformationType",
    # Live events
    "LiveHackingEvent", "EventParticipation", "EventInvitation",
    "EventMetrics", "EventStatus", "ParticipationStatus", "InvitationStatus",
    # AI red teaming
    "AIRedTeamingEngagement", "AITestingEnvironment", "AIVulnerabilityReport",
    "AIFindingClassification", "AISecurityReport", "AIModelType",
    "EngagementStatus", "AIAttackType", "AIClassification", "ReportStatus",
    # Messaging
    "Message", "Conversation",
    # Payments
    "BountyPayment", "Wallet", "WalletTransaction",
    # Subscriptions
    "OrganizationSubscription", "SubscriptionPayment", "SubscriptionTierPricing",
    "SubscriptionTier", "SubscriptionStatus",
    # Simulation
    "SimulationChallenge", "SimulationInstance", "SimulationProgress", "SimulationReport",
    "SimulationSolution", "SimulationSolutionComment", "SimulationSolutionLike", "SimulationLeaderboard",
]
