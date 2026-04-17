'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

export default function TriageAnalyticsPage() {
  const user = useAuthStore((state) => state.user);

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Triage Analytics"
          subtitle="Queue performance and validation metrics"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
            <p className="text-[#94A3B8]">
              Analytics content coming soon
            </p>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
