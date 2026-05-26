'use client';

import React from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

const settingsTabs = [
  { href: '/admin/settings/access-control',       label: 'Access Control' },
  { href: '/admin/settings/platform-governance',  label: 'Platform' },
  { href: '/admin/settings/security',             label: 'Security & Compliance' },
  { href: '/admin/settings/monitoring',           label: 'Monitoring & Audit' },
  { href: '/admin/settings/system-configuration', label: 'System Config' },
];

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Admin Settings"
          subtitle="Platform configuration and governance controls"
          navItems={getPortalNavItems(user.role)}
          moduleTabs={settingsTabs}
          hideThemeToggle={true}
        >
          {children}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
