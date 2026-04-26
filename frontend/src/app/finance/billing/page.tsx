'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function FinanceBillingPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data, isLoading } = useApiQuery<any>({
    endpoint: '/subscription/organizations',
  });

  const subscriptions = data?.subscriptions || [];

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      active: { bg: 'bg-[#10B981]', label: 'ACTIVE' },
      trial: { bg: 'bg-[#3B82F6]', label: 'TRIAL' },
      expired: { bg: 'bg-[#EF4444]', label: 'EXPIRED' },
      cancelled: { bg: 'bg-[#94A3B8]', label: 'CANCELLED' },
    };
    const config = statusMap[status] || { bg: 'bg-[#94A3B8]', label: status.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Billing"
          subtitle="Manage organization subscriptions"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Finance Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero Section */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Billing Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Organization Subscriptions
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Monitor and manage organization subscription plans and billing.
              </p>
            </div>
          </section>

          {/* Subscriptions List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading subscriptions...</p>
              </div>
            ) : subscriptions.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No subscriptions found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {subscriptions.map((subscription: any) => (
                  <Link key={subscription.id} href={`/finance/billing/${subscription.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {subscription.organization_name || 'Organization'}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {subscription.plan_name || 'Plan'} • {subscription.amount?.toLocaleString()} ETB/month • Expires {new Date(subscription.expires_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {getStatusBadge(subscription.status)}
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
