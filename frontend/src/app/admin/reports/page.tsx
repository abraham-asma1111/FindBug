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

export default function AdminReportsPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') || 'all';

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = statusFilter === 'all' 
    ? '/admin/reports' 
    : `/admin/reports?status=${statusFilter}`;

  const { data, isLoading } = useApiQuery<any>({
    endpoint,
  });

  const reports = data?.reports || [];

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      submitted: { bg: 'bg-[#3B82F6]', label: 'SUBMITTED' },
      triaged: { bg: 'bg-[#F59E0B]', label: 'TRIAGED' },
      validated: { bg: 'bg-[#10B981]', label: 'VALIDATED' },
      rejected: { bg: 'bg-[#EF4444]', label: 'REJECTED' },
      duplicate: { bg: 'bg-[#94A3B8]', label: 'DUPLICATE' },
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
          title="Reports"
          subtitle="Manage vulnerability reports"
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
                Report Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Vulnerability Reports
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                View and manage all vulnerability reports submitted to the platform.
              </p>
            </div>
          </section>

          {/* Filter Tabs */}
          <div className="mt-6 flex gap-2 flex-wrap">
            <Link href="/admin/reports">
              <Button 
                variant={statusFilter === 'all' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'all' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                All
              </Button>
            </Link>
            <Link href="/admin/reports?status=submitted">
              <Button 
                variant={statusFilter === 'submitted' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'submitted' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Submitted
              </Button>
            </Link>
            <Link href="/admin/reports?status=triaged">
              <Button 
                variant={statusFilter === 'triaged' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'triaged' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Triaged
              </Button>
            </Link>
            <Link href="/admin/reports?status=validated">
              <Button 
                variant={statusFilter === 'validated' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'validated' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Validated
              </Button>
            </Link>
          </div>

          {/* Reports List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading reports...</p>
              </div>
            ) : reports.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No reports found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {reports.map((report: any) => (
                  <Link key={report.id} href={`/admin/reports/${report.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {report.title}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {report.researcher_name} • {report.program_name} • {new Date(report.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {getStatusBadge(report.status)}
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
