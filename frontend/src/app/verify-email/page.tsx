'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import Header from '@/components/layout/Header';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001';

function VerifyEmailPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resendVerification = useAuthStore((state) => state.resendVerification);
  
  const [status, setStatus] = useState<'loading' | 'error' | 'waiting'>('loading');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');
    const waiting = searchParams.get('waiting');
    const emailParam = searchParams.get('email');
    
    if (token) {
      setMessage('Redirecting to email verification...');
      window.location.replace(`${API_URL}/api/v1/registration/verify-email?token=${encodeURIComponent(token)}`);
      return;
    }

    if (waiting === 'true' && emailParam) {
      setStatus('waiting');
      setEmail(emailParam);
      setMessage('Registration successful! Please check your email and click the verification link to activate your account.');
      return;
    }
    
    setStatus('error');
    setMessage('Invalid verification link. Please check your email for the correct link.');
  }, [searchParams]);

  const handleResendVerification = async () => {
    if (!email) {
      alert('Please enter your email address');
      return;
    }

    setIsResending(true);
    try {
      await resendVerification(email);
      alert('Verification email sent! Please check your inbox.');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to send verification email');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <>
      <Header />
      <div className="min-h-screen flex items-center justify-center bg-gray-50 pt-16">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Email Verification
            </h2>
            
            {status === 'waiting' && (
              <div className="space-y-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="text-center">
                  <p className="text-blue-600 font-medium text-lg mb-2">{message}</p>
                  <p className="text-gray-600 mb-4">We've sent a verification link to:</p>
                  <p className="font-medium text-gray-800 mb-6">{email}</p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <h4 className="font-medium text-blue-800 mb-2">Next Steps:</h4>
                    <ol className="text-sm text-blue-700 space-y-1 text-left">
                      <li>1. Check your email inbox</li>
                      <li>2. Look for an email from FindBug Platform</li>
                      <li>3. Click the "Verify Email Address" button</li>
                      <li>4. Your account will be activated automatically</li>
                    </ol>
                  </div>
                  <p className="text-sm text-gray-500">
                    Didn't receive the email? Check your spam folder or request a new one below.
                  </p>
                </div>
              </div>
            )}
            
            {status === 'loading' && (
              <div className="space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-600">{message || 'Verifying your email...'}</p>
              </div>
            )}
            
            {status === 'error' && (
              <div className="space-y-6">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <p className="text-red-600 font-medium">{message}</p>
                
                <div className="border-t pt-6">
                  <p className="text-gray-600 mb-4">Need a new verification email?</p>
                  <div className="space-y-3">
                    <input
                      type="email"
                      placeholder="Enter your email address"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={handleResendVerification}
                      disabled={isResending}
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isResending ? 'Sending...' : 'Resend Verification Email'}
                    </button>
                  </div>
                </div>
              </div>
            )}
            
            <div className="mt-8">
              <button
                onClick={() => router.push('/auth/login')}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Back to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function VerifyEmailPageFallback() {
  return (
    <>
      <Header />
      <div className="flex min-h-screen items-center justify-center bg-[#f5f1ec] pt-16">
        <div className="rounded-3xl border border-[#ddd4cb] bg-white dark:bg-[#111111] px-6 py-5 text-sm text-[#6d6760] shadow-sm">
          Loading email verification...
        </div>
      </div>
    </>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<VerifyEmailPageFallback />}>
      <VerifyEmailPageContent />
    </Suspense>
  );
}
