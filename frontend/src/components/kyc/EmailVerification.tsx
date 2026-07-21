'use client';

import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';

interface EmailVerificationProps {
  enabled: boolean;
  onSuccess?: () => void;
  onError?: (error: string) => void;
  initialVerified?: boolean; // Add prop to show verified state from API
  verifiedEmail?: string; // Add prop to show which email was verified
  userEmail: string; // SECURITY: The logged-in user's registered email (read-only)
}

export default function EmailVerification({ enabled, onSuccess, onError, initialVerified = false, verifiedEmail, userEmail }: EmailVerificationProps) {
  console.log('[EmailVerification] Props:', { enabled, initialVerified, verifiedEmail, userEmail });
  
  // CRITICAL: Track if email is verified - update when initialVerified prop changes
  const [isVerified, setIsVerified] = useState(initialVerified);
  
  const [step, setStep] = useState<'input' | 'verify' | 'success'>('input');
  // SECURITY: Use the user's registered email - they can ONLY verify their own email
  const [emailAddress, setEmailAddress] = useState(verifiedEmail || userEmail);
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes in seconds
  const [canResend, setCanResend] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // CRITICAL: Update isVerified when initialVerified prop changes (after refetch)
  useEffect(() => {
    console.log('[EmailVerification] initialVerified changed to:', initialVerified);
    setIsVerified(initialVerified);
  }, [initialVerified]);

  // Countdown timer
  useEffect(() => {
    if (step === 'verify' && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setCanResend(true);
            if (timerRef.current) clearInterval(timerRef.current);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
      };
    }
  }, [step, timeLeft]);

  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSendCode = async () => {
    // NO frontend validation - let backend handle everything
    setIsLoading(true);
    setError(null);

    try {
      console.log('[EmailVerification] Sending code to:', emailAddress);
      const response = await api.post('/kyc/email/send', { email_address: emailAddress });
      console.log('[EmailVerification] Code sent successfully:', response.data);
      
      // Reset timer and move to verify step
      setTimeLeft(600); // 10 minutes
      setCanResend(false);
      setStep('verify');
    } catch (err: any) {
      console.error('[EmailVerification] Error sending code:', err);
      let errorMsg = 'Unable to send verification code. Please try again.';
      
      if (err.response?.status === 400) {
        errorMsg = 'Invalid email address format. Please check and try again.';
      } else if (err.response?.status === 409) {
        // Check if it's specifically "already verified" error
        const detail = err.response?.data?.detail || '';
        if (detail.toLowerCase().includes('already verified')) {
          // Email already verified - trigger refetch WITHOUT reload
          // The parent component will refetch and React will automatically update the UI
          console.log('[EmailVerification] Email already verified, triggering refetch');
          if (onSuccess) {
            onSuccess(); // Trigger refetch - parent will update initialVerified prop
          }
          return; // Don't show error or change step
        } else {
          // Other conflict error
          errorMsg = detail || 'Email verification conflict. Please try again.';
        }
      } else if (err.response?.status === 429) {
        errorMsg = 'Too many attempts. Please wait a few minutes and try again.';
      } else if (!err.response) {
        // Network error or request didn't reach backend
        errorMsg = 'Network error. Please check your connection and try again.';
      }
      
      setError(errorMsg);
      if (onError) onError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter the 6-digit code');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/kyc/email/verify', { code: verificationCode });
      console.log('[EmailVerification] Code verified:', response.data);
      
      setStep('success');
      if (onSuccess) onSuccess();
    } catch (err: any) {
      console.error('[EmailVerification] Error verifying code:', err);
      let errorMsg = 'Invalid verification code. Please try again.';
      
      if (err.response?.status === 400) {
        const detail = err.response?.data?.detail || '';
        if (detail.includes('expired')) {
          errorMsg = 'Verification code expired. Please request a new code.';
        }
      }
      
      setError(errorMsg);
      if (onError) onError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setVerificationCode('');
    setError(null);
    setCanResend(false);
    await handleSendCode();
  };

  // ALWAYS show success state if email is verified (isVerified state from prop)
  // This ensures the green card persists after page refresh - EXACTLY like Persona card
  if (isVerified) {
    return (
      <div className="bg-[#10B981]/10 border border-[#10B981]/20 rounded-lg p-6 h-full flex flex-col">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-[#10B981] rounded-full flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">Email Verified</h3>
            <p className="text-sm text-[#94A3B8] mb-3">
              Your email address has been successfully verified
            </p>
            <div className="bg-[#0F172A] border border-[#334155] rounded-lg p-3">
              <div className="flex items-center gap-2 text-[#10B981]">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span className="font-medium text-sm">{verifiedEmail || emailAddress || userEmail}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // If NOT verified, show the active verification form (NO disabled state)
  console.log('[EmailVerification] Rendering form, step:', step);

  return (
    <div className="bg-[#1E293B] border border-[#334155] rounded-lg p-6 h-full flex flex-col">
      <div className="flex items-start gap-4 mb-4 flex-1">
        <div className="w-12 h-12 bg-[#3B82F6]/10 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">Email Verification</h3>
          <p className="text-sm text-[#94A3B8] mb-4">
            Verify your email address with a verification code
          </p>

          {error && (
            <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-3 mb-4">
              <p className="text-sm text-[#EF4444]">{error}</p>
            </div>
          )}

          {step === 'input' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Email Address
                </label>
                {/* SECURITY: Email is READ-ONLY - user can only verify their registered email */}
                <input
                  type="email"
                  value={emailAddress}
                  readOnly
                  disabled
                  className="w-full bg-[#0F172A] border border-[#334155] rounded-lg px-4 py-3 text-[#F8FAFC] placeholder-[#64748B] opacity-75 cursor-not-allowed"
                />
                <p className="text-xs text-[#64748B] mt-1">
                  This is your registered email address. To change it, update your account settings first.
                </p>
              </div>

              <Button
                variant="primary"
                size="md"
                onClick={handleSendCode}
                disabled={isLoading || !emailAddress}
                className="w-full gap-2"
              >
                {isLoading ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending Code...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Send Verification Code
                  </>
                )}
              </Button>
            </div>
          )}

          {step === 'verify' && (
            <div className="space-y-4">
              {/* Timer Display */}
              <div className="bg-[#0F172A] border border-[#334155] rounded-lg p-4 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-medium text-[#94A3B8]">Code expires in</span>
                </div>
                <div className={`text-3xl font-bold font-mono ${timeLeft <= 60 ? 'text-[#EF4444]' : 'text-[#3B82F6]'}`}>
                  {formatTime(timeLeft)}
                </div>
                {timeLeft === 0 && (
                  <p className="text-xs text-[#EF4444] mt-2">Code expired. Please request a new one.</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Verification Code
                </label>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  maxLength={6}
                  className="w-full bg-[#0F172A] border border-[#334155] rounded-lg px-4 py-3 text-center text-2xl font-mono text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] tracking-widest"
                  autoFocus
                />
                <p className="text-xs text-[#64748B] mt-1 text-center">
                  Enter the 6-digit code sent to <span className="text-[#3B82F6] font-medium">{emailAddress}</span>
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  size="md"
                  onClick={handleResendCode}
                  disabled={isLoading || !canResend}
                  className="flex-1 gap-2"
                  title={!canResend ? 'Wait for timer to expire' : 'Send a new code'}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {canResend ? 'Resend Code' : `Resend (${formatTime(timeLeft)})`}
                </Button>
                <Button
                  variant="primary"
                  size="md"
                  onClick={handleVerifyCode}
                  disabled={isLoading || verificationCode.length !== 6 || timeLeft === 0}
                  className="flex-1 gap-2"
                >
                  {isLoading ? (
                    <>
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Verifying...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Verify Code
                    </>
                  )}
                </Button>
              </div>

              <button
                onClick={() => {
                  setStep('input');
                  setVerificationCode('');
                  setError(null);
                  if (timerRef.current) clearInterval(timerRef.current);
                }}
                className="w-full text-sm text-[#64748B] hover:text-[#94A3B8] transition-colors"
              >
                ← Change email address
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
