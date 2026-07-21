'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import CodeReviewEngagementList from '@/components/organization/services/code-review/CodeReviewEngagementList';

export default function OrganizationCodeReviewPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Code Review"
          subtitle="Expert Security Code Reviews"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <CodeReviewEngagementList />
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
