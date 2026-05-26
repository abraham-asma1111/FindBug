"""
Simulation Platform Native API - FREQ-23 to FREQ-28
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, func
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import secrets

from src.core.config import settings
from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.domain.models.simulation import (
    SimulationChallenge,
    SimulationInstance,
    SimulationProgress,
    SimulationReport,
    SimulationLeaderboard,
    SimulationSolution,
)
from src.services.simulation_service import SimulationService
from src.services.container_service import ContainerOrchestrationService
from src.services.simulation_helpers import (
    can_manage_simulation,
    challenge_lab_path,
    dedupe_challenges,
    labs_hub_url,
    merged_user_status,
    normalize_category_filter,
    portal_lab_url,
    serialize_report,
    serialize_leaderboard_row,
    serialize_challenge,
    serialize_solution,
    rank_title_from_xp,
    build_hints_preview,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulation", tags=["Simulation Platform"])
_sim_service = SimulationService()
_container_svc = ContainerOrchestrationService()


def _ensure_progress(db: Session, user_id, challenge_id) -> SimulationProgress:
    prog = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == user_id,
        SimulationProgress.challenge_id == challenge_id,
    ).first()
    if not prog:
        prog = SimulationProgress(
            user_id=user_id,
            challenge_id=challenge_id,
            status="in_progress",
            hints_unlocked=[],
        )
        db.add(prog)
        db.commit()
        db.refresh(prog)
    return prog


@router.get("/challenges")
async def get_challenges(
    difficulty: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(SimulationChallenge).filter(
        or_(SimulationChallenge.is_active.is_(True), SimulationChallenge.is_active.is_(None)),
        SimulationChallenge.is_published == True,
    )
    if difficulty:
        query = query.filter(SimulationChallenge.difficulty_level == difficulty)
    cat = normalize_category_filter(category)
    if cat:
        query = query.filter(SimulationChallenge.category == cat)

    all_rows = query.all()
    challenges = dedupe_challenges(all_rows)
    total = len(challenges)
    page = challenges[skip : skip + limit]

    progress = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id
    ).all()
    prog_map = {str(p.challenge_id): p.status for p in progress}

    return {
        "challenges": [
            {
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                "category": c.category,
                "difficulty_level": c.difficulty_level,
                "points": c.points,
                "estimated_time_minutes": c.estimated_time_minutes,
                "user_status": merged_user_status(
                    c.vulnerability_type, all_rows, prog_map
                ),
                "lab_path": challenge_lab_path(c.vulnerability_type),
                "lab_sandbox_path": f"/lab-sandbox{challenge_lab_path(c.vulnerability_type)}",
            }
            for c in page
        ],
        "total": total,
        "labs_hub_url": labs_hub_url(),
        "docker_available": _container_svc.docker_available,
    }


@router.get("/labs")
async def get_labs_menu(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """All lab modules for the shared lab environment page."""
    all_rows = (
        db.query(SimulationChallenge)
        .filter(
            or_(SimulationChallenge.is_active.is_(True), SimulationChallenge.is_active.is_(None)),
            SimulationChallenge.is_published == True,
        )
        .all()
    )
    challenges = dedupe_challenges(all_rows)
    progress = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id
    ).all()
    prog_map = {str(p.challenge_id): p.status for p in progress}

    in_progress_id = next(
        (
            str(c.id)
            for c in challenges
            if merged_user_status(c.vulnerability_type, all_rows, prog_map)
            == "in_progress"
        ),
        None,
    )

    sample = challenges[0] if challenges else None
    lab_ready = bool(sample and _container_svc.try_shared_lab(sample))

    return {
        "labs_hub_url": labs_hub_url(),
        "default_focus_id": in_progress_id or (str(challenges[0].id) if challenges else None),
        "lab_ready": lab_ready,
        "labs": [
            {
                "id": str(c.id),
                "name": c.name,
                "category": c.category,
                "difficulty_level": c.difficulty_level,
                "points": c.points,
                "user_status": merged_user_status(
                    c.vulnerability_type, all_rows, prog_map
                ),
                "lab_path": challenge_lab_path(c.vulnerability_type),
                "lab_sandbox_path": f"/lab-sandbox{challenge_lab_path(c.vulnerability_type)}",
            }
            for c in challenges
        ],
    }


@router.post("/labs/ensure")
async def ensure_labs_running(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify shared academy lab on port 5050 is up."""
    c = (
        db.query(SimulationChallenge)
        .filter(
            or_(SimulationChallenge.is_active.is_(True), SimulationChallenge.is_active.is_(None)),
            SimulationChallenge.is_published == True,
        )
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="No challenges configured")
    if not _container_svc.try_shared_lab(c):
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Lab engine is not running.",
                "fix_steps": [
                    "docker compose -f simulation/docker-compose.yml up -d",
                    "Wait a few seconds, then refresh the lab page.",
                ],
            },
        )
    return {
        "ok": True,
        "labs_hub_url": labs_hub_url(),
        "message": "Lab environment is ready.",
    }


