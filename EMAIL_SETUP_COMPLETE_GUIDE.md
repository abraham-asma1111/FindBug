# 📧 Email Setup Complete Guide

## ✅ What's Already Implemented

### Backend Services
- ✅ **Registration Service**: Handles OTP-based registration flow
- ✅ **Email Service**: Sends beautiful HTML emails with OTP codes
- ✅ **Database Table**: `pending_registrations` table created
- ✅ **API Endpoints**: All registration endpoints implemented
- ✅ **Security**: Password validation, input sanitization, rate limiting

### Frontend Pages
- ✅ **Registration Forms**: Researcher and Organization registration
- ✅ **OTP Verification**: Beautiful 6-digit OTP input with timer
- ✅ **Email Integration**: Proper API calls to backend
- ✅ **Error Handling**: User-friendly error messages

### Email Features
- ✅ **HTML Templates**: Professional email design with FindBug branding
- ✅ **OTP Codes**: 6-digit codes with 10-minute expiration
- ✅ **Backup Links**: Alternative verification method
- ✅ **Resend Functionality**: Users can request new codes
- ✅ **Business Email Validation**: Organizations must use company emails

## 🔧 Final Setup Steps

### Step 1: Get Gmail App Password

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification" if not already enabled

2. **Generate App Password**
   - In Security settings, find "App passwords"
   - Select "Mail" → "Other (custom name)"
   - Enter "FindBug Platform"
   - Copy the 16-character password (like: `abcd efgh ijkl mnop`)

### Step 2: Configure Backend

Edit `backend/.env` file:

```env
# Replace these with your actual values:
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # Remove spaces from app password
```

### Step 3: Test Email Configuration

```bash
# Test SMTP connection
python test_email_setup.py

# Test complete registration flow
python test_otp_registration_flow.py
```

## 🚀 How the Registration Flow Works

### 1. User Registration
```
User fills form → Frontend validates → Sends to backend
```

### 2. Backend Processing
```
Validate data → Store in pending_registrations → Generate OTP → Send email
```

### 3. Email Verification
```
User receives email → Enters OTP → Backend verifies → Creates user account
```

### 4. Account Creation
```
OTP verified → Create User + Profile → Delete pending registration → Login ready
```

## 📱 Testing the Complete Flow

### Start Services
```bash
# Terminal 1: Backend
cd backend
uvicorn src.main:app --reload --port 8002

# Terminal 2: Frontend  
cd frontend
npm run dev
```

### Test Registration
1. Visit: http://localhost:3002/auth/register
2. Fill registration form
3. Submit form
4. Check email for OTP code
5. Visit: http://localhost:3002/auth/verify-otp
6. Enter 6-digit OTP
7. Account created successfully!

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/registration/researcher/initiate` | Start researcher registration |
| POST | `/registration/organization/initiate` | Start organization registration |
| POST | `/registration/verify-otp` | Verify OTP and create account |
| POST | `/registration/verify-token` | Verify via email link (backup) |
| POST | `/registration/resend-otp` | Resend OTP code |

## 📧 Email Templates

### Registration Email Features
- **Professional Design**: FindBug branding with purple theme
- **Clear OTP Display**: Large, centered 6-digit code
- **Expiration Warning**: 10-minute countdown
- **Backup Method**: Alternative verification link
- **Mobile Friendly**: Responsive HTML design

### Email Content
- Welcome message with user type (researcher/organization)
- Prominent OTP code display
- Clear expiration time
- Alternative verification link
- Security notice for unintended registrations

## 🔒 Security Features

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter  
- At least 1 number
- At least 1 special character

### Email Validation
- **Researchers**: Any valid email accepted
- **Organizations**: Business emails only (no Gmail, Yahoo, etc.)
- Email format validation
- Duplicate email prevention

### OTP Security
- 6-digit random codes
- 10-minute expiration
- Rate limiting on resend
- Secure token generation
- Hash storage in database

## 🗄️ Database Schema

### pending_registrations Table
```sql
- id (UUID, Primary Key)
- email (String, Unique)
- password_hash (String)
- registration_type (Enum: researcher/organization)
- first_name, last_name (String)
- company_name, phone_number, country (String, nullable)
- verification_token (String)
- verification_otp (String, nullable)
- otp_expires_at (DateTime, nullable)
- is_verified (Boolean, default: False)
- verified_at (DateTime, nullable)
- created_at, expires_at (DateTime)
- ip_address, user_agent (String, nullable)
```

## 🎉 What Happens After Setup

Once you configure the Gmail credentials:

1. **Registration emails will be sent automatically**
2. **Users receive professional-looking OTP emails**
3. **Complete registration flow works end-to-end**
4. **User accounts are created after OTP verification**
5. **Users can immediately log in after registration**

## 🔍 Troubleshooting

### Common Issues

**"Authentication failed"**
- Check if 2FA is enabled on Gmail
- Verify App Password is correct (no spaces)
- Make sure using App Password, not regular password

**"Email not received"**
- Check spam/junk folder
- Verify SMTP_USER is correct
- Test with `python test_email_setup.py`

**"Invalid OTP"**
- Check if OTP expired (10 minutes)
- Verify correct email address
- Try resending OTP

**"Registration failed"**
- Check password requirements
- Verify email format
- Check if email already registered

## 📞 Support

If you encounter issues:
1. Run `python test_email_setup.py` to diagnose
2. Check backend logs for detailed errors
3. Verify all environment variables are set
4. Test with a simple email first

---

**🎯 Status: Ready for Production!**

The OTP registration system is fully implemented and ready for use once Gmail credentials are configured.