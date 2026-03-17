# Persona KYC Integration

## Overview
FindBug uses **Persona** for identity verification of researchers, similar to how LinkedIn, Coinbase, and Stripe verify users.

## How It Works

### 1. Researcher Initiates KYC
```bash
POST /api/v1/auth/kyc/start
Authorization: Bearer <jwt_token>
```

**Requirements**:
- Email must be verified
- User must be a researcher (not organization)
- KYC not already verified

**Response**:
```json
{
  "inquiry_id": "inq_abc123",
  "session_token": "sess_xyz789",
  "status": "created",
  "message": "KYC verification session created"
}
```

### 2. Frontend Loads Persona Widget
```javascript
// Frontend code (React/Vue/vanilla JS)
const client = new Persona.Client({
  templateId: 'itmpl_xxx',
  environmentId: 'env_xxx',
  sessionToken: 'sess_xyz789', // From backend response
  onComplete: ({ inquiryId, status }) => {
    // Verification completed
    console.log('Verification complete:', inquiryId);
  },
  onError: (error) => {
    console.error('Verification error:', error);
  }
});

client.open();
```

### 3. User Completes Verification
The Persona widget guides the user through:
1. **Document Capture**: Take photo of government ID (passport, driver's license, national ID)
2. **Biometric Liveness**: 3D selfie with anti-spoofing detection
3. **Data Extraction**: Persona extracts name, DOB, ID number
4. **Verification**: AI + human review validates authenticity

### 4. Persona Sends Webhook
When verification completes, Persona sends webhook to:
```
POST /api/v1/auth/kyc/webhook
```

**Webhook Payload**:
```json
{
  "data": {
    "type": "inquiry",
    "id": "inq_abc123",
    "attributes": {
      "status": "completed",
      "decision": "approved",
      "reference-id": "researcher_uuid",
      "completed-at": "2026-03-17T10:30:00Z",
      "fields": {
        "selected-id-class": "passport"
      }
    }
  }
}
```

### 5. Backend Updates KYC Status
- `approved` → `kyc_status = "verified"`
- `declined` → `kyc_status = "rejected"`
- `needs_review` → `kyc_status = "pending"`

### 6. Check KYC Status
```bash
GET /api/v1/auth/kyc/status
Authorization: Bearer <jwt_token>
```

**Response**:
```json
{
  "kyc_status": "verified",
  "message": "KYC status: verified"
}
```

## Configuration

Add to `.env`:
```env
PERSONA_API_KEY=your_api_key_from_persona_dashboard
PERSONA_TEMPLATE_ID=itmpl_your_template_id
PERSONA_WEBHOOK_SECRET=your_webhook_secret
```

## Security Features

1. **Webhook Signature Verification**: HMAC-SHA256 signature validation
2. **Biometric Liveness**: Prevents photo/video spoofing
3. **Document Authentication**: AI detects fake IDs
4. **Audit Logging**: All KYC events logged with IP and timestamp

## Why Persona?

- **Used by**: LinkedIn, Coinbase, Stripe, Uber, DoorDash
- **Compliance**: GDPR, CCPA, SOC 2 Type II certified
- **Global Coverage**: Supports 200+ countries and 5000+ ID types
- **Liveness Detection**: 3D face mapping prevents spoofing
- **Fast**: 30-second verification flow
- **Mobile-First**: Works on iOS/Android/Web

## Testing (Sandbox Mode)

Persona provides sandbox mode for testing:
1. Use sandbox API key
2. Test with sample IDs (they provide test documents)
3. Webhook events work the same in sandbox

## Cost
- Pay per verification (~$1-3 per inquiry)
- Volume discounts available
- Free sandbox testing

---

**Next Steps**:
1. Sign up at https://withpersona.com
2. Get API keys from dashboard
3. Create inquiry template (configure what documents to accept)
4. Add webhook URL: `https://yourdomain.com/api/v1/auth/kyc/webhook`
5. Test in sandbox mode
6. Go live
