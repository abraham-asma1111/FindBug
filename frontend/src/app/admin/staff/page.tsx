'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function AdminStaffPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const roleFilter = searchParams.get('role') || 'all';

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = roleFilter === 'all' 
    ? '/admin/staff' 
    : `/admin/staff?role=${roleFilter}`;

  const { data, isLoading } = useApiQuery<any>({
    endpoint,
  });

  const staff = data?.staff || [];

  const getRoleBadge = (role: string) => {
    const roleMap: Record<string, { bg: string; label: string }> = {
      triage_specialist: { bg: 'bg-[#F59E0B]', label: 'TRIAGE' },
      finance_officer: { bg: 'bg-[#EF2330]', label: 'FINANCE' },
      admin: { bg: 'bg-[#8B5CF6]', label: 'ADMIN' },
      super_admin: { bg: 'bg-[#EC4899]', label: 'SUPER ADMIN' },
    };
    const config = roleMap[role] || { bg: 'bg-[#94A3B8]', label: role.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Staff"
          subtitle="Manage platform staff"
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
                Staff Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Platform Staff
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Manage triage specialists, finance officers, and administrators.
              </p>
            </div>
          </section>

          {/* Filter Tabs */}
          <div className="mt-6 flex gap-2 flex-wrap">
            <Link href="/admin/staff">
              <Button 
                variant={roleFilter === 'all' ? 'primary' : 'outline'} 
                size="sm"
                className={roleFilter === 'all' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                All
              </Button>
            </Link>
            <Link href="/admin/staff?role=triage_specialist">
              <Button 
                variant={roleFilter === 'triage_specialist' ? 'primary' : 'outline'} 
                size="sm"
                className={roleFilter === 'triage_specialist' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Triage
              </Button>
            </Link>
            <Link href="/admin/staff?role=finance_officer">
              <Button 
                variant={roleFilter === 'finance_officer' ? 'primary' : 'outline'} 
                size="sm"
                className={roleFilter === 'finance_officer' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Finance
              </Button>
            </Link>
            <Link href="/admin/staff?role=admin">
              <Button 
                variant={roleFilter === 'admin' ? 'primary' : 'outline'} 
                size="sm"
                className={roleFilter === 'admin' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Admin
              </Button>
            </Link>
          </div>

          {/* Staff List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading staff...</p>
              </div>
            ) : staff.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No staff found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {staff.map((member: any) => (
                  <Link key={member.id} href={`/admin/staff/${member.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {member.full_name || member.email}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {member.email} • {new Date(member.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {getRoleBadge(member.role)}
                          <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                            member.status === 'active' ? 'bg-[#10B981]' : 'bg-[#94A3B8]'
                          } text-white`}>
                            {member.status.toUpperCase()}
                          </span>
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
