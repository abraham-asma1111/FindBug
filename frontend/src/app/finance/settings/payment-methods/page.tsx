'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import { useApiQuery, useApiMutation } from '@/hooks/useApiQuery';

export default function FinancePaymentMethodsSettingsPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: methods, isLoading, refetch } = useApiQuery<any>({
    endpoint: '/payment-methods',
  });

  const toggleMutation = useApiMutation({
    method: 'PUT',
    onSuccess: () => {
      refetch();
    },
  });

  const handleToggle = async (methodId: string, enabled: boolean) => {
    await toggleMutation.mutateAsync({
      endpoint: `/payment-methods/${methodId}`,
      data: { enabled: !enabled },
    });
  };

  const paymentMethods = methods?.payment_methods || [];

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Payment Methods"
          subtitle="Configure available payment methods for payouts"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="bg-[#1E293B] rounded-lg border border-[#334155]">
            {isLoading ? (
              <div className="p-8 text-center text-[#64748B]">Loading...</div>
            ) : paymentMethods.length === 0 ? (
              <div className="p-8 text-center text-[#64748B]">No payment methods found</div>
            ) : (
              <div className="divide-y divide-[#334155]">
                {paymentMethods.map((method: any) => (
                  <div key={method.id} className="p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#0F172A] rounded-lg flex items-center justify-center">
                        {method.method_type === 'bank_transfer' && (
                          <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                          </svg>
                        )}
                        {method.method_type === 'paypal' && (
                          <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                          </svg>
                        )}
                        {method.method_type === 'crypto' && (
                          <svg className="w-6 h-6 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-[#F8FAFC]">
                          {method.method_type === 'bank_transfer' && 'Bank Transfer'}
                          {method.method_type === 'paypal' && 'PayPal'}
                          {method.method_type === 'crypto' && 'Cryptocurrency'}
                        </h3>
                        <p className="text-xs text-[#94A3B8] mt-0.5">
                          {method.method_type === 'bank_transfer' && 'Direct bank account transfers'}
                          {method.method_type === 'paypal' && 'PayPal account payments'}
                          {method.method_type === 'crypto' && 'Bitcoin, Ethereum, USDT'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs font-medium ${method.enabled ? 'text-[#10B981]' : 'text-[#94A3B8]'}`}>
                        {method.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                      <Button
                        variant={method.enabled ? 'danger' : 'success'}
                        size="sm"
                        onClick={() => handleToggle(method.id, method.enabled)}
                        disabled={toggleMutation.isLoading}
                      >
                        {method.enabled ? 'Disable' : 'Enable'}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
