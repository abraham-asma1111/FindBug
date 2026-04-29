'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';

export default function FinanceFeesSettingsPage() {
  const user = useAuthStore((state) => state.user);
  const [commissionRate, setCommissionRate] = useState('15');
  const [processingFee, setProcessingFee] = useState('2.5');
  const [minimumPayout, setMinimumPayout] = useState('50');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const updateMutation = useApiMutation({
    method: 'PUT',
    onSuccess: () => {
      alert('Fee settings updated successfully');
    },
  });

  const handleSave = async () => {
    await updateMutation.mutateAsync({
      endpoint: '/finance/settings/fees',
      data: {
        commission_rate: parseFloat(commissionRate),
        processing_fee: parseFloat(processingFee),
        minimum_payout: parseFloat(minimumPayout),
      },
    });
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Fee Settings"
          subtitle="Configure platform fees and commission rates"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Commission Rate (%)
                </label>
                <input
                  type="number"
                  value={commissionRate}
                  onChange={(e) => setCommissionRate(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                  step="0.1"
                  min="0"
                  max="100"
                />
                <p className="text-xs text-[#94A3B8] mt-1">
                  Platform commission on bounty payments
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Processing Fee (%)
                </label>
                <input
                  type="number"
                  value={processingFee}
                  onChange={(e) => setProcessingFee(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                  step="0.1"
                  min="0"
                  max="10"
                />
                <p className="text-xs text-[#94A3B8] mt-1">
                  Payment processing fee
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Minimum Payout Amount ($)
                </label>
                <input
                  type="number"
                  value={minimumPayout}
                  onChange={(e) => setMinimumPayout(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                  step="10"
                  min="0"
                />
                <p className="text-xs text-[#94A3B8] mt-1">
                  Minimum amount for payout requests
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <Button onClick={handleSave} disabled={updateMutation.isLoading}>
                  {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button variant="outline" onClick={() => {
                  setCommissionRate('15');
                  setProcessingFee('2.5');
                  setMinimumPayout('50');
                }}>
                  Reset to Defaults
                </Button>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
