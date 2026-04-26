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

export default function AdminProgramsPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') || 'all';

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = statusFilter === 'all' 
    ? '/admin/programs' 
    : `/admin/programs?status=${statusFilter}`;

  const { data, isLoading } = useApiQuery<any>({
    endpoint,
  });

  const programs = data?.programs || [];

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      draft: { bg: 'bg-[#94A3B8]', label: 'DRAFT' },
      active: { bg: 'bg-[#10B981]', label: 'ACTIVE' },
      paused: { bg: 'bg-[#F59E0B]', label: 'PAUSED' },
      closed: { bg: 'bg-[#EF4444]', label: 'CLOSED' },
    };
    const config = statusMap[status] || { bg: 'bg-[#94A3B8]', label: status.toUpperCase() };
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
          title="Programs"
          subtitle="Manage bug bounty programs"
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
                Program Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Bug Bounty Programs
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                View and manage all bug bounty programs on the platform.
              </p>
            </div>
          </section>

          {/* Filter Tabs */}
          <div className="mt-6 flex gap-2 flex-wrap">
            <Link href="/admin/programs">
              <Button 
                variant={statusFilter === 'all' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'all' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                All
              </Button>
            </Link>
            <Link href="/admin/programs?status=active">
              <Button 
                variant={statusFilter === 'active' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'active' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Active
              </Button>
            </Link>
            <Link href="/admin/programs?status=draft">
              <Button 
                variant={statusFilter === 'draft' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'draft' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Draft
              </Button>
            </Link>
            <Link href="/admin/programs?status=closed">
              <Button 
                variant={statusFilter === 'closed' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'closed' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Closed
              </Button>
            </Link>
          </div>

          {/* Programs List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading programs...</p>
              </div>
            ) : programs.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No programs found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {programs.map((program: any) => (
                  <Link key={program.id} href={`/admin/programs/${program.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {program.name}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {program.organization_name} • {program.total_reports || 0} reports • {new Date(program.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {getStatusBadge(program.status)}
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
