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

    def get_all_entries(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all VRT entries with pagination."""
        entries = self.repo.get_all_entries(limit=limit, offset=offset)
        return [e.to_dict() for e in entries]

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
        Seed VRT data from Bugcrowd's VRT JSON into the database.
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

        # Parse Bugcrowd VRT format: content -> categories -> subcategories -> variants
        for category_data in data.get("content", []):
            if category_data.get("type") != "category":
                continue
                
            cat_slug = category_data["id"]
            existing_cat = self.repo.get_category_by_slug(cat_slug)
            
            if not existing_cat:
                cat = self.repo.create_category({
                    "name": category_data["name"],
                    "slug": cat_slug,
                    "description": f"Bugcrowd VRT Category: {category_data['name']}",
                    "icon": None,
                })
                cat_count += 1
            else:
                cat = existing_cat

            # Process subcategories and variants
            for subcategory_data in category_data.get("children", []):
                if subcategory_data.get("type") != "subcategory":
                    continue
                    
                subcategory_name = subcategory_data["name"]
                
                # Process variants (actual vulnerability entries)
                for variant_data in subcategory_data.get("children", []):
                    if variant_data.get("type") != "variant":
                        continue
                        
                    entry_slug = variant_data["id"]
                    existing_entry = self.repo.get_entry_by_slug(entry_slug)
                    
                    if not existing_entry:
                        # Map priority (1=critical, 2=high, 3=medium, 4=low, 5=info)
                        priority_map = {1: "critical", 2: "high", 3: "medium", 4: "low", 5: "info"}
                        priority = priority_map.get(variant_data.get("priority", 3), "medium")
                        
                        self.repo.create_entry({
                            "category_id": cat.id,
                            "name": variant_data["name"],
                            "slug": entry_slug,
                            "subcategory": subcategory_name,
                            "description": f"{category_data['name']} > {subcategory_name} > {variant_data['name']}",
                            "cvss_min": 0.0,
                            "cvss_max": 10.0,
                            "priority": priority,
                            "remediation": None,
                            "references": "",
                        })
                        entry_count += 1

        # Invalidate cache
        cache.delete(cache.vrt_key("categories"))
        logger.info("VRT data loaded", extra={"categories": cat_count, "entries": entry_count})
        return {"categories": cat_count, "entries": entry_count}
