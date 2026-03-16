# VRT Implementation Plan
## Bugcrowd Vulnerability Rating Taxonomy Integration

**Date**: March 13, 2026  
**Status**: Ready for Implementation

---

## 📋 IMPLEMENTATION STEPS

### Step 1: Download VRT Data
**Task**: Obtain Bugcrowd VRT JSON
- Source: https://github.com/bugcrowd/vulnerability-rating-taxonomy
- File: `vulnerability-rating-taxonomy.json`
- Location: `backend/app/data/vrt.json`

### Step 2: Create Database Schema
**Task**: Add VRT tables to database

```sql
-- VRT Categories
CREATE TABLE vrt_categories (
    id SERIAL PRIMARY KEY,
    vrt_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES vrt_categories(id),
    priority VARCHAR(10),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VRT Subcategories
CREATE TABLE vrt_subcategories (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES vrt_categories(id),
    vrt_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    priority VARCHAR(10),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Update vulnerability_reports table
ALTER TABLE vulnerability_reports 
ADD COLUMN vrt_category_id INTEGER REFERENCES vrt_categories(id),
ADD COLUMN vrt_subcategory_id INTEGER REFERENCES vrt_subcategories(id),
ADD COLUMN vrt_priority VARCHAR(10);

-- Create indexes
CREATE INDEX idx_vrt_categories_vrt_id ON vrt_categories(vrt_id);
CREATE INDEX idx_vrt_subcategories_category_id ON vrt_subcategories(category_id);
CREATE INDEX idx_reports_vrt_category ON vulnerability_reports(vrt_category_id);
```

### Step 3: Create VRT Models
**File**: `backend/app/models/vrt.py`

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class VRTCategory(Base):
    __tablename__ = "vrt_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    vrt_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("vrt_categories.id"), nullable=True)
    priority = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("VRTCategory", remote_side=[id], backref="children")
    subcategories = relationship("VRTSubcategory", back_populates="category")
    reports = relationship("VulnerabilityReport", back_populates="vrt_category")

class VRTSubcategory(Base):
    __tablename__ = "vrt_subcategories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("vrt_categories.id"), nullable=False)
    vrt_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    priority = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("VRTCategory", back_populates="subcategories")
    reports = relationship("VulnerabilityReport", back_populates="vrt_subcategory")
```

### Step 4: Create VRT Schemas
**File**: `backend/app/schemas/vrt.py`

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VRTCategoryBase(BaseModel):
    vrt_id: str
    name: str
    priority: Optional[str] = None
    description: Optional[str] = None

class VRTCategoryCreate(VRTCategoryBase):
    parent_id: Optional[int] = None

class VRTCategory(VRTCategoryBase):
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VRTSubcategoryBase(BaseModel):
    vrt_id: str
    name: str
    priority: Optional[str] = None
    description: Optional[str] = None

class VRTSubcategoryCreate(VRTSubcategoryBase):
    category_id: int

class VRTSubcategory(VRTSubcategoryBase):
    id: int
    category_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class VRTCategoryWithSubcategories(VRTCategory):
    subcategories: List[VRTSubcategory] = []
```

### Step 5: Create VRT Service
**File**: `backend/app/services/vrt_service.py`


