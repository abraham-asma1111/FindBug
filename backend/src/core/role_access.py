"""
Central role checks aligned with RAD (FREQ-01): Researcher, Organization,
Triage Specialist, Finance Officer, Administrator, and platform Staff.

Use UserRole enum comparisons everywhere — avoid raw strings that never match SQLEnum.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from src.domain.models.user import User, UserRole


def role_of(user: User) -> UserRole:
    """Normalize user.role to UserRole (handles legacy string if any)."""
    r = user.role
    if isinstance(r, UserRole):
        return r
    try:
        return UserRole(str(r))
    except ValueError:
        return UserRole.STAFF


def role_from_str(role: str | UserRole) -> UserRole:
    """Parse API/service string roles to UserRole (invalid values → STAFF)."""
    if isinstance(role, UserRole):
        return role
    try:
        return UserRole(str(role))
    except ValueError:
        return UserRole.STAFF


def is_researcher(user: User) -> bool:
    return role_of(user) == UserRole.RESEARCHER


def is_organization(user: User) -> bool:
    return role_of(user) == UserRole.ORGANIZATION


def is_admin(user: User) -> bool:
    return role_of(user) in (UserRole.ADMIN, UserRole.SUPER_ADMIN)


def is_triage_specialist(user: User) -> bool:
    return role_of(user) == UserRole.TRIAGE_SPECIALIST


def is_finance_officer(user: User) -> bool:
    return role_of(user) == UserRole.FINANCE_OFFICER


def is_platform_staff(user: User) -> bool:
    """Generic platform staff (legacy STAFF role)."""
    return role_of(user) == UserRole.STAFF


def can_access_triage_queue(user: User) -> bool:
    """Triage specialist, platform staff, or admins (RAD: triage + platform staff)."""
    r = role_of(user)
    return r in (
        UserRole.TRIAGE_SPECIALIST,
        UserRole.STAFF,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    )


def can_calculate_or_approve_bounty(user: User) -> bool:
    """Organization, finance officer, or admin (FREQ-10)."""
    r = role_of(user)
    return r in (
        UserRole.ORGANIZATION,
        UserRole.FINANCE_OFFICER,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    )


def can_process_bounty_payout(user: User) -> bool:
    """Finance officer, platform staff (finance ops), or admin."""
    r = role_of(user)
    return r in (
        UserRole.FINANCE_OFFICER,
        UserRole.STAFF,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    )


def can_update_reputation_admin(user: User) -> bool:
    """Admin / triage for manual reputation updates."""
    r = role_of(user)
    return r in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.TRIAGE_SPECIALIST,
        UserRole.STAFF,
    )


def is_ptaas_admin_or_staff(user: User) -> bool:
    """PTaaS / matching admin endpoints (replaces broken \"ADMIN\"/\"STAFF\" string checks)."""
    r = role_of(user)
    return r in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.STAFF,
        UserRole.TRIAGE_SPECIALIST,
        UserRole.FINANCE_OFFICER,
    )


def can_org_or_triage_staff(user: User) -> bool:
    """Acknowledge / resolve / history: organization or platform triage staff."""
    r = role_of(user)
    return r in (
        UserRole.ORGANIZATION,
        UserRole.TRIAGE_SPECIALIST,
        UserRole.STAFF,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    )


def triage_staff_fk_id(user: User) -> Optional[UUID]:
    """
    FK to staff.id for triage actions. Admins without a Staff row return None
    (caller should pass Optional into TriageService).
    """
    if user.staff is not None:
        return user.staff.id
    return None