@router.get("/challenges/{challenge_id}")
async def get_challenge_details(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = db.query(SimulationChallenge).filter(SimulationChallenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    prog = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id,
        SimulationProgress.challenge_id == challenge_id,
    ).first()

    active_inst = db.query(SimulationInstance).filter(
        SimulationInstance.user_id == current_user.id,
        SimulationInstance.challenge_id == challenge_id,
        SimulationInstance.status == "running",
    ).first()

    unlocked = list(prog.hints_unlocked or []) if prog else []
    hints_preview, free_hint_count, paid_hint_count = build_hints_preview(c, unlocked)
    lb = db.query(SimulationLeaderboard).filter(
        SimulationLeaderboard.user_id == current_user.id
    ).first()

    solutions = (
        db.query(SimulationSolution)
        .options(joinedload(SimulationSolution.user))
        .filter(
            SimulationSolution.challenge_id == challenge_id,
            SimulationSolution.is_approved == True,
        )
        .order_by(desc(SimulationSolution.likes_count))
        .limit(20)
        .all()
    )

    embed_url = None
    if active_inst:
        embed_url = _container_svc.resolve_embed_url(c, active_inst)
        if embed_url and embed_url != active_inst.unique_url:
            active_inst.unique_url = embed_url
            db.commit()

    return {
        "challenge": {
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "category": c.category,
            "difficulty_level": c.difficulty_level,
            "points": c.points,
            "tutorial_video_url": c.tutorial_video_url,
            "documentation": c.documentation,
            "external_resources": c.external_resources,
            "hint_count": len(hints_preview),
            "free_hint_count": free_hint_count,
            "paid_hint_count": paid_hint_count,
            "hints_preview": hints_preview,
            "vulnerability_type": c.vulnerability_type,
            "lab_path": challenge_lab_path(c.vulnerability_type),
        },
        "user_progress": {
            "status": prog.status if prog else "not_started",
            "hints_used": prog.hints_used if prog else 0,
            "hints_unlocked": unlocked,
        },
        "user_xp": {
            "balance": int(lb.total_points or 0) if lb else 0,
        },
        "community_solutions": [
            {
                "id": str(s.id),
                "title": s.title,
                "author": s.user.email if s.user else "Anonymous",
                "likes_count": s.likes_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in solutions
        ],
        "active_instance": {
            "instance_id": active_inst.instance_id,
            "url": labs_hub_url(challenge_id),
            "embed_url": embed_url,
            "lab_path": challenge_lab_path(c.vulnerability_type),
            "docker": bool(active_inst.container_id),
            "navigation_hint": (
                f"You can access your lab at {labs_hub_url(challenge_id)}"
            ),
        }
        if active_inst and embed_url
        else None,
        "lab_sandbox_path": f"/lab-sandbox{challenge_lab_path(c.vulnerability_type)}",
        "labs_hub_url": labs_hub_url(challenge_id),
        "docker_available": _container_svc.docker_available,
        "shared_lab_port": settings.SIMULATION_LAB_PORT,
    }


@router.post("/challenges/{challenge_id}/start")
async def start_challenge(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = db.query(SimulationChallenge).filter(SimulationChallenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    existing = db.query(SimulationInstance).filter(
        SimulationInstance.user_id == current_user.id,
        SimulationInstance.challenge_id == challenge_id,
        SimulationInstance.status == "running",
    ).first()
    if existing:
        embed = _container_svc.resolve_embed_url(c, existing)
        if not embed:
            existing.status = "stopped"
            existing.stopped_at = datetime.utcnow()
            db.commit()
        else:
            if embed != existing.unique_url:
                existing.unique_url = embed
                db.commit()
            return {
                "message": "Already running",
                "url": labs_hub_url(challenge_id),
                "embed_url": embed,
                "lab_sandbox_path": f"/lab-sandbox{challenge_lab_path(c.vulnerability_type)}",
                "docker": bool(existing.container_id),
                "mode": "academy_lab",
                "navigation_hint": (
                    f"Open {labs_hub_url(challenge_id)} — pick your lab from the menu."
                ),
            }

    try:
        result = await _container_svc.start_challenge_instance(
            db, current_user.id, challenge_id, c
        )
        _ensure_progress(db, current_user.id, c.id)
        mode = result.get("mode", "docker")
        embed_url = result["url"]
        return {
            "message": f"Challenge started ({mode})",
            "instance_id": result["instance_id"],
            "url": labs_hub_url(challenge_id),
            "embed_url": embed_url,
            "lab_sandbox_path": f"/lab-sandbox{challenge_lab_path(c.vulnerability_type)}",
            "port": result.get("port"),
            "status": "running",
            "docker": mode == "docker",
            "reachable": result.get("reachable", True),
            "navigation_hint": (
                f"You can access your lab at {labs_hub_url(challenge_id)}"
            ),
        }
    except Exception as exc:
        logger.exception("Failed to start simulation lab")
        raise HTTPException(
            status_code=503,
            detail={
                "error": str(exc),
                "docker_available": _container_svc.docker_available,
                "image": c.docker_image,
                "fix_steps": [
                    "sudo systemctl start docker   # or open Docker Desktop",
                    f"docker pull {c.docker_image}",
                    "cd ~/Desktop/Final-year-project && docker compose -f simulation/docker-compose.yml up -d",
                    "Then click Start Instance again",
                ],
            },
        )


@router.post("/challenges/{challenge_id}/stop")
async def stop_challenge(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inst = db.query(SimulationInstance).filter(
        SimulationInstance.user_id == current_user.id,
        SimulationInstance.challenge_id == challenge_id,
        SimulationInstance.status == "running",
    ).first()
    if not inst:
        return {"message": "No running instance"}

    if inst.container_id and _container_svc.docker_available:
        try:
            await _container_svc.stop_challenge_instance(db, inst.instance_id)
            return {"message": "Challenge stopped"}
        except Exception:
            pass

    inst.status = "stopped"
    inst.stopped_at = datetime.utcnow()
    db.commit()
    return {"message": "Challenge stopped"}


@router.post("/challenges/{challenge_id}/hints/{hint_index}/unlock")
async def unlock_hint(
    challenge_id: str,
    hint_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = _sim_service.unlock_hint(
            db, current_user.id, challenge_id, hint_index
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/challenges/{challenge_id}/solutions")
async def list_community_solutions(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    solutions = (
        db.query(SimulationSolution)
        .options(joinedload(SimulationSolution.user))
        .filter(SimulationSolution.challenge_id == challenge_id)
        .order_by(desc(SimulationSolution.created_at))
        .all()
    )
    return {
        "solutions": [
            {
                "id": str(s.id),
                "title": s.title,
                "content": s.content if s.is_approved else None,
                "video_url": s.video_url,
                "author": s.user.email if s.user else "Anonymous",
                "is_approved": s.is_approved,
                "likes_count": s.likes_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in solutions
        ]
    }


@router.post("/challenges/{challenge_id}/solutions")
async def post_community_solution(
    challenge_id: str,
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = db.query(SimulationChallenge).filter(SimulationChallenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    solution = SimulationSolution(
        challenge_id=c.id,
        user_id=current_user.id,
        title=body.get("title", "Community writeup"),
        content=body.get("content", ""),
        video_url=body.get("video_url"),
        is_approved=False,
    )
    db.add(solution)
    db.commit()
    db.refresh(solution)
    return {
        "message": "Writeup submitted for moderation",
        "solution_id": str(solution.id),
    }


@router.post("/challenges/{challenge_id}/submit")
async def submit_simulation_report(
    challenge_id: str,
    report_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _sim_service.submit_practice_report(
            db, current_user.id, challenge_id, report_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-reports")
async def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = (
        db.query(SimulationReport)
        .options(joinedload(SimulationReport.challenge))
        .filter(SimulationReport.user_id == current_user.id)
        .order_by(desc(SimulationReport.submitted_at))
        .all()
    )
    return {"reports": [serialize_report(r) for r in reports]}


@router.get("/my-progress")
async def get_my_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    progress = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id
    ).all()
    leaderboard = db.query(SimulationLeaderboard).filter(
        SimulationLeaderboard.user_id == current_user.id
    ).first()

    completed = [p for p in progress if p.status == "completed"]
    xp_earned = int(
        db.query(func.coalesce(func.sum(SimulationReport.points_awarded), 0))
        .filter(
            SimulationReport.user_id == current_user.id,
            SimulationReport.status == "validated",
        )
        .scalar()
        or 0
    )
    xp_balance = int(leaderboard.total_points or 0) if leaderboard else 0
    xp_spent = max(0, xp_earned - xp_balance)
    rank_xp = xp_earned

    return {
        "xp": xp_earned,
        "xp_earned": xp_earned,
        "xp_balance": xp_balance,
        "xp_spent_on_hints": xp_spent,
        "rank_title": rank_title_from_xp(rank_xp),
        "challenges_completed": len(completed),
        "in_progress": len(progress) - len(completed),
        "current_streak": leaderboard.current_streak if leaderboard else 0,
    }


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    top_users = (
        db.query(SimulationLeaderboard)
        .options(joinedload(SimulationLeaderboard.user))
        .order_by(desc(SimulationLeaderboard.total_points))
        .limit(limit)
        .all()
    )
    return {
        "leaderboard": [
            serialize_leaderboard_row(u, idx + 1) for idx, u in enumerate(top_users)
        ]
    }


@router.get("/health")
async def simulation_health():
    return {
        "simulation_platform": "healthy",
        "docker_available": _container_svc.docker_available,
    }


@router.get("/admin/reports")
async def admin_list_reports(
    status: Optional[str] = Query(None, description="submitted, validated, invalid"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_manage_simulation(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")

    query = (
        db.query(SimulationReport)
        .options(
            joinedload(SimulationReport.challenge),
            joinedload(SimulationReport.user),
        )
        .order_by(desc(SimulationReport.submitted_at))
    )
    if status:
        query = query.filter(SimulationReport.status == status)
    else:
        query = query.filter(SimulationReport.status == "submitted")

    reports = query.limit(100).all()
    return {"reports": [serialize_report(r, include_body=True) for r in reports]}


@router.put("/admin/reports/{report_id}/review")
async def admin_review_report(
    report_id: str,
    review_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_manage_simulation(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")

    report = db.query(SimulationReport).filter(SimulationReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    _sim_service.apply_admin_review(
        db,
        report,
        is_valid=review_data.get("is_valid", True),
        score=int(review_data.get("score", 0)),
        xp=int(review_data.get("xp", 0)),
        feedback=review_data.get("feedback", ""),
    )
    return {"message": "Report reviewed successfully"}


@router.get("/admin/challenges")
async def admin_list_challenges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_manage_simulation(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = (
        db.query(SimulationChallenge)
        .order_by(SimulationChallenge.difficulty_level, SimulationChallenge.name)
        .all()
    )
    return {"challenges": [serialize_challenge(c, admin=True) for c in rows]}


@router.post("/admin/challenges")
async def admin_create_challenge(
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_manage_simulation(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")

    name = body.get("name")
    docker_image = body.get("docker_image")
    if not name or not docker_image:
        raise HTTPException(status_code=400, detail="name and docker_image are required")

    c = SimulationChallenge(
        name=name,
        description=body.get("description", ""),
        category=body.get("category", "web"),
        vulnerability_type=body.get("vulnerability_type"),
        difficulty_level=body.get("difficulty_level", "beginner"),
        severity=body.get("severity", "medium"),
        points=int(body.get("points", 100)),
        estimated_time_minutes=int(body.get("estimated_time_minutes", 30)),
        docker_image=docker_image,
        exposed_port=int(body.get("exposed_port", 5050)),
        tutorial_video_url=body.get("tutorial_video_url"),
        documentation=body.get("documentation"),
        external_resources=body.get("external_resources"),
        hints=body.get("hints"),
        hint_costs=body.get("hint_costs"),
        official_solution=body.get("official_solution"),
        expected_vulnerability_type=body.get("expected_vulnerability_type"),
        expected_severity=body.get("expected_severity"),
        validation_keywords=body.get("validation_keywords"),
        is_active=body.get("is_active", True),
        is_published=body.get("is_published", False),
        published_at=datetime.utcnow() if body.get("is_published") else None,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"message": "Challenge created", "challenge": serialize_challenge(c, admin=True)}


@router.put("/admin/challenges/{challenge_id}")
async def admin_update_challenge(
    challenge_id: str,
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_manage_simulation(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")

    c = db.query(SimulationChallenge).filter(SimulationChallenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    for field in (
        "name", "description", "category", "vulnerability_type", "difficulty_level",
        "severity", "docker_image", "tutorial_video_url", "documentation",
        "official_solution", "expected_vulnerability_type", "expected_severity",
    ):
        if field in body:
            setattr(c, field, body[field])

    for field in ("points", "estimated_time_minutes", "exposed_port"):
        if field in body:
            setattr(c, field, int(body[field]))

    for field in ("external_resources", "hints", "hint_costs", "validation_keywords"):
        if field in body:
            setattr(c, field, body[field])

    if "is_active" in body:
        c.is_active = bool(body["is_active"])
    if "is_published" in body:
        was_published = c.is_published
        c.is_published = bool(body["is_published"])
        if c.is_published and not was_published:
            c.published_at = datetime.utcnow()

    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)
    return {"message": "Challenge updated", "challenge": serialize_challenge(c, admin=True)}


@router.get("/admin/solutions")
async def admin_list_solutions(
    pending_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_manage_simulation(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")

    query = (
        db.query(SimulationSolution)
        .options(
            joinedload(SimulationSolution.challenge),
            joinedload(SimulationSolution.user),
        )
        .order_by(desc(SimulationSolution.created_at))
    )
    if pending_only:
        query = query.filter(SimulationSolution.is_approved == False)

    rows = query.limit(100).all()
    return {"solutions": [serialize_solution(s) for s in rows]}


@router.put("/admin/solutions/{solution_id}/approve")
async def admin_approve_solution(
    solution_id: str,
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_manage_simulation(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")

    s = db.query(SimulationSolution).filter(SimulationSolution.id == solution_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solution not found")

    s.is_approved = bool(body.get("is_approved", True))
    db.commit()
    return {"message": "Solution updated", "solution": serialize_solution(s)}
