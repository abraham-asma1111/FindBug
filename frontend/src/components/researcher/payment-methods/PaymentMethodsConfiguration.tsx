'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useAuthStore } from '@/store/authStore';
import Spinner from '@/components/ui/Spinner';
import Modal from '@/components/ui/Modal';
import SectionCard from '@/components/dashboard/SectionCard';

interface PaymentMethod {
  id: string;
  method_type: string;
  account_name: string;
  account_number: string;
  bank_name?: string;
  is_default: boolean;
  is_verified: boolean;
  created_at: string;
}

export default function PaymentMethodsConfiguration() {
  const user = useAuthStore((state) => state.user);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    method_type: 'bank_transfer',
    account_name: '',
    account_number: '',
    bank_name: '',
  });
  const [formError, setFormError] = useState('');

  const { data: methodsData, isLoading, error, refetch } = useApiQuery<PaymentMethod[]>(
    `/payment-methods/${user?.id || ''}`,
    { 
      enabled: !!user?.id,
      retry: 0,
    }
  );

  const methods = Array.isArray(methodsData) ? methodsData : [];
  const isKycError = error && error.message?.includes('KYC verification required');

  const { mutate: addMethod, isLoading: isAdding } = useApiMutation(
    `/payment-methods/${user?.id || ''}`,
    'POST',
    {
      onSuccess: () => {
        setIsAddModalOpen(false);
        setFormData({
          method_type: 'bank_transfer',
          account_name: '',
          account_number: '',
          bank_name: '',
        });
        setFormError('');
        refetch();
      },
      onError: (error: any) => {
        if (error.message?.includes('KYC verification required')) {
          setFormError('KYC verification is required to add payment methods. Please complete your KYC verification first.');
        } else {
          setFormError(error.message || 'Failed to add payment method');
        }
      },
    }
  );

  const handleSubmit = () => {
    setFormError('');

    if (!formData.account_name || !formData.account_number) {
      setFormError('Please fill in all required fields');
      return;
    }

    if (formData.method_type === 'bank_transfer' && !formData.bank_name) {
      setFormError('Bank name is required for bank transfers');
      return;
    }

    addMethod(formData);
  };

  const handleSetDefault = (methodId: string) => {
    const endpoint = `/payment-methods/${methodId}/set-default`;
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: user?.id }),
    }).then(() => refetch());
  };

  const handleDelete = (methodId: string) => {
    if (confirm('Are you sure you want to delete this payment method?')) {
      const endpoint = `/payment-methods/${methodId}`;
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1${endpoint}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      }).then(() => refetch());
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isKycError) {
    return (
      <SectionCard
        title="KYC Verification Required"
        description="Complete your KYC verification to configure payment methods"
        headerAlign="center"
      >
        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#fef2f2] flex items-center justify-center">
            <svg className="w-8 h-8 text-[#ef2330]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#b42318] mb-2">
            KYC Verification Required
          </p>
          <p className="text-sm text-[#6d6760] mb-4">
            You need to complete KYC verification before you can add payment methods or withdraw earnings.
          </p>
          <button
            onClick={() => window.location.href = '/researcher/earnings?tab=kyc'}
            className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
          >
            Complete KYC Verification
          </button>
        </div>
      </SectionCard>
    );
  }

  return (
    <>
      <div className="space-y-6">
        {/* Header Actions */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold text-[#2d2a26]">Your Payment Methods</h2>
            <p className="text-sm text-[#6d6760] mt-1">
              Manage your bank accounts and payment methods for receiving earnings
            </p>
          </div>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Payment Method
          </button>
        </div>

        {/* Payment Methods List */}
        {methods.length === 0 ? (
          <SectionCard
            title="Configure Payment Method"
            description="Add your first payment method to start receiving earnings"
            headerAlign="center"
          >
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#faf6f1] flex items-center justify-center border border-[#e6ddd4]">
                <svg className="w-8 h-8 text-[#8b8177]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177] mb-2">
                No Payment Methods
              </p>
              <p className="text-sm text-[#6d6760] mb-4">
                Add a payment method to receive your earnings from bug bounties and rewards
              </p>
              <button
                onClick={() => setIsAddModalOpen(true)}
                className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Your First Payment Method
              </button>
            </div>
          </SectionCard>
        ) : (
          <div className="grid gap-4">
            {methods.map((method) => (
              <SectionCard key={method.id}>
                <div className="flex items-start justify-between p-6">
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#faf6f1] flex items-center justify-center border border-[#e6ddd4] text-[#8b8177]">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                      </svg>
                    </div>

                    {/* Details */}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-semibold text-[#2d2a26] capitalize">
                          {method.method_type.replace('_', ' ')}
                        </p>
                        {method.is_default && (
                          <span className="inline-flex items-center rounded-full bg-[#10b981] px-2 py-0.5 text-xs font-medium text-white">
                            Default
                          </span>
                        )}
                        {method.is_verified ? (
                          <span className="inline-flex items-center rounded-full bg-[#3b82f6] px-2 py-0.5 text-xs font-medium text-white">
                            Verified
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-[#f59e0b] px-2 py-0.5 text-xs font-medium text-white">
                            Pending Verification
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-[#6d6760] font-medium">
                        {method.account_name}
                      </p>
                      <p className="text-xs text-[#8b8177] mt-1">
                        {method.bank_name && `${method.bank_name} • `}
                        ****{method.account_number.slice(-4)}
                      </p>
                      <p className="text-xs text-[#8b8177] mt-1">
                        Added {new Date(method.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3">
                    {!method.is_default && (
                      <button
                        onClick={() => handleSetDefault(method.id)}
                        className="text-xs font-medium text-[#ef2330] hover:text-[#d41f2c] transition px-3 py-1 rounded-full border border-[#ef2330] hover:bg-[#fef2f2]"
                      >
                        Set as Default
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(method.id)}
                      className="text-xs font-medium text-[#6d6760] hover:text-[#b42318] transition px-3 py-1 rounded-full border border-[#d8d0c8] hover:bg-[#fff2f1] hover:border-[#f2c0bc]"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </SectionCard>
            ))}
          </div>
        )}

        {/* Information Card */}
        <SectionCard
          title="Important Information"
          description="Please read before adding payment methods"
        >
          <div className="p-6 space-y-4">
            <div className="rounded-2xl bg-[#eef5fb] border border-[#b8d4f1] p-4">
              <h4 className="text-sm font-semibold text-[#2d78a8] mb-2">📋 Supported Payment Methods</h4>
              <ul className="text-xs text-[#2d78a8] space-y-1">
                <li>• <strong>Bank Transfer:</strong> Ethiopian commercial banks (CBE, Dashen, Awash, etc.)</li>
                <li>• <strong>Telebirr:</strong> Mobile money service by Ethio Telecom</li>
                <li>• <strong>CBE Birr:</strong> Mobile banking service by Commercial Bank of Ethiopia</li>
              </ul>
            </div>

            <div className="rounded-2xl bg-[#fff7ed] border border-[#fed7aa] p-4">
              <h4 className="text-sm font-semibold text-[#ea580c] mb-2">⚠️ Verification Process</h4>
              <ul className="text-xs text-[#ea580c] space-y-1">
                <li>• Payment methods are verified within 24-48 hours</li>
                <li>• You must have completed KYC verification</li>
                <li>• Account name must match your KYC verified name</li>
                <li>• Only verified payment methods can receive payouts</li>
              </ul>
            </div>

            <div className="rounded-2xl bg-[#f0fdf4] border border-[#bbf7d0] p-4">
              <h4 className="text-sm font-semibold text-[#16a34a] mb-2">💰 Payout Information</h4>
              <ul className="text-xs text-[#16a34a] space-y-1">
                <li>• Minimum payout amount: 100 ETB</li>
                <li>• Payouts are processed within 3-5 business days</li>
                <li>• Set a default payment method for automatic payouts</li>
                <li>• Platform commission: 30% (deducted before payout)</li>
              </ul>
            </div>
          </div>
        </SectionCard>
      </div>

      {/* Add Payment Method Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          setIsAddModalOpen(false);
          setFormData({
            method_type: 'bank_transfer',
            account_name: '',
            account_number: '',
            bank_name: '',
          });
          setFormError('');
        }}
        size="md"
      >
        <div className="space-y-5">
          <div>
            <h2 className="text-xl font-bold text-[#2d2a26]">Add Payment Method</h2>
            <p className="text-sm text-[#6d6760] mt-1">
              Add a new payment method to receive your earnings
            </p>
          </div>

          {formError && (
            <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              <p className="font-semibold">Error</p>
              <p className="mt-1">{formError}</p>
            </div>
          )}

          <div className="rounded-2xl bg-[#faf6f1] p-5 space-y-4">
            {/* Method Type */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Payment Method Type *
              </label>
              <select
                value={formData.method_type}
                onChange={(e) => setFormData({ ...formData, method_type: e.target.value })}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
              >
                <option value="bank_transfer">Bank Transfer</option>
                <option value="telebirr">Telebirr</option>
                <option value="cbe_birr">CBE Birr</option>
              </select>
            </div>

            {/* Account Holder Name */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Account Holder Name *
              </label>
              <input
                type="text"
                placeholder="Full name as on account (must match KYC name)"
                value={formData.account_name}
                onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
              />
            </div>

            {/* Bank Name (for bank transfers) */}
            {formData.method_type === 'bank_transfer' && (
              <div>
                <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                  Bank Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g., Commercial Bank of Ethiopia"
                  value={formData.bank_name}
                  onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                  className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
                />
              </div>
            )}

            {/* Account Number */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Account Number *
              </label>
              <input
                type="text"
                placeholder={
                  formData.method_type === 'bank_transfer'
                    ? 'Bank account number'
                    : formData.method_type === 'telebirr'
                    ? 'Telebirr phone number (e.g., 0911234567)'
                    : 'CBE Birr phone number (e.g., 0911234567)'
                }
                value={formData.account_number}
                onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-[#e6ddd4]">
            <button
              onClick={() => {
                setIsAddModalOpen(false);
                setFormData({
                  method_type: 'bank_transfer',
                  account_name: '',
                  account_number: '',
                  bank_name: '',
                });
                setFormError('');
              }}
              className="inline-flex rounded-full border border-[#d8d0c8] px-6 py-2.5 text-sm font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isAdding}
              className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAdding ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Adding...
                </>
              ) : (
                'Add Payment Method'
              )}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}