'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useAuthStore } from '@/store/authStore';

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

export default function PlatformPaymentMethods() {
  const user = useAuthStore((state) => state.user);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [formData, setFormData] = useState({
    method_type: 'bank_transfer',
    account_name: '',
    account_number: '',
    bank_name: '',
  });
  const [formError, setFormError] = useState('');

  const { data: methodsData, isLoading, refetch } = useApiQuery<PaymentMethod[]>(
    `/payment-methods/${user?.id || ''}`,
    { enabled: !!user?.id }
  );

  const methods = Array.isArray(methodsData) ? methodsData : [];

  const { mutate: addMethod, isLoading: isAdding } = useApiMutation(
    `/payment-methods/${user?.id || ''}`,
    'POST',
    {
      onSuccess: () => {
        setIsAddOpen(false);
        setFormData({ method_type: 'bank_transfer', account_name: '', account_number: '', bank_name: '' });
        setFormError('');
        refetch();
      },
      onError: (error: any) => {
        setFormError(error.message || 'Failed to add payment method');
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

  const handleDelete = (methodId: string) => {
    if (confirm('Delete this payment method?')) {
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/payment-methods/${methodId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
      }).then(() => refetch());
    }
  };

  const methodTypeLabel = (type: string) => {
    if (type === 'bank_transfer') return 'Bank Transfer';
    if (type === 'telebirr') return 'Telebirr';
    if (type === 'cbe_birr') return 'CBE Birr';
    return type;
  };

  return (
    <div className="mb-6">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-[#F8FAFC]">Payout Methods</h2>
          <p className="text-[#64748B] text-sm mt-0.5">Configure where platform commissions are sent on withdrawal</p>
        </div>
        <button
          onClick={() => setIsAddOpen(!isAddOpen)}
          className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-sm font-semibold rounded-xl transition-all shadow-sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Method
        </button>
      </div>

      {/* Add Method Form (inline, dark) */}
      {isAddOpen && (
        <div className="mb-4 bg-[#1E293B] border border-[#334155] rounded-2xl p-6 animate-in fade-in slide-in-from-top-2 duration-200">
          <h3 className="text-[#F8FAFC] font-semibold mb-4">New Payout Method</h3>

          {formError && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {formError}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-[#94A3B8] mb-1.5 uppercase tracking-wider">Method Type</label>
              <select
                value={formData.method_type}
                onChange={(e) => setFormData({ ...formData, method_type: e.target.value })}
                className="w-full px-4 py-2.5 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] text-sm"
              >
                <option value="bank_transfer">Bank Transfer</option>
                <option value="telebirr">Telebirr</option>
                <option value="cbe_birr">CBE Birr</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-[#94A3B8] mb-1.5 uppercase tracking-wider">Account Name</label>
              <input
                type="text"
                placeholder="e.g., Platform Operations"
                value={formData.account_name}
                onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                className="w-full px-4 py-2.5 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder:text-[#475569] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] text-sm"
              />
            </div>

            {formData.method_type === 'bank_transfer' && (
              <div>
                <label className="block text-xs font-medium text-[#94A3B8] mb-1.5 uppercase tracking-wider">Bank Name</label>
                <input
                  type="text"
                  placeholder="e.g., Commercial Bank of Ethiopia"
                  value={formData.bank_name}
                  onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                  className="w-full px-4 py-2.5 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder:text-[#475569] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] text-sm"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-[#94A3B8] mb-1.5 uppercase tracking-wider">Account Number / Phone</label>
              <input
                type="text"
                placeholder="Account number or mobile number"
                value={formData.account_number}
                onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                className="w-full px-4 py-2.5 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder:text-[#475569] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] text-sm"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button
              onClick={() => { setIsAddOpen(false); setFormError(''); }}
              className="px-4 py-2 bg-[#334155] hover:bg-[#475569] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isAdding}
              className="px-5 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isAdding ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Saving...</>
              ) : 'Save Method'}
            </button>
          </div>
        </div>
      )}

      {/* Methods List */}
      {isLoading ? (
        <div className="bg-[#1E293B] border border-[#334155] rounded-2xl p-6 animate-pulse">
          <div className="h-4 bg-[#334155] rounded w-1/3 mb-3" />
          <div className="h-4 bg-[#334155] rounded w-1/2" />
        </div>
      ) : methods.length === 0 ? (
        <div className="bg-[#1E293B] border border-dashed border-[#334155] rounded-2xl p-8 text-center">
          <div className="w-12 h-12 bg-[#0F172A] rounded-full flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <p className="text-[#64748B] text-sm">No payout methods configured yet.</p>
          <button onClick={() => setIsAddOpen(true)} className="text-[#3B82F6] text-sm font-medium hover:text-[#60A5FA] mt-1 transition-colors">
            Add your first method →
          </button>
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {methods.map((method) => (
            <div key={method.id} className="bg-[#1E293B] border border-[#334155] hover:border-[#3B82F6]/50 rounded-2xl p-5 flex items-center justify-between transition-colors">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-[#0F172A] flex items-center justify-center text-[#3B82F6]">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
                <div>
                  <p className="text-[#F8FAFC] font-semibold text-sm">{methodTypeLabel(method.method_type)}</p>
                  <p className="text-[#94A3B8] text-xs mt-0.5">{method.account_name}</p>
                  <p className="text-[#64748B] text-xs">
                    {method.bank_name && `${method.bank_name} · `}****{method.account_number.slice(-4)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDelete(method.id)}
                className="text-[#64748B] hover:text-red-400 p-2 rounded-lg hover:bg-red-500/10 transition-all"
                title="Delete method"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
