"""
System Settings Service - Handle platform-wide configuration logic.
"""
from typing import Dict, Any, List, Optional
import json

from sqlalchemy.orm import Session

from src.domain.models.system_setting import SystemSetting
from src.core.logging import get_logger

logger = get_logger(__name__)


class SettingsService:
    """
    Service for managing platform-wide system settings.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def _parse_value(self, value_str: str, value_type: str) -> Any:
        if value_str is None:
            return None
        if value_type == "boolean":
            return value_str.lower() in ["true", "1", "yes"]
        if value_type == "integer":
            return int(value_str)
        if value_type == "float":
            return float(value_str)
        if value_type == "json":
            try:
                return json.loads(value_str)
            except:
                return value_str
        return value_str

    def _format_value(self, value: Any, value_type: str) -> str:
        if value is None:
            return ""
        if value_type == "boolean":
            return "true" if value else "false"
        if value_type == "json":
            if isinstance(value, (dict, list)):
                return json.dumps(value)
        return str(value)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting by key."""
        setting = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if not setting:
            return default
        return self._parse_value(setting.value, setting.type)

    def get_all_settings(self, include_private: bool = False) -> Dict[str, Any]:
        """Get all settings as a dictionary."""
        query = self.db.query(SystemSetting)
        if not include_private:
            query = query.filter(SystemSetting.is_public == True)
            
        settings = query.all()
        result = {}
        for s in settings:
            result[s.key] = self._parse_value(s.value, s.type)
        return result

    def update_setting(self, key: str, value: Any, value_type: str = "string", 
                       description: str = None, is_public: bool = False, admin_email: str = None) -> SystemSetting:
        """Create or update a setting."""
        setting = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
        
        str_value = self._format_value(value, value_type)
        
        if setting:
            setting.value = str_value
            if description:
                setting.description = description
            if admin_email:
                setting.updated_by = admin_email
            # Only update type/public if provided
            if value_type != "string" or setting.type == "string":
                setting.type = value_type
            setting.is_public = is_public
        else:
            setting = SystemSetting(
                key=key,
                value=str_value,
                type=value_type,
                description=description,
                is_public=is_public,
                updated_by=admin_email
            )
            self.db.add(setting)
            
        self.db.commit()
        self.db.refresh(setting)
        
        logger.info(f"Setting {key} updated by {admin_email}")
        return setting
        
    def bulk_update_settings(self, settings_dict: Dict[str, Any], admin_email: str = None) -> Dict[str, Any]:
        """Update multiple settings at once."""
        updated = {}
        for key, payload in settings_dict.items():
            value = payload.get("value")
            value_type = payload.get("type", "string")
            is_public = payload.get("is_public", False)
            description = payload.get("description")
            
            self.update_setting(
                key=key,
                value=value,
                value_type=value_type,
                description=description,
                is_public=is_public,
                admin_email=admin_email
            )
            updated[key] = value
            
        return updated
