"""
VRT Endpoints — Vulnerability Rating Taxonomy browsing and search
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import require_admin
from src.services.vrt_service import VRTService
from src.api.v1.schemas.vrt import VRTCategoryResponse, VRTCategoryWithEntriesResponse, VRTEntryResponse, VRTSearchResponse

router = APIRouter(prefix="/vrt", tags=["Vulnerability Rating Taxonomy"])


@router.get("/categories", response_model=List[VRTCategoryResponse], summary="List VRT Categories")
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all active VRT categories."""
    service = VRTService(db)
    return service.get_all_categories()


@router.get("/categories/{category_id}", response_model=VRTCategoryWithEntriesResponse, summary="Get Category Details")
def get_category(category_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific VRT category including all its vulnerability entries."""
    service = VRTService(db)
    return service.get_category(category_id)


@router.get("/entries/{entry_id}", response_model=VRTEntryResponse, summary="Get VRT Entry Details")
def get_entry(entry_id: str, db: Session = Depends(get_db)):
    """Retrieve specific vulnerability entry details."""
    service = VRTService(db)
    return service.get_entry(entry_id)


@router.get("/search", response_model=VRTSearchResponse, summary="Search VRT")
def search_vrt(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Full-text search across VRT entries."""
    service = VRTService(db)
    entries = service.search_vrt(q, limit)
    return {"entries": entries}


@router.post("/seed", summary="Seed VRT Data (Admin)", status_code=202)
def seed_vrt_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Admin-only. Load VRT data from `vrt.json` into the database in the background."""
    def seed_task():
        db_session = next(get_db())
        svc = VRTService(db_session)
        svc.load_vrt_from_json()
        db_session.close()

    background_tasks.add_task(seed_task)
    return {"message": "VRT data seeding started in the background."}
