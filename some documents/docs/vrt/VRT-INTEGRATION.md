# Bugcrowd VRT Integration
## Vulnerability Rating Taxonomy

**Decision Date**: March 13, 2026  
**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor**: Yosef Worku

---

## 🎯 DECISION

We will use **Bugcrowd's Vulnerability Rating Taxonomy (VRT)** as our standard for:
- Vulnerability classification
- Severity scoring
- Impact assessment
- Reward tier mapping

---

## 📋 WHAT IS BUGCROWD VRT?

Bugcrowd VRT is an industry-standard vulnerability classification system that provides:
- **Hierarchical taxonomy** of vulnerability types
- **Standardized severity ratings** (P1-P5)
- **Clear impact definitions**
- **Consistent reward guidance**
- **Open-source and community-maintained**

### VRT Repository
- **GitHub**: https://github.com/bugcrowd/vulnerability-rating-taxonomy
- **Format**: JSON-based taxonomy
- **License**: Open source (can be used freely)
- **Updates**: Regularly maintained by Bugcrowd

---

## 🏗️ VRT STRUCTURE

### Priority Levels (P1-P5)

**P1 - Critical**
- Immediate and severe impact
- Complete system compromise
- Examples: RCE, Authentication bypass, SQL injection with data access

**P2 - High**
- Significant impact
- Major security weakness
- Examples: Stored XSS, IDOR with sensitive data, CSRF on critical functions

**P3 - Medium**
- Moderate impact
- Security weakness requiring specific conditions
- Examples: Reflected XSS, Information disclosure, CSRF on non-critical functions

**P4 - Low**
- Minor impact
- Limited security concern
- Examples: Self-XSS, Minor information leakage, Missing security headers

**P5 - Informational**
- No immediate security impact
- Best practice recommendations
- Examples: Outdated software versions, Missing rate limiting

---

## 🔧 IMPLEMENTATION APPROACH

### 1. VRT Data Integration

**Option A: Static JSON File (Recommended for MVP)**
- Download VRT JSON from Bugcrowd GitHub
- Store in `backend/app/data/vrt.json`
- Load into memory on application startup
- Update manually when VRT is updated

**Option B: Database Storage (Production)**
- Import VRT into PostgreSQL tables
- Create VRT management interface
- Allow custom VRT extensions
- Sync with Bugcrowd updates via API/script

### 2. Database Schema for VRT


```sql
-- VRT Categories Table
CREATE TABLE vrt_categories (
    id SERIAL PRIMARY KEY,
    vrt_id VARCHAR(100) UNIQUE NOT NULL,  -- e.g., "server_security_misconfiguration"
    name VARCHAR(255) NOT NULL,            -- e.g., "Server Security Misconfiguration"
    parent_id INTEGER REFERENCES vrt_categories(id),
    priority VARCHAR(10),                  -- P1, P2, P3, P4, P5
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VRT Subcategories Table
CREATE TABLE vrt_subcategories (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES vrt_categories(id),
    vrt_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    priority VARCHAR(10),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link vulnerability reports to VRT
ALTER TABLE vulnerability_reports ADD COLUMN vrt_category_id INTEGER REFERENCES vrt_categories(id);
ALTER TABLE vulnerability_reports ADD COLUMN vrt_subcategory_id INTEGER REFERENCES vrt_subcategories(id);
```

### 3. VRT Service Implementation

**File**: `backend/app/services/vrt_service.py`


```python
# VRT Service - Load and query VRT taxonomy
class VRTService:
    def __init__(self):
        self.vrt_data = self.load_vrt()
    
    def load_vrt(self) -> dict:
        """Load VRT from JSON file"""
        pass
    
    def get_categories(self) -> list:
        """Get all VRT categories"""
        pass
    
    def get_subcategories(self, category_id: str) -> list:
        """Get subcategories for a category"""
        pass
    
    def get_priority(self, vrt_id: str) -> str:
        """Get priority level (P1-P5) for VRT ID"""
        pass
    
    def suggest_severity(self, title: str, description: str) -> dict:
        """AI-assisted severity suggestion based on report content"""
        pass
    
    def calculate_reward_range(self, priority: str, program_tiers: dict) -> tuple:
        """Calculate reward range based on priority and program tiers"""
        pass
```

### 4. Report Submission with VRT

**Workflow**:
1. Researcher submits vulnerability report
2. Researcher selects VRT category/subcategory (dropdown)
3. System suggests priority based on VRT
4. Triage specialist validates and adjusts if needed
5. System maps priority to reward tier


---

## 📊 VRT MAIN CATEGORIES

Based on Bugcrowd VRT, the main categories include:

1. **Server Security Misconfiguration**
2. **Broken Authentication and Session Management**
3. **Cross-Site Scripting (XSS)**
4. **Insecure Direct Object References (IDOR)**
5. **Security Misconfiguration**
6. **Sensitive Data Exposure**
7. **Missing Function Level Access Control**
8. **Cross-Site Request Forgery (CSRF)**
9. **Using Components with Known Vulnerabilities**
10. **Unvalidated Redirects and Forwards**
11. **SQL Injection**
12. **Remote Code Execution (RCE)**
13. **Server-Side Request Forgery (SSRF)**
14. **XML External Entity (XXE)**
15. **Insecure Deserialization**
16. **Insufficient Logging and Monitoring**
17. **Business Logic Errors**
18. **Privacy Concerns**
19. **Mobile Security**
20. **API Security**

Each category has multiple subcategories with specific priority mappings.

---

## 🎨 UI/UX INTEGRATION

### Report Submission Form

**VRT Selection Component**:
```
┌─────────────────────────────────────────┐
│ Vulnerability Category *                │
│ ┌─────────────────────────────────────┐ │
│ │ Select category...                  ▼│ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Subcategory *                           │
│ ┌─────────────────────────────────────┐ │
│ │ Select subcategory...               ▼│ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Suggested Priority: P2 (High)           │
│ ℹ️ Based on selected VRT category       │
└─────────────────────────────────────────┘
```

### Triage Dashboard

**VRT Display**:
```
Report #12345
Category: Cross-Site Scripting (XSS)
Subcategory: Stored XSS
VRT Priority: P2 (High)
Assigned Severity: High ✓
Reward Range: $500 - $2,000
```

---

## 💰 REWARD TIER MAPPING

### Default Mapping (Can be customized per program)
