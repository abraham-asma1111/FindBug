'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Header from '@/components/layout/Header';
import api from '@/lib/api';

function VerifyOTPPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isResending, setIsResending] = useState(false);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes in seconds

  useEffect(() => {
    const emailParam = searchParams.get('email');
    if (emailParam) {
      setEmail(emailParam);
    } else {
      router.push('/auth/register');
    }
  }, [searchParams, router]);

  // Countdown timer
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) return; // Only allow single digit
    if (!/^\d*$/.test(value)) return; // Only allow numbers

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      const nextInput = document.getElementById(`otp-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      const prevInput = document.getElementById(`otp-${index - 1}`);
      prevInput?.focus();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const otpCode = otp.join('');
    
    if (otpCode.length !== 6) {
      setError('Please enter all 6 digits');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await api.post('/registration/verify-otp', {
        email: email,
        otp: otpCode
      });

      alert('Registration completed successfully! You can now log in.');
      router.push('/auth/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setIsResending(true);
    setError('');

    try {
      await api.post('/registration/resend-otp', { email });
      setTimeLeft(600); // Reset timer
      setOtp(['', '', '', '', '', '']); // Clear current OTP
      alert('New verification code sent to your email!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to resend verification code');
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
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Verify Your Email
            </h2>
            <p className="text-gray-600 mb-8">
              We sent a 6-digit code to<br />
              <span className="font-medium text-gray-900">{email}</span>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            {/* OTP Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4 text-center">
                Enter verification code
              </label>
              <div className="flex justify-center space-x-3">
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    id={`otp-${index}`}
                    type="text"
                    value={digit}
                    onChange={(e) => handleOtpChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    className="w-12 h-12 text-center text-xl font-bold border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                    maxLength={1}
                  />
                ))}
              </div>
            </div>

            {/* Timer */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Code expires in: <span className="font-mono font-medium text-red-600">{formatTime(timeLeft)}</span>
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || otp.join('').length !== 6}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isLoading ? 'Verifying...' : 'Verify & Complete Registration'}
            </button>
          </form>

          {/* Resend Section */}
          <div className="text-center space-y-4">
            <p className="text-sm text-gray-600">
              Didn't receive the code?
            </p>
            <button
              onClick={handleResendOTP}
              disabled={isResending || timeLeft > 540} // Allow resend after 1 minute
              className="text-blue-600 hover:text-blue-800 font-medium disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              {isResending ? 'Sending...' : 'Resend verification code'}
            </button>
            {timeLeft > 540 && (
              <p className="text-xs text-gray-500">
                You can resend in {formatTime(timeLeft - 540)}
              </p>
            )}
          </div>

          {/* Back to Registration */}
          <div className="text-center">
            <button
              onClick={() => router.push('/auth/register')}
              className="text-gray-600 hover:text-gray-800 font-medium"
            >
              ← Back to Registration
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function VerifyOTPPageFallback() {
  return (
    <>
      <Header />
      <div className="flex min-h-screen items-center justify-center bg-[#f5f1ec] pt-16">
        <div className="rounded-3xl border border-[#ddd4cb] bg-white px-6 py-5 text-sm text-[#6d6760] shadow-sm">
          Loading verification flow...
        </div>
      </div>
    </>
  );
}

export default function VerifyOTPPage() {
  return (
    <Suspense fallback={<VerifyOTPPageFallback />}>
      <VerifyOTPPageContent />
    </Suspense>
  );
}
