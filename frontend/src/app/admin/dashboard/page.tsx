'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function AdminDashboardPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: stats } = useApiQuery<any>({
    endpoint: '/admin/statistics',
  });

  const { data: recentUsers } = useApiQuery<any>({
    endpoint: '/admin/users?limit=5',
  });

  const { data: recentPrograms } = useApiQuery<any>({
    endpoint: '/admin/programs?limit=5',
  });

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Admin Dashboard"
          subtitle="Platform administration and management"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero Section */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Admin Dashboard
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Platform Administration
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Manage users, programs, reports, and platform operations.
              </p>
            </div>
          </section>

          {/* Stats Grid */}
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Users
              </p>
              <p className="mt-2 text-3xl font-bold text-[#3B82F6]">
                {stats?.total_users || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Active Programs
              </p>
              <p className="mt-2 text-3xl font-bold text-[#10B981]">
                {stats?.active_programs || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Reports
              </p>
              <p className="mt-2 text-3xl font-bold text-[#F59E0B]">
                {stats?.total_reports || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Platform Revenue
              </p>
              <p className="mt-2 text-3xl font-bold text-[#EF2330]">
                {stats?.platform_revenue?.toLocaleString() || 0} ETB
              </p>
            </div>
          </div>

          {/* Recent Users */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[#F8FAFC]">Recent Users</h2>
              <Link href="/admin/users">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </div>
            <div className="space-y-3">
              {!recentUsers?.users || recentUsers.users.length === 0 ? (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                  <p className="text-[#94A3B8]">No users found</p>
                </div>
              ) : (
                recentUsers.users.map((user: any) => (
                  <Link key={user.id} href={`/admin/users/${user.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {user.full_name || user.email}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {user.role} • {new Date(user.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                            user.status === 'active' ? 'bg-[#10B981]' : 'bg-[#94A3B8]'
                          } text-white`}>
                            {user.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>

          {/* Recent Programs */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[#F8FAFC]">Recent Programs</h2>
              <Link href="/admin/programs">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </div>
            <div className="space-y-3">
              {!recentPrograms?.programs || recentPrograms.programs.length === 0 ? (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                  <p className="text-[#94A3B8]">No programs found</p>
                </div>
              ) : (
                recentPrograms.programs.map((program: any) => (
                  <Link key={program.id} href={`/admin/programs/${program.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {program.name}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {program.organization_name} • {new Date(program.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                            program.status === 'active' ? 'bg-[#10B981]' : 'bg-[#94A3B8]'
                          } text-white`}>
                            {program.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
