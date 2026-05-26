"""Shared helpers for simulation XP, ranks, and API serialization."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.domain.models.simulation import (
    SimulationChallenge,
    SimulationLeaderboard,
    SimulationReport,
    SimulationSolution,
)
from src.domain.models.user import User, UserRole
from src.core.role_access import role_of
from src.core.config import settings


def dedupe_challenges(challenges: list) -> list:
    """One row per vulnerability_type (keeps newest). Fixes repeated seed runs."""
    by_vuln: dict = {}
    for c in sorted(
        challenges,
        key=lambda x: (x.created_at is not None, x.created_at),
        reverse=True,
    ):
        key = (c.vulnerability_type or c.name or str(c.id)).strip().lower()
        if key not in by_vuln:
            by_vuln[key] = c
    return sorted(
        by_vuln.values(),
        key=lambda x: (x.difficulty_level or "", x.name or ""),
    )


def merged_user_status(vulnerability_type: str, challenges: list, prog_map: dict) -> str:
    """Best status across duplicate DB rows for the same vuln type."""
    statuses = [
        prog_map.get(str(c.id), "not_started")
        for c in challenges
        if (c.vulnerability_type or "").strip().lower()
        == (vulnerability_type or "").strip().lower()
    ]
    if "completed" in statuses:
        return "completed"
    if "in_progress" in statuses:
        return "in_progress"
    return "not_started"


def challenge_lab_path(vulnerability_type: Optional[str]) -> str:
    from src.services.container_service import VULNERABILITY_LAB_PATHS

    return VULNERABILITY_LAB_PATHS.get(vulnerability_type or "", "/")


def labs_hub_url(challenge_id=None) -> str:
    """Single lab menu URL on the Next.js app (port 3000)."""
    base = (settings.FRONTEND_URL or "http://localhost:3000").rstrip("/")
    url = f"{base}/researcher/simulation/labs"
    if challenge_id:
        return f"{url}?focus={challenge_id}"
    return url


def portal_lab_url(challenge_id) -> str:
    return labs_hub_url(challenge_id)


def hints_as_list(challenge: SimulationChallenge) -> List[str]:
    raw = challenge.hints
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return [raw[k] for k in sorted(raw.keys(), key=lambda x: str(x))]
    return []


def hint_cost_for_index(challenge: SimulationChallenge, index: int) -> int:
    costs = challenge.hint_costs or {}
    if isinstance(costs, dict):
        return int(costs.get(str(index), costs.get(index, 0)))
    return 0


def build_hints_preview(
    challenge: SimulationChallenge, unlocked_indices: Optional[List[int]] = None
) -> Tuple[List[Dict[str, Any]], int, int]:
    """Build hint cards with free vs paid tiers for the challenge UI."""
    hint_list = hints_as_list(challenge)
    unlocked = set(unlocked_indices or [])
    free_n = paid_n = 0
    rows: List[Dict[str, Any]] = []

    for i, text in enumerate(hint_list):
        cost = hint_cost_for_index(challenge, i)
        tier = "free" if cost == 0 else "paid"
        if tier == "free":
            free_n += 1
            title = f"Free hint {free_n}"
        else:
            paid_n += 1
            title = f"Paid hint {paid_n}"

        rows.append(
            {
                "index": i,
                "tier": tier,
                "title": title,
                "xp_cost": cost,
                "unlocked": i in unlocked,
                "preview": text if i in unlocked else None,
            }
        )

    return rows, free_n, paid_n


def rank_title_from_xp(xp: int) -> str:
    if xp >= 6000:
        return "Red Team Operator"
    if xp >= 3000:
        return "Elite Hacker"
    if xp >= 1500:
        return "Security Researcher"
    if xp >= 700:
        return "Bug Hunter"
    if xp >= 300:
        return "Explorer"
    if xp >= 100:
        return "Learner"
    return "Newbie"


def can_manage_simulation(user: User) -> bool:
    r = role_of(user)
    return r in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.STAFF,
        UserRole.TRIAGE_SPECIALIST,
    )


def normalize_category_filter(category: Optional[str]) -> Optional[str]:
    """Map UI category slugs to DB values (web, api, ...)."""
    if not category:
        return None
    slug = category.lower().strip()
    mapping = {
        "web_security": "web",
        "web": "web",
        "api_security": "api",
        "api": "api",
        "authentication": "auth",
        "auth": "auth",
        "access_control": "access_control",
        "cloud_security": "cloud",
        "mobile_security": "mobile",
        "recon_&_enumeration": "recon",
        "recon": "recon",
    }
    return mapping.get(slug, slug.replace(" ", "_"))


def serialize_report(r: SimulationReport, include_body: bool = False) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "id": str(r.id),
        "user_id": str(r.user_id),
        "challenge_id": str(r.challenge_id),
        "challenge_name": r.challenge.name if r.challenge else "Unknown",
        "title": r.title,
        "status": r.status,
        "score": r.score or 0,
        "xp_awarded": r.points_awarded or 0,
        "is_correct": r.is_correct,
        "feedback": r.feedback,
        "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
        "validated_at": r.validated_at.isoformat() if r.validated_at else None,
    }
    if include_body:
        data.update({
            "description": r.description,
            "steps_to_reproduce": r.steps_to_reproduce,
            "impact_assessment": r.impact_assessment,
            "suggested_severity": r.suggested_severity,
            "poc": r.proof_of_concept,
            "remediation": r.remediation,
            "researcher_email": r.user.email if r.user else None,
        })
    return data


def serialize_challenge(c: SimulationChallenge, admin: bool = False) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "id": str(c.id),
        "name": c.name,
        "description": c.description,
        "category": c.category,
        "vulnerability_type": c.vulnerability_type,
        "difficulty_level": c.difficulty_level,
        "severity": c.severity,
        "points": c.points,
        "estimated_time_minutes": c.estimated_time_minutes,
        "is_active": c.is_active,
        "is_published": c.is_published,
    }
    if admin:
        data.update({
            "docker_image": c.docker_image,
            "exposed_port": c.exposed_port,
            "tutorial_video_url": c.tutorial_video_url,
            "documentation": c.documentation,
            "external_resources": c.external_resources,
            "hints": c.hints,
            "hint_costs": c.hint_costs,
            "official_solution": c.official_solution,
            "expected_vulnerability_type": c.expected_vulnerability_type,
            "expected_severity": c.expected_severity,
            "validation_keywords": c.validation_keywords,
            "total_attempts": c.total_attempts,
            "total_completions": c.total_completions,
        })
    return data


def serialize_solution(s: SimulationSolution, include_content: bool = True) -> Dict[str, Any]:
    return {
        "id": str(s.id),
        "challenge_id": str(s.challenge_id),
        "challenge_name": s.challenge.name if s.challenge else None,
        "title": s.title,
        "content": s.content if include_content else None,
        "video_url": s.video_url,
        "author": s.user.email if s.user else "Unknown",
        "is_approved": s.is_approved,
        "likes_count": s.likes_count,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def serialize_leaderboard_row(entry: SimulationLeaderboard, rank: int) -> Dict[str, Any]:
    xp = entry.total_points or 0
    return {
        "rank": rank,
        "username": entry.user.email if entry.user else "Unknown",
        "rank_title": entry.rank_title or rank_title_from_xp(xp),
        "xp": xp,
        "challenges_completed": entry.challenges_completed or 0,
        "current_streak": entry.current_streak or 0,
    }
