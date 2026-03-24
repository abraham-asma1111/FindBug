"""
VRT Service — Vulnerability Rating Taxonomy management (FREQ-09)
"""
import json
import os
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.repositories.vrt_repository import VRTRepository
from src.domain.models.vrt import VRTCategory, VRTEntry
from src.core.cache import cache
from src.core.logging import get_logger
from src.core.exceptions import NotFoundException
from src.utils.formatters import slugify

logger = get_logger(__name__)

VRT_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vrt.json")


class VRTService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VRTRepository(db)

    # ─── Categories ───────────────────────────────────────────────────────

    def get_all_categories(self) -> List[dict]:
        """Return all active VRT categories (cached for 1 hour)."""
        cache_key = cache.vrt_key("categories")
        cached = cache.get(cache_key)
        if cached:
            return cached

        categories = self.repo.get_all_categories(active_only=True)
        result = [c.to_dict() for c in categories]
        cache.set(cache_key, result, ttl=3600)
        return result

    def get_category(self, category_id: str) -> dict:
        """Get a single category with its entries."""
        category = self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("VRT category not found.")
        entries = self.repo.get_entries_by_category(category_id)
        data = category.to_dict()
        data["entries"] = [e.to_dict() for e in entries]
        return data

    # ─── Entries ──────────────────────────────────────────────────────────

    def get_entry(self, entry_id: str) -> dict:
        """Get a single VRT entry by ID."""
        entry = self.repo.get_entry_by_id(entry_id)
        if not entry:
            raise NotFoundException("VRT entry not found.")
        return entry.to_dict()

    def search_vrt(self, query: str, limit: int = 20) -> List[dict]:
        """Full-text search across VRT entries."""
        if not query or len(query.strip()) < 2:
            return []
        entries = self.repo.search_entries(query.strip(), limit=limit)
        return [e.to_dict() for e in entries]

    # ─── Seeding ──────────────────────────────────────────────────────────

    def load_vrt_from_json(self, path: Optional[str] = None) -> dict:
        """
        Seed VRT data from data/vrt.json into the database.
        Safe to call multiple times (skips existing slugs).
        """
        file_path = path or VRT_JSON_PATH
        if not os.path.exists(file_path):
            logger.warning("vrt.json not found", extra={"path": file_path})
            return {"categories": 0, "entries": 0}

        with open(file_path, "r") as f:
            data = json.load(f)

        cat_count = 0
        entry_count = 0

        for cat_data in data.get("categories", []):
            slug = slugify(cat_data["name"])
            existing = self.repo.get_category_by_slug(slug)
            if not existing:
                cat = self.repo.create_category({
                    "name": cat_data["name"],
                    "slug": slug,
                    "description": cat_data.get("description"),
                    "icon": cat_data.get("icon"),
                })
                cat_count += 1
            else:
                cat = existing

            for entry_data in cat_data.get("entries", []):
                entry_slug = slugify(entry_data["name"])
                existing_entry = self.repo.get_entry_by_slug(entry_slug)
                if not existing_entry:
                    self.repo.create_entry({
                        "category_id": cat.id,
                        "name": entry_data["name"],
                        "slug": entry_slug,
                        "subcategory": entry_data.get("subcategory"),
                        "description": entry_data.get("description"),
                        "cvss_min": entry_data.get("cvss_min", 0.0),
                        "cvss_max": entry_data.get("cvss_max", 10.0),
                        "priority": entry_data.get("priority", "medium"),
                        "remediation": entry_data.get("remediation"),
                        "references": "\n".join(entry_data.get("references", [])),
                    })
                    entry_count += 1

        # Invalidate cache
        cache.delete(cache.vrt_key("categories"))
        logger.info("VRT data loaded", extra={"categories": cat_count, "entries": entry_count})
        return {"categories": cat_count, "entries": entry_count}
