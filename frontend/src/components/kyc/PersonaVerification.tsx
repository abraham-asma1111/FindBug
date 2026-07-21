'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';

// Add global styles for Persona modal
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    /* Persona modal full-width styles */
    .persona-modal-overlay {
      z-index: 9999 !important;
    }
    
    .persona-modal-container {
      max-width: 800px !important;
      width: 90vw !important;
      margin: 0 auto !important;
    }
    
    /* Ensure Persona iframe is responsive */
    iframe[src*="withpersona.com"] {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 600px !important;
    }
    
    /* Persona embedded flow container */
    #persona-embedded-flow {
      max-width: 800px !important;
      width: 100% !important;
      margin: 0 auto !important;
    }
  `;
  if (!document.getElementById('persona-custom-styles')) {
    style.id = 'persona-custom-styles';
    document.head.appendChild(style);
  }
}

interface PersonaVerificationProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function PersonaVerification({ onSuccess, onError }: PersonaVerificationProps) {
  const user = useAuthStore((state) => state.user);
  const [isLoading, setIsLoading] = useState(false);
  const [inquiryId, setInquiryId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('not_started');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check current verification status on mount only
    checkVerificationStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const checkVerificationStatus = async () => {
    try {
      const response = await api.get('/kyc/persona/status');
      console.log('[PersonaVerification] Status response:', response.data);
      setStatus(response.data.status);
      setInquiryId(response.data.persona_inquiry_id);
    } catch (err: any) {
      console.error('[PersonaVerification] Failed to check verification status:', err);
    }
  };

  const startVerification = async () => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('[PersonaVerification] Starting verification...');
      
      // Start Persona verification
      const response = await api.post('/kyc/persona/start');
      console.log('[PersonaVerification] API response:', response.data);
      
      const { inquiry_id, template_id, session_token } = response.data;

      if (!inquiry_id || !template_id) {
        throw new Error('Unable to initialize verification. Please try again.');
      }

      setInquiryId(inquiry_id);

      // Load Persona SDK dynamically
      if (typeof window !== 'undefined' && !(window as any).Persona) {
        console.log('[PersonaVerification] Loading Persona SDK...');
        const script = document.createElement('script');
        script.src = 'https://cdn.withpersona.com/dist/persona-v4.9.0.js';
        script.async = true;
        script.onload = () => {
          console.log('[PersonaVerification] Persona SDK loaded');
          launchPersonaFlow(inquiry_id, template_id, session_token);
        };
        script.onerror = () => {
          console.error('[PersonaVerification] Failed to load Persona SDK');
          setError('Unable to load verification system. Please check your internet connection.');
          setIsLoading(false);
        };
        document.body.appendChild(script);
      } else {
        console.log('[PersonaVerification] Persona SDK already loaded');
        launchPersonaFlow(inquiry_id, template_id, session_token);
      }
    } catch (err: any) {
      console.error('[PersonaVerification] Error starting verification:', err);
      // Show user-friendly error message (hide technical details)
      const errorMsg = 'Unable to start verification. Please try again or contact support.';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      setIsLoading(false);
    }
  };

  const launchPersonaFlow = (inquiryId: string, templateId: string, sessionToken?: string) => {
    console.log('[PersonaVerification] Launching Persona flow...', { inquiryId, templateId, hasSessionToken: !!sessionToken });
    
    const Persona = (window as any).Persona;

    if (!Persona) {
      console.error('[PersonaVerification] Persona SDK not available');
      setError('Persona SDK failed to load');
      setIsLoading(false);
      return;
    }

    try {
      // Use inquiryId to RESUME the existing inquiry created by backend
      // This ensures the inquiry ID matches what's in our database
      const clientConfig: any = {
        inquiryId: inquiryId, // CRITICAL: Resume the inquiry created by backend
        environment: 'sandbox',
        onReady: () => {
          console.log('[PersonaVerification] Persona client ready');
          setIsLoading(false); // Stop loading spinner when ready
        },
        onLoad: () => {
          console.log('[PersonaVerification] Persona modal loaded');
        },
        onComplete: async ({ inquiryId: completedInquiryId }: { inquiryId: string }) => {
          console.log('[PersonaVerification] Verification completed:', completedInquiryId);
          
          // Verify with backend
          try {
            await api.post('/kyc/persona/verify', null, {
              params: { inquiry_id: completedInquiryId }
            });
            
            setStatus('approved');
            if (onSuccess) onSuccess();
          } catch (err: any) {
            console.error('[PersonaVerification] Verification failed:', err);
            const errorMsg = err.response?.data?.detail || 'Verification failed';
            setError(errorMsg);
            if (onError) onError(errorMsg);
          } finally {
            setIsLoading(false);
          }
        },
        onCancel: ({ inquiryId: cancelledInquiryId }: { inquiryId: string }) => {
          console.log('[PersonaVerification] Verification cancelled:', cancelledInquiryId);
          setError('Verification cancelled');
          setIsLoading(false);
        },
        onError: (error: any) => {
          console.error('[PersonaVerification] Persona error:', error);
          setError(`Verification error: ${error.message || 'Unknown error'}`);
          if (onError) onError('Verification error occurred');
          setIsLoading(false);
        }
      };

      console.log('[PersonaVerification] Creating Persona client with config:', clientConfig);
      const client = new Persona.Client(clientConfig);
      console.log('[PersonaVerification] Persona client created, calling open()...');
      
      // Open the modal
      client.open();
      
    } catch (err: any) {
      console.error('[PersonaVerification] Error creating Persona client:', err);
      setError(`Failed to initialize verification: ${err.message}`);
      setIsLoading(false);
    }
  };

  if (status === 'approved') {
    return (
      <div className="bg-[#10B981]/10 border border-[#10B981]/20 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-12 h-12 bg-[#10B981] rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#F8FAFC]">Identity Verified</h3>
            <p className="text-sm text-[#94A3B8]">Your identity has been successfully verified</p>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'pending') {
    return (
      <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/20 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-12 h-12 bg-[#F59E0B] rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#F8FAFC]">Verification In Progress</h3>
            <p className="text-sm text-[#94A3B8]">Your verification is being reviewed</p>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'rejected') {
    return (
      <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-12 h-12 bg-[#EF4444] rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#F8FAFC]">Verification Failed</h3>
            <p className="text-sm text-[#94A3B8]">Your verification was not successful</p>
          </div>
        </div>
        <Button variant="primary" size="sm" onClick={startVerification} disabled={isLoading}>
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="bg-[#1E293B] border border-[#334155] rounded-lg p-6">
      <div className="flex items-start gap-4 mb-4">
        <div className="w-12 h-12 bg-[#3B82F6]/10 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">Identity Verification Required</h3>
          <p className="text-sm text-[#94A3B8] mb-4">
            To receive payments, you need to verify your identity. This process takes about 2-3 minutes.
          </p>
          <ul className="space-y-2 mb-4">
            <li className="flex items-center gap-2 text-sm text-[#94A3B8]">
              <svg className="w-4 h-4 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Government-issued ID (Passport, National ID, or Driver's License)
            </li>
            <li className="flex items-center gap-2 text-sm text-[#94A3B8]">
              <svg className="w-4 h-4 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Selfie photo for identity confirmation
            </li>
            {user?.role === 'organization' && (
              <li className="flex items-center gap-2 text-sm text-[#94A3B8]">
                <svg className="w-4 h-4 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Business documents (Trade License or Registration Certificate)
              </li>
            )}
          </ul>
          {error && (
            <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-3 mb-4">
              <p className="text-sm text-[#EF4444]">{error}</p>
            </div>
          )}
          <Button 
            variant="primary" 
            size="md" 
            onClick={startVerification} 
            disabled={isLoading}
            className="gap-2"
          >
            {isLoading ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Starting Verification...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Start Verification
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
