# FREQ-21 Implementation Status: Secure File Storage with Malware Detection

**Requirement**: The system shall securely store vulnerability reports and related attachments.

**Priority**: High

**Status**: ✅ COMPLETED

---

## Implementation Summary

Implemented secure file storage service with VirusTotal API integration for malware detection. Files are validated, scanned for viruses, and securely stored with metadata tracking.

---

## Components Implemented

### 1. File Storage Service (`backend/src/core/file_storage.py`)

**Features**:
- File type validation (images, videos, documents, archives)
- File size validation (50MB max)
- Safe filename generation with UUID
- SHA-256 hash calculation
- VirusTotal API integration for malware scanning
- Fallback basic malware checks when API unavailable

**Malware Detection Methods**:

1. **VirusTotal Hash Lookup**:
   - Checks if file hash exists in VirusTotal database
   - Instant results for known files
   - API: `GET /api/v3/files/{sha256_hash}`

2. **VirusTotal File Upload**:
   - Uploads new files for scanning
   - Waits for analysis completion (max 60 seconds)
   - API: `POST /api/v3/files`

3. **Analysis Status Polling**:
   - Polls for scan results
   - Returns malicious/suspicious counts
   - API: `GET /api/v3/analyses/{analysis_id}`

4. **Basic Malware Check (Fallback)**:
   - Pattern-based detection for common threats
   - Checks for suspicious signatures
   - Used when VirusTotal API unavailable

**Allowed File Types**:
- Images: PNG, JPEG, JPG, GIF
- Videos: MP4, AVI, QuickTime
- Documents: PDF, TXT
- Archives: ZIP

**Security Features**:
- File type whitelist
- Size limit enforcement (50MB)
- Virus scanning before storage
- Automatic deletion of infected files
- SHA-256 hash for integrity

---

### 2. Report Service Integration (`backend/src/services/report_service.py`)

**Enhanced `upload_attachment` Method**:
- Validates report exists
- Saves file to storage
- Performs virus scanning
- Deletes file if malware detected
- Creates attachment record with scan results
- Tracks `is_safe` and `scanned_at` fields

**Error Handling**:
- Raises error if malware detected
- Prevents infected files from being stored
- Returns detailed scan results

---

### 3. API Endpoint (`backend/src/api/v1/endpoints/reports.py`)

**Endpoint**: `POST /api/v1/reports/{report_id}/attachments`

**Request**:
```
POST /api/v1/reports/{report_id}/attachments
Content-Type: multipart/form-data

file: [binary file data]
```

**Response** (Success):
```json
{
  "message": "Attachment uploaded successfully",
  "attachment_id": "uuid",
  "filename": "safe_filename.ext",
  "original_filename": "original.ext",
  "size": 1024000,
  "type": "image/png",
  "is_safe": true,
  "uploaded_at": "2026-03-19T10:30:00Z"
}
```

**Response** (Malware Detected):
```json
{
  "detail": "Malware detected in file: 3 malicious, 2 suspicious"
}
```

**Access Control**:
- Only researchers can upload attachments
- Must be owner of the report

---

### 4. Database Model (`backend/src/domain/models/report.py`)

**ReportAttachment Model**:
```python
class ReportAttachment:
    id: UUID
    report_id: UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    storage_path: str
    uploaded_by: UUID
    uploaded_at: datetime
    is_safe: bool          # Virus scan result
    scanned_at: datetime   # Scan timestamp
```

---

## VirusTotal API Configuration

### API Key Setup

1. **Get Free API Key**:
   - Visit: https://www.virustotal.com/gui/join-us
   - Sign up for free account
   - Get API key from dashboard

2. **Configure Environment**:
   ```bash
   # Add to .env file
   VIRUSTOTAL_API_KEY=your_api_key_here
   ```

3. **Free Tier Limits**:
   - 4 requests per minute
   - 500 requests per day
   - Suitable for development/testing

### API Endpoints Used

1. **File Hash Lookup**:
   ```
   GET https://www.virustotal.com/api/v3/files/{sha256}
   Header: x-apikey: YOUR_API_KEY
   ```

