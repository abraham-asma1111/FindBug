'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import {
  formatCompactNumber,
  formatCurrency,
  getPortalNavItems,
  getDashboardRouteForRole,
} from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

export default function DashboardPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    if (user) {
      // Redirect to role-specific dashboard
      router.replace(getDashboardRouteForRole(user.role));
    }
  }, [router, user]);

  return (
    <ProtectedRoute>
      {user ? (
        <PortalShell
          user={user}
          title="Dashboard"
          subtitle="Welcome to FindBug Bug Bounty Platform"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Platform Dashboard"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="mb-4 h-12 w-12 mx-auto animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
              <p className="text-sm text-[#6d6760]">Redirecting to your portal...</p>
            </div>
          </div>
        </PortalShell>
      ) : (
        <div className="flex min-h-screen items-center justify-center bg-[#faf6f1]">
          <div className="rounded-3xl border border-[#e6ddd4] bg-white px-6 py-5 text-sm text-[#6d6760] shadow-sm">
            Loading...
          </div>
        </div>
      )}
    </ProtectedRoute>
  );
}
