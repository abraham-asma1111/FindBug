'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import PTaaSEngagementList from '@/components/organization/services/ptaas/PTaaSEngagementList';

export default function OrganizationPTaaSPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="PTaaS"
          subtitle="Penetration Testing as a Service"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <PTaaSEngagementList />
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
