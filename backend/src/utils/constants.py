"""
Platform-wide constants for FindBug Bug Bounty Platform
"""
from enum import Enum


# ─── User Roles ───────────────────────────────────────────────────────────────
class UserRole(str, Enum):
    RESEARCHER = "researcher"
    ORGANIZATION = "organization"
    STAFF = "staff"
    ADMIN = "admin"
    TRIAGE_SPECIALIST = "triage_specialist"
    FINANCIAL_OFFICER = "financial_officer"


USER_ROLES = [role.value for role in UserRole]


# ─── Report / Vulnerability Severity ─────────────────────────────────────────
class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


SEVERITY_LEVELS = [s.value for s in Severity]

# CVSS score ranges per severity
CVSS_RANGES = {
    Severity.CRITICAL: (9.0, 10.0),
    Severity.HIGH: (7.0, 8.9),
    Severity.MEDIUM: (4.0, 6.9),
    Severity.LOW: (0.1, 3.9),
    Severity.INFORMATIONAL: (0.0, 0.0),
}


# ─── Report Status ────────────────────────────────────────────────────────────
class ReportStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    TRIAGED = "triaged"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
    INFORMATIONAL = "informational"
    RESOLVED = "resolved"
    CLOSED = "closed"


REPORT_STATUSES = [s.value for s in ReportStatus]


# ─── Program Status ───────────────────────────────────────────────────────────
class ProgramStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ProgramType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"


# ─── Payment / Payout ────────────────────────────────────────────────────────
class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CHAPA = "chapa"
    TELEBIRR = "telebirr"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


PAYMENT_METHODS = [m.value for m in PaymentMethod]


# ─── KYC Status ──────────────────────────────────────────────────────────────
class KYCStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


# ─── Notification ─────────────────────────────────────────────────────────────
class NotificationChannel(str, Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    SMS = "sms"
    WEBHOOK = "webhook"


class NotificationType(str, Enum):
    REPORT_SUBMITTED = "report_submitted"
    REPORT_UPDATED = "report_updated"
    BOUNTY_AWARDED = "bounty_awarded"
    PAYOUT_PROCESSED = "payout_processed"
    PROGRAM_UPDATED = "program_updated"
    SYSTEM = "system"
    SECURITY_ALERT = "security_alert"


# ─── VRT (Vulnerability Rating Taxonomy) ──────────────────────────────────────
class VRTCategory(str, Enum):
    SERVER_SIDE_INJECTION = "server_side_injection"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA = "sensitive_data_exposure"
    XXE = "xml_external_entities"
    BROKEN_ACCESS = "broken_access_control"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    XSS = "cross_site_scripting"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    KNOWN_VULNERABILITIES = "using_components_with_known_vulnerabilities"
    INSUFFICIENT_LOGGING = "insufficient_logging_and_monitoring"
    CSRF = "cross_site_request_forgery"
    SSRF = "server_side_request_forgery"
    IDOR = "insecure_direct_object_reference"
    OTHER = "other"


# ─── File Upload ──────────────────────────────────────────────────────────────
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain", "application/msword"}
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ─── Pagination ───────────────────────────────────────────────────────────────
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# ─── Token TTLs (seconds) ────────────────────────────────────────────────────
ACCESS_TOKEN_TTL = 3600           # 1 hour
REFRESH_TOKEN_TTL = 86400 * 7    # 7 days
EMAIL_VERIFY_TOKEN_TTL = 86400   # 24 hours
PASSWORD_RESET_TOKEN_TTL = 3600  # 1 hour

# ─── Security ─────────────────────────────────────────────────────────────────
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
MIN_PASSWORD_LENGTH = 8
BCRYPT_ROUNDS = 12

# ─── Celery Queue Names ───────────────────────────────────────────────────────
QUEUE_EMAIL = "email"
QUEUE_NOTIFICATION = "notification"
QUEUE_REPORT = "report"
QUEUE_PAYMENT = "payment"
QUEUE_CLEANUP = "cleanup"
QUEUE_ANALYTICS = "analytics"
QUEUE_MATCHING = "matching"

# ─── Researcher Ranks ─────────────────────────────────────────────────────────
class ResearcherRank(str, Enum):
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    HUNTER = "hunter"
    ELITE = "elite"
    LEGEND = "legend"


RANK_THRESHOLDS = {
    ResearcherRank.NOVICE: 0,
    ResearcherRank.APPRENTICE: 100,
    ResearcherRank.HUNTER: 500,
    ResearcherRank.ELITE: 2000,
    ResearcherRank.LEGEND: 10000,
}

# ─── Platform Commission ──────────────────────────────────────────────────────
PLATFORM_COMMISSION_RATE = 0.15   # 15%
MIN_PAYOUT_AMOUNT = 50.0          # ETB or USD depending on gateway

# ─── PTaaS / Engagement ──────────────────────────────────────────────────────
class EngagementStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PricingModel(str, Enum):
    FIXED = "fixed"
    HOURLY = "hourly"
    RETAINER = "retainer"
