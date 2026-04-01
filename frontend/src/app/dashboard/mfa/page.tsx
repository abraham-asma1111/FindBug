'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import Header from '@/components/layout/Header';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import { getDashboardRouteForRole } from '@/lib/portal';

function MFASetupContent() {
  const router = useRouter();
  const { user, enableMFA, verifyMFASetup, disableMFA } = useAuthStore();
  
  const [step, setStep] = useState<'setup' | 'verify' | 'complete'>('setup');
  const [setupSecret, setSetupSecret] = useState('');
  const [setupUri, setSetupUri] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleEnableMFA = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const result = await enableMFA();
      setSetupSecret(result.secret);
      setSetupUri(result.qr_uri);
      setBackupCodes(result.backup_codes);
      setStep('verify');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to enable MFA');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyMFA = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      await verifyMFASetup(verificationCode);
      setStep('complete');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Invalid verification code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    if (!password) {
      setError('Please enter your password');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      await disableMFA(password);
      setStep('setup');
      setPassword('');
      setSetupSecret('');
      setSetupUri('');
      setBackupCodes([]);
      alert('MFA has been disabled successfully');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to disable MFA');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    user ? (
      <>
        <Header />
        <div className="min-h-screen bg-[#f5f1ec] pt-24">
          <div className="max-w-2xl mx-auto px-4 py-8">
            <div className="rounded-[2rem] border border-[#ddd4cb] bg-white p-8 shadow-sm">
              <h1 className="mb-8 text-3xl font-bold text-[#2d2a26]">
                Multi-Factor Authentication
              </h1>

              <div className="mb-8 rounded-3xl bg-[#faf6f1] p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-[#2d2a26]">MFA Status</h3>
                    <p className="text-sm text-[#6d6760]">
                      {user.mfaEnabled ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    user.mfaEnabled 
                      ? 'bg-[#eef7ef] text-[#24613a]' 
                      : 'bg-[#fde9e7] text-[#9d1f1f]'
                  }`}>
                    {user.mfaEnabled ? 'Secured' : 'Not Secured'}
                  </div>
                </div>
              </div>

              {error && (
                <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4">
                  <p className="text-red-600">{error}</p>
                </div>
              )}

              {!user.mfaEnabled && (
                <>
                  {step === 'setup' && (
                    <div className="space-y-6">
                      <div>
                        <h2 className="mb-4 text-xl font-semibold text-[#2d2a26]">
                          Enable Two-Factor Authentication
                        </h2>
                        <p className="mb-6 text-[#6d6760]">
                          Add an extra layer of security to your account by enabling two-factor authentication.
                          You'll need an authenticator app like Google Authenticator or Authy.
                        </p>
                      </div>

                      <div className="rounded-3xl bg-[#faf6f1] p-4">
                        <h3 className="mb-2 font-medium text-[#2d2a26]">Before you start:</h3>
                        <ul className="space-y-1 text-sm text-[#6d6760]">
                          <li>• Install an authenticator app on your phone</li>
                          <li>• Make sure you have access to your device</li>
                          <li>• Save the backup codes in a secure location</li>
                        </ul>
                      </div>

                      <button
                        onClick={handleEnableMFA}
                        disabled={isLoading}
                        className="w-full rounded-full bg-[#ef2330] px-4 py-3 font-medium text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isLoading ? 'Setting up...' : 'Enable MFA'}
                      </button>
                    </div>
                  )}

                  {step === 'verify' && (
                    <div className="space-y-6">
                      <div>
                        <h2 className="mb-4 text-xl font-semibold text-[#2d2a26]">
                          Connect your authenticator
                        </h2>
                        <p className="mb-6 text-[#6d6760]">
                          The backend returns an authenticator setup URI rather than an image, so use the secret below or paste the URI into a compatible authenticator app.
                        </p>
                      </div>

                      <div className="space-y-4 rounded-3xl bg-[#faf6f1] p-5">
                        <div>
                          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                            Manual setup key
                          </p>
                          <code className="mt-2 block rounded-2xl border border-[#ddd4cb] bg-white px-4 py-3 text-sm text-[#2d2a26]">
                            {setupSecret || 'Secret unavailable'}
                          </code>
                        </div>
                        <div>
                          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                            Setup URI
                          </p>
                          <code className="mt-2 block max-h-32 overflow-auto rounded-2xl border border-[#ddd4cb] bg-white px-4 py-3 text-sm text-[#2d2a26]">
                            {setupUri || 'URI unavailable'}
                          </code>
                        </div>
                      </div>

                      <div className="rounded-3xl bg-[#fff6e9] p-4">
                        <h3 className="mb-2 font-medium text-[#8a5b16]">
                          Save these backup codes
                        </h3>
                        <p className="mb-3 text-sm text-[#8a5b16]">
                          Store these codes in a safe place. You can use them to access your account if you lose your device.
                        </p>
                        <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                          {backupCodes.map((code, index) => (
                            <div key={index} className="bg-white p-2 rounded border">
                              {code}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <label className="mb-2 block text-sm font-medium text-[#4f4943]">
                          Enter verification code
                        </label>
                        <input
                          type="text"
                          value={verificationCode}
                          onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                          placeholder="123456"
                          className="w-full rounded-2xl border border-[#d5ccc3] px-3 py-2 text-center text-lg font-mono text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
                          maxLength={6}
                        />
                      </div>

                      <div className="flex space-x-4">
                        <button
                          onClick={() => setStep('setup')}
                          className="flex-1 rounded-full bg-[#efe8df] px-4 py-2 text-[#4f4943] transition hover:bg-[#e5dbd0]"
                        >
                          Back
                        </button>
                        <button
                          onClick={handleVerifyMFA}
                          disabled={isLoading || verificationCode.length !== 6}
                          className="flex-1 rounded-full bg-[#ef2330] px-4 py-2 text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {isLoading ? 'Verifying...' : 'Verify & Enable'}
                        </button>
                      </div>
                    </div>
                  )}

                  {step === 'complete' && (
                    <div className="text-center space-y-6">
                      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[#eef7ef]">
                        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <h2 className="mb-2 text-xl font-semibold text-[#24613a]">
                          MFA Enabled Successfully!
                        </h2>
                        <p className="text-[#6d6760]">
                          Your account is now protected with two-factor authentication.
                        </p>
                      </div>
                      <button
                        onClick={() => router.push(getDashboardRouteForRole(user.role))}
                        className="rounded-full bg-[#ef2330] px-6 py-2 text-white transition hover:bg-[#d81c29]"
                      >
                        Return to Dashboard
                      </button>
                    </div>
                  )}
                </>
              )}

              {user.mfaEnabled && (
                <div className="space-y-6">
                  <div>
                    <h2 className="mb-4 text-xl font-semibold text-[#2d2a26]">
                      Disable Two-Factor Authentication
                    </h2>
                    <p className="mb-6 text-[#6d6760]">
                      Disabling MFA will make your account less secure. Enter your password to confirm.
                    </p>
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-[#4f4943]">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full rounded-2xl border border-[#d5ccc3] px-3 py-2 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
                      placeholder="Enter your password"
                    />
                  </div>

                  <button
                    onClick={handleDisableMFA}
                    disabled={isLoading || !password}
                    className="w-full rounded-full bg-[#ef2330] px-4 py-3 font-medium text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isLoading ? 'Disabling...' : 'Disable MFA'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </>
    ) : null
  );
}

export default function MFASetupPage() {
  return (
    <ProtectedRoute>
      <MFASetupContent />
    </ProtectedRoute>
  );
}
