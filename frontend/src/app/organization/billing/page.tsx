'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Card from '@/components/ui/Card';

export default function OrganizationBillingPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user ? (
        <PortalShell
          user={user}
          title="Billing & Invoices"
          subtitle="Manage your subscription, invoices, and payment history"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <Card className="p-12 text-center">
            <div className="text-6xl mb-4">💳</div>
            <h2 className="text-2xl font-bold text-[#2d2a26] dark:text-white mb-2">
              Billing & Invoices
            </h2>
            <p className="text-[#6d6760] dark:text-slate-400 mb-6">
              Manage your subscription, view invoices, and update payment methods
            </p>
            <p className="text-sm text-[#8b8177] dark:text-slate-500">
              Coming soon
            </p>
          </Card>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
