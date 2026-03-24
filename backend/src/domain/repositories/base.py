"""
Generic BaseRepository providing CRUD for all domain models.
"""
from typing import Generic, Optional, Type, TypeVar, List
from sqlalchemy.orm import Session
from src.core.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Generic repository with get_by_id, get_all, create, update, delete.
    All concrete repositories inherit from this class.
    """

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    # ─── Read ─────────────────────────────────────────────────────────────

    def get_by_id(self, record_id: str) -> Optional[T]:
        """Fetch a single record by primary key."""
        return self.db.query(self.model).filter(
            self.model.id == record_id
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[dict] = None,
    ) -> List[T]:
        """Fetch all records with optional skip/limit and equality filters."""
        query = self.db.query(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(
                        getattr(self.model, field) == value
                    )
        return query.offset(skip).limit(limit).all()

    def count(self, filters: Optional[dict] = None) -> int:
        """Count records matching optional filters."""
        query = self.db.query(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(
                        getattr(self.model, field) == value
                    )
        return query.count()

    # ─── Write ────────────────────────────────────────────────────────────

    def create(self, data: dict) -> T:
        """Create a new record from a dict of field values."""
        instance = self.model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, record_id: str, data: dict) -> Optional[T]:
        """Update fields of an existing record."""
        instance = self.get_by_id(record_id)
        if not instance:
            return None
        for field, value in data.items():
            if hasattr(instance, field) and value is not None:
                setattr(instance, field, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, record_id: str) -> bool:
        """Hard-delete a record. Returns True if deleted."""
        instance = self.get_by_id(record_id)
        if not instance:
            return False
        self.db.delete(instance)
        self.db.commit()
        return True

    def soft_delete(self, record_id: str) -> bool:
        """
        Soft-delete: set is_active=False if the column exists.
        Returns True if the record was found and updated.
        """
        instance = self.get_by_id(record_id)
        if not instance:
            return False
        if hasattr(instance, "is_active"):
            instance.is_active = False
            self.db.commit()
            return True
        return self.delete(record_id)

    # ─── Helpers ──────────────────────────────────────────────────────────

    def exists(self, record_id: str) -> bool:
        """Check if a record with the given ID exists."""
        return self.get_by_id(record_id) is not None

    def bulk_create(self, data_list: List[dict]) -> List[T]:
        """Insert multiple records in one commit."""
        instances = [self.model(**data) for data in data_list]
        self.db.add_all(instances)
        self.db.commit()
        for inst in instances:
            self.db.refresh(inst)
        return instances
