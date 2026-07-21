"""
System Setting Model - For platform-wide configurations.
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime
from datetime import datetime

from src.core.database import Base


class SystemSetting(Base):
    """
    Key-Value store for platform-wide configurations.
    Allows dynamic updates without modifying environment variables.
    """
    __tablename__ = "system_settings"
    
    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    type = Column(String(50), default="string")  # string, boolean, integer, json
    is_public = Column(Boolean, default=False)   # If true, can be accessed by unauthenticated users (e.g. maintenance mode)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)  # Admin email who last updated this
    
    def __repr__(self):
        return f"<SystemSetting {self.key}={self.value}>"
