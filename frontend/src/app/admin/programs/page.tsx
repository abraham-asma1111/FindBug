'use client';

import { useEffect, useState } from 'react';
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
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = statusFilter === 'all' 
    ? '/admin/programs' 
    : `/admin/programs?status_filter=${statusFilter}`;

  const { data, isLoading, isError, error } = useApiQuery<any>({
    endpoint,
  });

  const programs = data?.programs || [];
  
  // Debug: Log API errors
  useEffect(() => {
    if (isError && error) {
      console.error('[Admin Programs] API Error:', error.message);
    }
  }, [isError, error]);
  
  const filteredPrograms = programs.filter((p: any) => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (p.organization_name && p.organization_name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      draft: { bg: 'bg-[#94A3B8]', label: 'DRAFT' },
      active: { bg: 'bg-[#10B981]', label: 'ACTIVE' },
      public: { bg: 'bg-[#10B981]', label: 'ACTIVE' },
      private: { bg: 'bg-[#10B981]', label: 'PRIVATE' },
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
    <ProtectedRoute allowedRoles={['admin']}>
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

          {/* Controls Row */}
          <div className="mt-4 mb-3 flex flex-col md:flex-row items-center justify-between gap-6">
            
            {/* Filter Tabs */}
            <div className="flex justify-start gap-8 sm:gap-12 flex-wrap">
            <Link href="/admin/programs">
              <Button 
                variant={statusFilter === 'all' ? 'primary' : 'outline'} 
                size="sm"
                className={`w-32 sm:w-40 transition-colors ${statusFilter === 'all' ? 'bg-[#EF2330] hover:bg-[#DC2026] border-transparent font-semibold' : 'bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] border-[#334155]'}`}
              >
                All
              </Button>
            </Link>
            <Link href="/admin/programs?status=public">
              <Button 
                variant={statusFilter === 'public' ? 'primary' : 'outline'} 
                size="sm"
                className={`w-32 sm:w-40 transition-colors ${statusFilter === 'public' ? 'bg-[#EF2330] hover:bg-[#DC2026] border-transparent font-semibold' : 'bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] border-[#334155]'}`}
              >
                Active
              </Button>
            </Link>
            <Link href="/admin/programs?status=draft">
              <Button 
                variant={statusFilter === 'draft' ? 'primary' : 'outline'} 
                size="sm"
                className={`w-32 sm:w-40 transition-colors ${statusFilter === 'draft' ? 'bg-[#EF2330] hover:bg-[#DC2026] border-transparent font-semibold' : 'bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] border-[#334155]'}`}
              >
                Draft
              </Button>
            </Link>
            <Link href="/admin/programs?status=closed">
              <Button 
                variant={statusFilter === 'closed' ? 'primary' : 'outline'} 
                size="sm"
                className={`w-32 sm:w-40 transition-colors ${statusFilter === 'closed' ? 'bg-[#EF2330] hover:bg-[#DC2026] border-transparent font-semibold' : 'bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] border-[#334155]'}`}
              >
                Closed
              </Button>
            </Link>
          </div>
          
            {/* Search Bar */}
            <div className="w-full xl:w-72 flex justify-end">
              <div className="relative w-full max-w-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-[#64748B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Search programs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-[#334155] rounded-lg leading-5 bg-[#0F172A] text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-1 focus:ring-purple-500 focus:border-purple-500 sm:text-sm transition-colors"
                />
              </div>
            </div>
          </div>

          {/* Programs List */}
          <div className="mt-3">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading programs...</p>
              </div>
            ) : isError ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4">
                  <h3 className="text-red-400 font-semibold mb-2">Error Loading Programs</h3>
                  <p className="text-red-300 text-sm">{error?.message || 'Failed to load programs'}</p>
                </div>
              </div>
            ) : filteredPrograms.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No programs found</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredPrograms.map((program: any) => (
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