2. **File Upload**:
   ```
   POST https://www.virustotal.com/api/v3/files
   Header: x-apikey: YOUR_API_KEY
   Body: multipart/form-data with file
   ```

3. **Analysis Status**:
   ```
   GET https://www.virustotal.com/api/v3/analyses/{id}
   Header: x-apikey: YOUR_API_KEY
   ```

---

## Security Features

### 1. File Validation
- ✅ File type whitelist enforcement
- ✅ File size limit (50MB)
- ✅ Empty file rejection
- ✅ Content-type verification

### 2. Malware Detection
- ✅ VirusTotal API integration
- ✅ Hash-based lookup (instant)
- ✅ File upload scanning (new files)
- ✅ Multi-engine analysis (70+ engines)
- ✅ Fallback basic checks

### 3. Safe Storage
- ✅ UUID-based filenames
- ✅ Organized folder structure
- ✅ SHA-256 hash tracking
- ✅ Metadata persistence
- ✅ Automatic infected file deletion

### 4. Audit Trail
- ✅ Upload timestamp
- ✅ Uploader tracking
- ✅ Scan result logging
- ✅ File integrity hash

---

## File Storage Structure

```
data/uploads/
└── reports/
    └── {report_id}/
        ├── {report_id}_20260319_103000_{uuid}.png
        ├── {report_id}_20260319_103015_{uuid}.pdf
        └── {report_id}_20260319_103030_{uuid}.zip
```

---

## Testing Scenarios

### 1. Valid File Upload
```bash
curl -X POST http://localhost:8000/api/v1/reports/{id}/attachments \
  -H "Authorization: Bearer {token}" \
  -F "file=@screenshot.png"
```

**Expected**: File uploaded, scanned, and stored successfully

### 2. Malware File Upload
```bash
curl -X POST http://localhost:8000/api/v1/reports/{id}/attachments \
  -H "Authorization: Bearer {token}" \
  -F "file=@malware.exe"
```

**Expected**: File rejected with malware detection error

### 3. Invalid File Type
```bash
curl -X POST http://localhost:8000/api/v1/reports/{id}/attachments \
  -H "Authorization: Bearer {token}" \
  -F "file=@script.sh"
```

**Expected**: File type not allowed error

### 4. File Too Large
```bash
curl -X POST http://localhost:8000/api/v1/reports/{id}/attachments \
  -H "Authorization: Bearer {token}" \
  -F "file=@large_video.mp4"  # > 50MB
```

**Expected**: File size exceeds limit error

---

## Dependencies Added

```
requests==2.31.0  # For VirusTotal API calls
```

---

## Configuration Files Updated

1. ✅ `backend/.env.example` - Added VIRUSTOTAL_API_KEY
2. ✅ `backend/requirements.txt` - Added requests library
3. ✅ `backend/src/core/file_storage.py` - Implemented malware detection
4. ✅ `backend/src/services/report_service.py` - Integrated virus scanning

---

## FREQ-21 Requirements Checklist

- ✅ Secure file storage implementation
- ✅ File type validation
- ✅ File size limits
- ✅ Malware detection (VirusTotal)
- ✅ Safe filename generation
- ✅ File integrity (SHA-256)
- ✅ Metadata tracking
- ✅ Access control
- ✅ Error handling
- ✅ Audit logging

---

## Next Steps

1. **Production Setup**:
   - Obtain VirusTotal API key
   - Configure environment variables
   - Set up file storage directory
   - Configure backup strategy

2. **Optional Enhancements**:
   - Async virus scanning (Celery task)
   - File encryption at rest
   - CDN integration for downloads
   - Thumbnail generation for images
   - Automatic file cleanup (old reports)

3. **Monitoring**:
   - Track VirusTotal API usage
   - Monitor scan success rates
   - Alert on malware detections
   - Log file storage metrics

---

## Related FREQs

- **FREQ-06**: Vulnerability Report Submission (uses file upload)
- **FREQ-18**: Researcher Report Tracking (views attachments)
- **FREQ-19**: Organization Report Management (downloads attachments)

---

**Implementation Date**: March 19, 2026  
**Status**: Production Ready  
**Security Level**: High
