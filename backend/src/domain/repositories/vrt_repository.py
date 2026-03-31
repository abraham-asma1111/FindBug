"""
VRT Repository — Vulnerability Rating Taxonomy queries
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.repositories.base import BaseRepository
from src.domain.models.vrt import VRTCategory, VRTEntry


class VRTRepository(BaseRepository[VRTCategory]):
    def __init__(self, db: Session):
        super().__init__(db, VRTCategory)

    def get_all_categories(self, active_only: bool = True) -> List[VRTCategory]:
        query = self.db.query(VRTCategory)
        if active_only:
            query = query.filter(VRTCategory.is_active == True)
        return query.order_by(VRTCategory.name).all()

    def get_category_by_slug(self, slug: str) -> Optional[VRTCategory]:
        return self.db.query(VRTCategory).filter(VRTCategory.slug == slug).first()

    def get_entries_by_category(self, category_id: str) -> List[VRTEntry]:
        return (
            self.db.query(VRTEntry)
            .filter(VRTEntry.category_id == category_id, VRTEntry.is_active == True)
            .order_by(VRTEntry.name)
            .all()
        )

    def get_all_entries(self, limit: int = 100, offset: int = 0) -> List[VRTEntry]:
        """Get all VRT entries with pagination."""
        return (
            self.db.query(VRTEntry)
            .filter(VRTEntry.is_active == True)
            .order_by(VRTEntry.name)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_entry_by_id(self, entry_id: str) -> Optional[VRTEntry]:
        return self.db.query(VRTEntry).filter(VRTEntry.id == entry_id).first()

    def get_entry_by_slug(self, slug: str) -> Optional[VRTEntry]:
        return self.db.query(VRTEntry).filter(VRTEntry.slug == slug).first()

    def search_entries(self, query: str, limit: int = 20) -> List[VRTEntry]:
        like = f"%{query}%"
        return (
            self.db.query(VRTEntry)
            .filter(
                VRTEntry.is_active == True,
                (VRTEntry.name.ilike(like) | VRTEntry.description.ilike(like))
            )
            .limit(limit)
            .all()
        )

    def create_category(self, data: dict) -> VRTCategory:
        cat = VRTCategory(**data)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def create_entry(self, data: dict) -> VRTEntry:
        entry = VRTEntry(**data)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
