'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';

// Add global styles for Persona modal
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    .persona-modal-overlay {
      z-index: 9999 !important;
    }
    .persona-modal-container {
      max-width: 800px !important;
      width: 90vw !important;
      margin: 0 auto !important;
    }
    iframe[src*="withpersona.com"] {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 600px !important;
    }
  `;
  if (!document.getElementById('persona-custom-styles')) {
    style.id = 'persona-custom-styles';
    document.head.appendChild(style);
  }
}

interface CompleteVerificationProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function CompleteVerification({ onSuccess, onError }: CompleteVerificationProps) {
  const user = useAuthStore((state) => state.user);
  
  // Persona KYC state
  const [personaStatus, setPersonaStatus] = useState<string>('not_started');
  const [isLoadingPersona, setIsLoadingPersona] = useState(false);
  const [personaError, setPersonaError] = useState<string | null>(null);
  
  // SMS Verification state
  const [phoneNumber, setPhoneNumber] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [phoneVerified, setPhoneVerified] = useState(false);
  const [isLoadingSMS, setIsLoadingSMS] = useState(false);
  const [smsError, setSmsError] = useState<string | null>(null);
  const [codeSent, setCodeSent] = useState(false);
  const [canVerifyPhone, setCanVerifyPhone] = useState(false);

  useEffect(() => {
    checkVerificationStatus();
  }, []);

  const checkVerificationStatus = async () => {
    try {
      const response = await api.get('/kyc/persona/status');
      setPersonaStatus(response.data.persona_status || 'not_started');
      setPhoneVerified(response.data.phone_verified || false);
      setCanVerifyPhone(response.data.can_verify_phone || false);
      setPhoneNumber(response.data.phone_number || '');
    } catch (err: any) {
      console.error('Failed to check verification status:', err);
    }
  };

  const startPersonaVerification = async () => {
    setIsLoadingPersona(true);
    setPersonaError(null);

    try {
      const response = await api.post('/kyc/persona/start');
      const { inquiry_id, template_id } = response.data;

      if (!inquiry_id || !template_id) {
        throw new Error('Unable to initialize verification');
      }

      // Load Persona SDK
      if (typeof window !== 'undefined' && !(window as any).Persona) {
        const script = document.createElement('script');
        script.src = 'https://cdn.withpersona.com/dist/persona-v4.9.0.js';
        script.async = true;
        script.onload = () => launchPersonaFlow(inquiry_id);
        script.onerror = () => {
          setPersonaError('Failed to load verification system');
          setIsLoadingPersona(false);
        };
        document.body.appendChild(script);
      } else {
        launchPersonaFlow(inquiry_id);
      }
    } catch (err: any) {
      setPersonaError('Unable to start verification');
      setIsLoadingPersona(false);
    }
  };

  const launchPersonaFlow = (inquiryId: string) => {
    const Persona = (window as any).Persona;
    if (!Persona) {
      setPersonaError('Persona SDK not available');
      setIsLoadingPersona(false);
      return;
    }

    try {
      const client = new Persona.Client({
        inquiryId,
        environment: process.env.NEXT_PUBLIC_PERSONA_ENVIRONMENT || 'sandbox',
        onReady: () => client.open(),
        onComplete: async () => {
          // Verify with backend and refresh status
          try {
            await api.post(`/kyc/persona/verify?inquiry_id=${inquiryId}`);
          } catch (err) {
            console.error('Failed to verify inquiry:', err);
          }
          await checkVerificationStatus();
          setIsLoadingPersona(false);
        },
        onCancel: () => {
          setPersonaError('Verification cancelled');
          setIsLoadingPersona(false);
        },
        onError: () => {
          setPersonaError('Verification error occurred');
          setIsLoadingPersona(false);
        }
      });
    } catch (err: any) {
      setPersonaError('Failed to initialize verification');
      setIsLoadingPersona(false);
    }
  };

  const sendSMSCode = async () => {
    if (!phoneNumber) {
      setSmsError('Please enter your phone number');
      return;
    }

    setIsLoadingSMS(true);
    setSmsError(null);

    try {
      await api.post('/kyc/phone/send', null, {
        params: { phone_number: phoneNumber }
      });
      setCodeSent(true);
      setSmsError(null);
    } catch (err: any) {
      setSmsError(err.response?.data?.detail || 'Failed to send SMS');
    } finally {
      setIsLoadingSMS(false);
    }
  };

  const verifySMSCode = async () => {
    if (!verificationCode) {
      setSmsError('Please enter the verification code');
      return;
    }

    setIsLoadingSMS(true);
    setSmsError(null);

    try {
      await api.post('/kyc/phone/verify', null, {
        params: { code: verificationCode }
      });
      setPhoneVerified(true);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setSmsError(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setIsLoadingSMS(false);
    }
  };

  // Fully verified
  if ((personaStatus === 'completed' || personaStatus === 'approved') && phoneVerified) {
    return (
      <div className="bg-[#10B981]/10 border border-[#10B981]/20 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-[#10B981] rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#2d2a26]">Fully Verified ✅</h3>
            <p className="text-sm text-[#6d6760]">Your identity and phone number are verified</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Step 1: Persona KYC */}
      <div className="bg-[#faf6f1] border border-[#e6ddd4] rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
            (personaStatus === 'completed' || personaStatus === 'approved') ? 'bg-[#10B981]' : 'bg-[#3B82F6]'
          }`}>
            {(personaStatus === 'completed' || personaStatus === 'approved') ? (
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <span className="text-white font-bold">1</span>
            )}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-[#2d2a26] mb-2">
              Step 1: Identity Verification (KYC)
            </h3>
            <p className="text-sm text-[#6d6760] mb-4">
              Verify your identity with a government-issued ID
            </p>
            
            {(personaStatus === 'completed' || personaStatus === 'approved') ? (
              <div className="flex items-center gap-2 text-sm text-[#10B981]">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Identity verified
              </div>
            ) : (
              <>
                {personaError && (
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-3 mb-4">
                    <p className="text-sm text-[#EF4444]">{personaError}</p>
                  </div>
                )}
                <Button 
                  variant="primary" 
                  size="md" 
                  onClick={startPersonaVerification} 
                  disabled={isLoadingPersona}
                >
                  {isLoadingPersona ? 'Starting...' : 'Start ID Verification'}
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Step 2: SMS Verification */}
      <div className={`bg-[#faf6f1] border border-[#e6ddd4] rounded-lg p-6 ${
        !canVerifyPhone ? 'opacity-50' : ''
      }`}>
        <div className="flex items-start gap-4">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
            phoneVerified ? 'bg-[#10B981]' : canVerifyPhone ? 'bg-[#3B82F6]' : 'bg-[#6b7280]'
          }`}>
            {phoneVerified ? (
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <span className="text-white font-bold">2</span>
            )}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-[#2d2a26] mb-2">
              Step 2: Phone Verification (SMS)
            </h3>
            <p className="text-sm text-[#6d6760] mb-4">
              {canVerifyPhone 
                ? 'Verify your phone number with an SMS code'
                : 'Complete Step 1 first to unlock phone verification'
              }
            </p>
            
            {canVerifyPhone && !phoneVerified && (
              <div className="space-y-4">
                {!codeSent ? (
                  <div>
                    <label className="block text-sm font-semibold text-[#2d2a26] mb-2">
                      Phone Number
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="tel"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        placeholder="+251912345678"
                        className="flex-1 rounded-lg border border-[#d8d0c8] px-4 py-2 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                      />
                      <Button 
                        variant="primary" 
                        size="md" 
                        onClick={sendSMSCode} 
                        disabled={isLoadingSMS}
                      >
                        {isLoadingSMS ? 'Sending...' : 'Send Code'}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-semibold text-[#2d2a26] mb-2">
                      Verification Code
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={verificationCode}
                        onChange={(e) => setVerificationCode(e.target.value)}
                        placeholder="123456"
                        maxLength={6}
                        className="flex-1 rounded-lg border border-[#d8d0c8] px-4 py-2 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                      />
                      <Button 
                        variant="primary" 
                        size="md" 
                        onClick={verifySMSCode} 
                        disabled={isLoadingSMS}
                      >
                        {isLoadingSMS ? 'Verifying...' : 'Verify'}
                      </Button>
                    </div>
                    <button
                      onClick={() => setCodeSent(false)}
                      className="text-xs text-[#8b8177] hover:text-[#6d6760] mt-2"
                    >
                      Change phone number
                    </button>
                  </div>
                )}
                
                {smsError && (
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-3">
                    <p className="text-sm text-[#EF4444]">{smsError}</p>
                  </div>
                )}
              </div>
            )}
            
            {phoneVerified && (
              <div className="flex items-center gap-2 text-sm text-[#10B981]">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Phone verified: {phoneNumber}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