```python
import json
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.vrt import VRTCategory, VRTSubcategory
from app.schemas.vrt import VRTCategoryCreate, VRTSubcategoryCreate

class VRTService:
    def __init__(self, db: Session):
        self.db = db
    
    def load_vrt_from_json(self, json_path: str) -> bool:
        """Load VRT data from Bugcrowd JSON file"""
        try:
            with open(json_path, 'r') as f:
                vrt_data = json.load(f)
            
            # Parse and insert VRT data
            self._parse_and_insert_vrt(vrt_data)
            return True
        except Exception as e:
            print(f"Error loading VRT: {e}")
            return False
    
    def _parse_and_insert_vrt(self, vrt_data: dict):
        """Parse VRT JSON and insert into database"""
        # Implementation depends on VRT JSON structure
        pass
    
    def get_all_categories(self) -> List[VRTCategory]:
        """Get all VRT categories"""
        return self.db.query(VRTCategory).filter(VRTCategory.parent_id == None).all()
    
    def get_category_by_id(self, category_id: int) -> Optional[VRTCategory]:
        """Get VRT category by ID"""
        return self.db.query(VRTCategory).filter(VRTCategory.id == category_id).first()
    
    def get_subcategories(self, category_id: int) -> List[VRTSubcategory]:
        """Get subcategories for a category"""
        return self.db.query(VRTSubcategory).filter(
            VRTSubcategory.category_id == category_id
        ).all()
    
    def get_priority_by_vrt_id(self, vrt_id: str) -> Optional[str]:
        """Get priority (P1-P5) for VRT ID"""
        category = self.db.query(VRTCategory).filter(
            VRTCategory.vrt_id == vrt_id
        ).first()
        
        if category:
            return category.priority
        
        subcategory = self.db.query(VRTSubcategory).filter(
            VRTSubcategory.vrt_id == vrt_id
        ).first()
        
        return subcategory.priority if subcategory else None
    
    def suggest_severity(self, title: str, description: str) -> Dict:
        """
        AI-assisted severity suggestion based on report content
        (Future enhancement with ML/NLP)
        """
        # For now, return default suggestion
        return {
            "suggested_priority": "P3",
            "confidence": 0.5,
            "reasoning": "Default suggestion - manual review required"
        }
    
    def calculate_reward_range(
        self, 
        priority: str, 
        program_tiers: Dict
    ) -> tuple:
        """Calculate reward range based on priority and program tiers"""
        tier = program_tiers.get(priority, {})
        return (tier.get('min', 0), tier.get('max', 0))
```

### Step 6: Create VRT API Endpoints
**File**: `backend/app/api/v1/vrt.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.vrt_service import VRTService
from app.schemas.vrt import VRTCategory, VRTSubcategory, VRTCategoryWithSubcategories

router = APIRouter()

@router.get("/categories", response_model=List[VRTCategory])
def get_vrt_categories(db: Session = Depends(get_db)):
    """Get all VRT categories"""
    vrt_service = VRTService(db)
    return vrt_service.get_all_categories()

@router.get("/categories/{category_id}", response_model=VRTCategoryWithSubcategories)
def get_vrt_category(category_id: int, db: Session = Depends(get_db)):
    """Get VRT category with subcategories"""
    vrt_service = VRTService(db)
    category = vrt_service.get_category_by_id(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

@router.get("/categories/{category_id}/subcategories", response_model=List[VRTSubcategory])
def get_vrt_subcategories(category_id: int, db: Session = Depends(get_db)):
    """Get subcategories for a category"""
    vrt_service = VRTService(db)
    return vrt_service.get_subcategories(category_id)

@router.get("/priority/{vrt_id}")
def get_vrt_priority(vrt_id: str, db: Session = Depends(get_db)):
    """Get priority for VRT ID"""
    vrt_service = VRTService(db)
    priority = vrt_service.get_priority_by_vrt_id(vrt_id)
    
    if not priority:
        raise HTTPException(status_code=404, detail="VRT ID not found")
    
    return {"vrt_id": vrt_id, "priority": priority}
```

### Step 7: Update Report Schema
**File**: `backend/app/schemas/report.py`

Add VRT fields to report schemas:

```python
class VulnerabilityReportCreate(BaseModel):
    program_id: int
    title: str
    description: str
    steps_to_reproduce: str
    impact_assessment: str
    vrt_category_id: int  # NEW
    vrt_subcategory_id: Optional[int] = None  # NEW
    severity_suggestion: Optional[str] = None
    attachments: Optional[List[str]] = []

class VulnerabilityReport(VulnerabilityReportBase):
    id: int
    researcher_id: int
    status: str
    vrt_category_id: int  # NEW
    vrt_subcategory_id: Optional[int] = None  # NEW
    vrt_priority: Optional[str] = None  # NEW (P1-P5)
    assigned_severity: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    vrt_category: Optional[VRTCategory] = None  # NEW
    vrt_subcategory: Optional[VRTSubcategory] = None  # NEW
```

