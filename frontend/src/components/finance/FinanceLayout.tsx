'use client';

import { useEffect, ReactNode } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface FinanceLayoutProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  headerActions?: ReactNode;
}

export default function FinanceLayout({ title, subtitle, children, headerActions }: FinanceLayoutProps) {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title={title}
          subtitle={subtitle || ''}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {headerActions && (
            <div className="mb-6 flex justify-end">
              {headerActions}
            </div>
          )}
          {children}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
