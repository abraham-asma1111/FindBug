"""
VRT (Vulnerability Rating Taxonomy) SQLAlchemy models
Maps to Bugcrowd's public VRT taxonomy — FREQ-09
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship

from src.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class VRTCategory(Base):
    """Top-level vulnerability category (e.g. Server-Side Injection)."""
    __tablename__ = "vrt_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    entries = relationship("VRTEntry", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<VRTCategory {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "icon": self.icon,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class VRTEntry(Base):
    """
    Specific vulnerability entry within a category.
    e.g. Category: XSS → Entry: Reflected XSS
    """
    __tablename__ = "vrt_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("vrt_categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    subcategory = Column(String(200), nullable=True)   # e.g. "Stored", "Reflected"
    description = Column(Text, nullable=True)
    cvss_min = Column(Float, default=0.0, nullable=False)
    cvss_max = Column(Float, default=10.0, nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    remediation = Column(Text, nullable=True)
    references = Column(Text, nullable=True)  # Newline-separated URLs
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("VRTCategory", back_populates="entries")

    def __repr__(self):
        return f"<VRTEntry {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "slug": self.slug,
            "subcategory": self.subcategory,
            "description": self.description,
            "cvss_min": self.cvss_min,
            "cvss_max": self.cvss_max,
            "priority": self.priority,
            "remediation": self.remediation,
            "references": self.references.split("\n") if self.references else [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