### Step 8: Frontend VRT Component
**File**: `frontend/src/components/forms/VRTSelector.tsx`

```typescript
import { useState, useEffect } from 'react';

interface VRTCategory {
  id: number;
  name: string;
  priority: string;
}

interface VRTSubcategory {
  id: number;
  name: string;
  priority: string;
}

export function VRTSelector({ onChange }) {
  const [categories, setCategories] = useState<VRTCategory[]>([]);
  const [subcategories, setSubcategories] = useState<VRTSubcategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [selectedSubcategory, setSelectedSubcategory] = useState<number | null>(null);
  const [suggestedPriority, setSuggestedPriority] = useState<string>('');

  useEffect(() => {
    // Fetch VRT categories
    fetch('/api/v1/vrt/categories')
      .then(res => res.json())
      .then(data => setCategories(data));
  }, []);

  useEffect(() => {
    if (selectedCategory) {
      // Fetch subcategories
      fetch(`/api/v1/vrt/categories/${selectedCategory}/subcategories`)
        .then(res => res.json())
        .then(data => setSubcategories(data));
    }
  }, [selectedCategory]);

  const handleCategoryChange = (categoryId: number) => {
    setSelectedCategory(categoryId);
    setSelectedSubcategory(null);
    
    const category = categories.find(c => c.id === categoryId);
    setSuggestedPriority(category?.priority || '');
    
    onChange({ categoryId, subcategoryId: null, priority: category?.priority });
  };

  const handleSubcategoryChange = (subcategoryId: number) => {
    setSelectedSubcategory(subcategoryId);
    
    const subcategory = subcategories.find(s => s.id === subcategoryId);
    setSuggestedPriority(subcategory?.priority || '');
    
    onChange({ 
      categoryId: selectedCategory, 
      subcategoryId, 
      priority: subcategory?.priority 
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">
          Vulnerability Category *
        </label>
        <select
          className="w-full border rounded-lg p-2"
          value={selectedCategory || ''}
          onChange={(e) => handleCategoryChange(Number(e.target.value))}
        >
          <option value="">Select category...</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      {selectedCategory && subcategories.length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2">
            Subcategory
          </label>
          <select
            className="w-full border rounded-lg p-2"
            value={selectedSubcategory || ''}
            onChange={(e) => handleSubcategoryChange(Number(e.target.value))}
          >
            <option value="">Select subcategory...</option>
            {subcategories.map(sub => (
              <option key={sub.id} value={sub.id}>
                {sub.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {suggestedPriority && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-800">
            <strong>Suggested Priority:</strong> {suggestedPriority}
          </p>
          <p className="text-xs text-blue-600 mt-1">
            ℹ️ Based on selected VRT category
          </p>
        </div>
      )}
    </div>
  );
}
```

---

## 📦 DELIVERABLES

1. ✅ VRT JSON data downloaded
2. ✅ Database schema created
3. ✅ VRT models implemented
4. ✅ VRT service implemented
5. ✅ VRT API endpoints created
6. ✅ Report schema updated
7. ✅ Frontend VRT selector component
8. ✅ Reward tier mapping configured
9. ✅ Documentation updated

---

## 🧪 TESTING

### Unit Tests
- Test VRT data loading
- Test category/subcategory retrieval
- Test priority mapping
- Test reward calculation

### Integration Tests
- Test report submission with VRT
- Test triage workflow with VRT
- Test reward calculation based on VRT

### Manual Testing
- Verify VRT dropdown works
- Verify priority suggestion displays
- Verify triage specialist can override
- Verify reward calculation is correct

---

**Status**: Ready for implementation in FREQ-08
