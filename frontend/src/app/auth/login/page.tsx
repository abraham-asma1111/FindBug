'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import Header from '@/components/layout/Header';
import { getDashboardRouteForRole } from '@/lib/portal';
import { API_URL } from '@/lib/api';

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [showMFA, setShowMFA] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showVerificationSuccess, setShowVerificationSuccess] = useState(false);

  useEffect(() => {
    const verified = searchParams.get('verified');
    const errorMessage = searchParams.get('error');
    let timeoutId: number | undefined;
    
    if (verified === 'true') {
      setShowVerificationSuccess(true);
      timeoutId = window.setTimeout(() => {
        setShowVerificationSuccess(false);
      }, 5000);
    }
    
    if (errorMessage) {
      setError(decodeURIComponent(errorMessage));
    }

    return () => {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const user = await login(email, password, mfaCode || undefined);
      router.replace(getDashboardRouteForRole(user.role));
    } catch (err: any) {
      if (err.mfaRequired) {
        setShowMFA(true);
        setError('Please enter your 6-digit MFA code');
      } else {
        const errorMessage = err.response?.data?.detail
          || (err.request ? `Cannot reach backend at ${API_URL}. Restart the frontend after env changes and make sure the API server is running there.` : null)
          || err.message
          || 'Login failed. Please try again.';
        
        if (errorMessage.includes('MFA') || errorMessage.includes('two-factor')) {
          setShowMFA(true);
          setError('Please enter your 6-digit MFA code');
        } else {
          setError(errorMessage);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="min-h-screen flex pt-16">
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-gray-900 to-black items-center justify-center p-12 fixed left-0 top-16 bottom-0">
          <div className="text-center">
            <h1 className="text-6xl font-bold text-white mb-4">FindBug</h1>
            <p className="text-2xl text-gray-300 mb-8">
              PAY A REWARD<br />NOT A RANSOM
            </p>
            <p className="text-gray-400 text-lg">
              Welcome back to the community
            </p>
          </div>
        </div>

        <div className="w-full lg:w-1/2 lg:ml-[50%] flex items-start justify-center p-8 bg-white dark:bg-[#111111] min-h-screen pt-24">
          <div className="max-w-md w-full py-4">
            <div className="mb-8 text-center">
              <h2 className="text-3xl font-bold text-black mb-2">SIGN IN</h2>
              <p className="text-gray-600">Welcome back! Please login to your account.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {showVerificationSuccess && (
                <div className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 text-sm">
                  ✅ Email verified successfully! You can now log in to your account.
                </div>
              )}
              
              {error && (
                <div className="bg-red-50 border-l-4 border-danger text-danger px-4 py-3 text-sm">
                  {error}
                </div>
              )}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-black mb-2">
                  Email Address <span className="text-danger">*</span>
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 focus:outline-none focus:border-primary text-black"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-black mb-2">
                  Password <span className="text-danger">*</span>
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 focus:outline-none focus:border-primary text-black"
                  placeholder="••••••••"
                />
              </div>

              {showMFA && (
                <div>
                  <label htmlFor="mfaCode" className="block text-sm font-medium text-black mb-2">
                    MFA Code <span className="text-danger">*</span>
                  </label>
                  <input
                    id="mfaCode"
                    type="text"
                    required={showMFA}
                    value={mfaCode}
                    onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    className="w-full px-4 py-3 border border-gray-300 focus:outline-none focus:border-primary text-black text-center font-mono"
                    placeholder="123456"
                    maxLength={6}
                  />
                  <p className="text-sm text-gray-600 mt-1">
                    Enter the 6-digit code from your authenticator app
                  </p>
                </div>
              )}

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" />
                  <span className="text-gray-700">Remember me</span>
                </label>
                <Link href="/auth/forgot-password" className="text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-primary text-white py-3 font-medium hover:bg-primary-hover transition-colors disabled:bg-gray-400"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-gray-600">Don't have an account? </span>
              <Link href="/auth/register" className="text-primary font-medium hover:underline">
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function LoginPageFallback() {
  return (
    <>
      <Header />
      <div className="flex min-h-screen items-center justify-center bg-[#f5f1ec] pt-16">
        <div className="rounded-3xl border border-[#ddd4cb] bg-white dark:bg-[#111111] px-6 py-5 text-sm text-[#6d6760] shadow-sm">
          Loading sign-in workspace...
        </div>
      </div>
    </>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginPageFallback />}>
      <LoginPageContent />
    </Suspense>
  );
}
