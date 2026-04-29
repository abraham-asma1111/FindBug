'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceBillingPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: organizations } = useApiQuery<any>({
    endpoint: '/organizations?limit=100',
  });

  const orgs = organizations?.organizations || [];

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Billing Management"
          subtitle="Organization subscriptions and invoices"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155] mb-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Organization Subscriptions</h2>
            
            {orgs.length === 0 ? (
              <div className="text-center py-8 text-[#94A3B8]">
                <p>No organizations found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {orgs.map((org: any) => (
                  <div key={org.id} className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-[#F8FAFC]">{org.company_name || org.name}</h3>
                        <p className="text-sm text-[#94A3B8]">
                          {org.subscription_type || 'Free'} Plan
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-[#10B981]">
                          ${org.subscription_amount || 0}/month
                        </p>
                        <p className="text-xs text-[#94A3B8]">
                          {org.subscription_status || 'Active'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Recent Invoices</h2>
            <div className="text-center py-8 text-[#94A3B8]">
              <p>No recent invoices</p>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
