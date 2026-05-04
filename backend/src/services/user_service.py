"""
User Service — Profile management (FREQ-14)
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.researcher_repository import ResearcherRepository
from src.domain.repositories.organization_repository import OrganizationRepository
from src.core.exceptions import NotFoundException, ForbiddenException, ConflictException
from src.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.researcher_repo = ResearcherRepository(db)
        self.org_repo = OrganizationRepository(db)

    # ─── Profile ──────────────────────────────────────────────────────────

    def get_profile(self, user_id: str) -> dict:
        """Get full profile for a user (includes role-specific data)."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")

        profile = {
            "id": str(user.id),
            "email": user.email,
            "full_name": getattr(user, "full_name", None),
            "role": user.role,
            "status": getattr(user, "status", "active"),
            "email_verified": getattr(user, "email_verified", False),
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if getattr(user, "last_login_at", None) else None,
        }

        # Attach role-specific data
        if user.role.lower() == "researcher":
            researcher = self.researcher_repo.get_by_user_id(user_id)
            if researcher:
                profile["researcher"] = {
                    "bio": getattr(researcher, "bio", None),
                    "website": getattr(researcher, "website", None),
                    "github": getattr(researcher, "github", None),
                    "twitter": getattr(researcher, "twitter", None),
                    "reputation_score": getattr(researcher, "reputation_score", 0),
                    "rank": getattr(researcher, "rank", 0),
                    "total_earnings": float(getattr(researcher, "total_earnings", 0)),
                }
        elif user.role.lower() == "organization":
            org = self.org_repo.get_by_user_id(user_id)
            if org:
                profile["organization"] = {
                    "id": str(org.id),  # Include organization ID for subscription management
                    "company_name": getattr(org, "company_name", None),
                    "industry": getattr(org, "industry", None),
                    "website": getattr(org, "website", None),
                    "subscription_type": getattr(org, "subscription_type", None),
                }

        logger.info("Profile fetched", extra={"user_id": user_id})
        return profile

    def get_public_profile(self, user_id: str) -> dict:
        """Public-facing profile (no sensitive data)."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        if user.role == "researcher":
            researcher = self.researcher_repo.get_by_user_id(user_id)
            return {
                "id": str(user.id),
                "full_name": getattr(user, "full_name", None),
                "role": user.role,
                "bio": getattr(researcher, "bio", None) if researcher else None,
                "github": getattr(researcher, "github", None) if researcher else None,
                "reputation_score": getattr(researcher, "reputation_score", 0) if researcher else 0,
                "rank": getattr(researcher, "rank", 0) if researcher else 0,
            }
        return {
            "id": str(user.id),
            "full_name": getattr(user, "full_name", None),
            "role": user.role,
        }

    def search_users(self, query: str, limit: int = 10, exclude_user_id: Optional[str] = None) -> dict:
        """Search for users by email or name."""
        from src.domain.models.user import User
        
        # Build search query
        search_filter = User.email.ilike(f"%{query}%")
        if hasattr(User, 'full_name'):
            search_filter = search_filter | User.full_name.ilike(f"%{query}%")
        
        query_builder = self.db.query(User).filter(search_filter)
        
        # Exclude current user
        if exclude_user_id:
            from uuid import UUID
            query_builder = query_builder.filter(User.id != UUID(exclude_user_id))
        
        # Limit results
        users = query_builder.limit(limit).all()
        
        results = []
        for user in users:
            results.append({
                "id": str(user.id),
                "email": user.email,
                "full_name": getattr(user, "full_name", None),
                "role": user.role,
            })
        
        return {
            "users": results,
            "total": len(results),
            "query": query
        }

    def update_profile(self, user_id: str, data: dict, requesting_user_id: str) -> dict:
        """Update user profile. Users can only update their own profiles."""
        if user_id != requesting_user_id:
            raise ForbiddenException("You can only update your own profile.")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")

        # Update top-level user fields
        user_fields = {k: v for k, v in data.items()
                       if k in ("full_name", "phone") and v is not None}
        if user_fields:
            for field, value in user_fields.items():
                setattr(user, field, value)
            self.db.commit()

        # Update role-specific fields
        role_data = data.get("profile", {})
        if role_data:
            if user.role == "researcher":
                researcher = self.researcher_repo.get_by_user_id(user_id)
                if researcher:
                    allowed_fields = {"bio", "website", "github", "twitter", "linkedin"}
                    for field in allowed_fields:
                        if field in role_data:
                            setattr(researcher, field, role_data[field])
                    self.db.commit()
            elif user.role == "organization":
                org = self.org_repo.get_by_user_id(user_id)
                if org:
                    allowed_fields = {"company_name", "industry", "website"}
                    for field in allowed_fields:
                        if field in role_data:
                            setattr(org, field, role_data[field])
                    self.db.commit()

        logger.info("Profile updated", extra={"user_id": user_id})
        return self.get_profile(user_id)

    # ─── Admin operations ─────────────────────────────────────────────────

    def list_users(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> dict:
        """List users (admin only)."""
        filters = {}
        if role:
            filters["role"] = role
        if status:
            filters["status"] = status
        users = self.user_repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.user_repo.count(filters=filters)
        return {
            "users": [
                {
                    "id": str(u.id),
                    "email": u.email,
                    "full_name": getattr(u, "full_name", None),
                    "role": u.role,
                    "status": getattr(u, "status", "active"),
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def deactivate_user(self, user_id: str) -> dict:
        """Deactivate (soft-delete) a user account."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        user.status = "deactivated"
        user.is_active = False
        self.db.commit()
        logger.info("User deactivated", extra={"user_id": user_id})
        return {"message": "User account deactivated.", "user_id": user_id}

    def reactivate_user(self, user_id: str) -> dict:
        """Reactivate a deactivated user account."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        user.status = "active"
        user.is_active = True
        self.db.commit()
        logger.info("User reactivated", extra={"user_id": user_id})
        return {"message": "User account reactivated.", "user_id": user_id}
