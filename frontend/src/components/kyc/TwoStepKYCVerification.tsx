'use client';

import PersonaVerification from './PersonaVerification';
import EmailVerification from './EmailVerification';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useAuthStore } from '@/store/authStore';

interface TwoStepKYCVerificationProps {
  onComplete?: () => void;
}

export default function TwoStepKYCVerification({ onComplete }: TwoStepKYCVerificationProps) {
  // COMPLETELY INDEPENDENT: Persona and Email are separate systems
  const { data: personaStatus, refetch: refetchPersona, error: personaError } = useApiQuery('/kyc/persona/status');
  const { data: emailStatus, refetch: refetchEmail, error: emailError } = useApiQuery('/kyc/email/status');
  
  // Get current user from auth store (more reliable than API call)
  const user = useAuthStore((state) => state.user);

  // Debug logging - CRITICAL for diagnosing state issues
  console.log('[TwoStepKYC] personaStatus:', personaStatus);
  console.log('[TwoStepKYC] emailStatus:', emailStatus);
  console.log('[TwoStepKYC] emailStatus?.email_verified:', emailStatus?.email_verified);
  console.log('[TwoStepKYC] typeof emailStatus?.email_verified:', typeof emailStatus?.email_verified);
  console.log('[TwoStepKYC] user from store:', user);

  // Persona is approved when status is "approved"
  const personaApproved = personaStatus?.status === 'approved';
  
  // Email verification status - ONLY from /kyc/email/status endpoint
  // CRITICAL: Convert to boolean explicitly to ensure React detects changes
  const emailVerified = Boolean(
    emailStatus?.email_verified === true || 
    emailStatus?.email_verified === 'true' || 
    emailStatus?.email_verified === 1 ||
    emailStatus?.email_verified === '1'
  );
  
  // Get email address from email status endpoint
  const verifiedEmail = emailStatus?.email_address;
  
  // SECURITY: Get user's registered email from auth store (most reliable)
  const userEmail = user?.email || '';
  
  console.log('[TwoStepKYC] Raw emailStatus:', emailStatus);
  console.log('[TwoStepKYC] emailVerified (computed):', emailVerified, 'type:', typeof emailVerified);
  console.log('[TwoStepKYC] verifiedEmail:', verifiedEmail);
  console.log('[TwoStepKYC] userEmail:', userEmail);
  
  // Email verification is ALWAYS enabled for independent testing
  const emailEnabled = true;

  const handlePersonaSuccess = () => {
    refetchPersona();
    refetchEmail(); // Refresh email status
  };

  const handleEmailSuccess = () => {
    refetchEmail();
    if (onComplete) onComplete();
  };

  // Show friendly error if API fails
  if (personaError || emailError) {
    return (
      <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <svg className="w-6 h-6 text-[#EF4444]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h3 className="text-lg font-bold text-[#F8FAFC]">Unable to Load Verification</h3>
            <p className="text-sm text-[#94A3B8]">Please refresh the page or contact support if the issue persists.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Two cards side-by-side on desktop, stacked on mobile - EQUAL HEIGHT */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        {/* Step 1: Persona Identity Verification */}
        <div className="relative h-full">
          <div className="absolute -left-4 top-4 flex items-center justify-center w-8 h-8 bg-[#3B82F6] text-white rounded-full font-bold text-sm z-10">
            1
          </div>
          <div className="h-full">
            <PersonaVerification onSuccess={handlePersonaSuccess} />
          </div>
        </div>

        {/* Step 2: Email Verification */}
        <div className="relative h-full">
          <div className={`absolute -left-4 top-4 flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm z-10 bg-[#3B82F6] text-white`}>
            2
          </div>
          <div className="h-full">
            <EmailVerification 
              enabled={emailEnabled}
              onSuccess={handleEmailSuccess}
              initialVerified={emailVerified}
              verifiedEmail={verifiedEmail}
              userEmail={userEmail}
            />
          </div>
        </div>
      </div>

      {/* Completion Message */}
      {personaApproved && emailVerified && (
        <div className="bg-[#10B981]/10 border border-[#10B981]/20 rounded-lg p-6 text-center">
          <div className="w-16 h-16 bg-[#10B981] rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-[#F8FAFC] mb-2">Verification Complete!</h3>
          <p className="text-[#94A3B8]">
            Your identity and email have been successfully verified. You can now receive payments.
          </p>
        </div>
      )}
    </div>
  );
}
