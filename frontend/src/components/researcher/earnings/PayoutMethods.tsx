'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useAuthStore } from '@/store/authStore';
import Spinner from '@/components/ui/Spinner';
import Modal from '@/components/ui/Modal';
import Badge from '@/components/ui/Badge';

interface PaymentMethod {
  id: string;
  method_type: string;
  account_holder_name: string;
  account_number: string;
  bank_name?: string;
  is_default: boolean;
  is_verified: boolean;
  created_at: string;
}

export default function PayoutMethods() {
  const user = useAuthStore((state) => state.user);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    method_type: 'bank_account',
    account_holder_name: '',
    account_number: '',
    bank_name: '',
  });
  const [formError, setFormError] = useState('');

  const { data: methodsData, isLoading, error, refetch } = useApiQuery<PaymentMethod[]>(
    `/payment-methods/${user?.id || ''}`,
    { 
      enabled: !!user?.id,
      retry: 0, // Don't retry on errors
    }
  );

  const methods = Array.isArray(methodsData) ? methodsData : [];

  // Check for KYC error directly from the error object
  const isKycError = error && error.message?.includes('KYC verification required');

  const { mutate: addMethod, isLoading: isAdding } = useApiMutation(
    `/payment-methods/${user?.id || ''}`,
    'POST',
    {
      onSuccess: () => {
        setIsAddModalOpen(false);
        setFormData({
          method_type: 'bank_account',
          account_holder_name: '',
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

    if (!formData.account_holder_name || !formData.account_number) {
      setFormError('Please fill in all required fields');
      return;
    }

    if (formData.method_type === 'bank_account' && !formData.bank_name) {
      setFormError('Bank name is required for bank accounts');
      return;
    }

    addMethod(formData);
  };

  const handleSetDefault = (methodId: string) => {
    // Update the endpoint dynamically
    const endpoint = `/payment-methods/${methodId}/set-default`;
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      },
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

  const getMethodIcon = (type: string) => {
    switch (type) {
      case 'bank_account':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
        );
      case 'mobile_money':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        );
      case 'crypto':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  // Show KYC required message
  if (isKycError) {
    return (
      <div className="rounded-2xl bg-[#fff2f1] border border-[#f2c0bc] p-8 text-center">
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
          onClick={() => window.location.href = '/researcher/earnings'}
          className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
        >
          Complete KYC Verification
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-5">
        {/* Add New Button */}
        <div className="flex justify-end">
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
          <div className="rounded-2xl bg-[#faf6f1] p-8 text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
              No payment methods
            </p>
            <p className="mt-2 text-sm text-[#6d6760]">
              Add a payment method to receive your earnings
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {methods.map((method) => (
              <div
                key={method.id}
                className="rounded-2xl bg-[#faf6f1] p-5"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-white dark:bg-[#111111] flex items-center justify-center border border-[#e6ddd4] text-[#8b8177]">
                      {getMethodIcon(method.method_type)}
                    </div>

                    {/* Details */}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-semibold text-[#2d2a26] capitalize">
                          {method.method_type.replace('_', ' ')}
                        </p>
                        {method.is_default && (
                          <Badge className="bg-[#10b981] text-white">Default</Badge>
                        )}
                        {method.is_verified ? (
                          <Badge className="bg-[#3b82f6] text-white">Verified</Badge>
                        ) : (
                          <Badge className="bg-[#f59e0b] text-white">Pending</Badge>
                        )}
                      </div>
                      <p className="text-sm text-[#6d6760]">
                        {method.account_holder_name}
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
                  <div className="flex items-center gap-2">
                    {!method.is_default && (
                      <button
                        onClick={() => handleSetDefault(method.id)}
                        className="text-xs font-medium text-[#ef2330] hover:text-[#d41f2c] transition"
                      >
                        Set as Default
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(method.id)}
                      className="text-xs font-medium text-[#6d6760] hover:text-[#b42318] transition"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Payment Method Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          setIsAddModalOpen(false);
          setFormData({
            method_type: 'bank_account',
            account_holder_name: '',
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
                <option value="bank_account">Bank Account</option>
                <option value="mobile_money">Mobile Money</option>
                <option value="crypto">Cryptocurrency</option>
              </select>
            </div>

            {/* Account Holder Name */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Account Holder Name *
              </label>
              <input
                type="text"
                placeholder="Full name as on account"
                value={formData.account_holder_name}
                onChange={(e) => setFormData({ ...formData, account_holder_name: e.target.value })}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
              />
            </div>

            {/* Bank Name (for bank accounts) */}
            {formData.method_type === 'bank_account' && (
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
                  formData.method_type === 'bank_account'
                    ? 'Bank account number'
                    : formData.method_type === 'mobile_money'
                    ? 'Mobile number'
                    : 'Wallet address'
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
                  method_type: 'bank_account',
                  account_holder_name: '',
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
                'Add Method'
              )}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
