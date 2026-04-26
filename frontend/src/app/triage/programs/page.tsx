'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { RefreshCw, ChevronRight, AlertCircle } from 'lucide-react';

interface ProgramStats {
  id: string;
  name: string;
  organization_name: string;
  total_reports: number;
  pending_count: number;
  valid_count: number;
  duplicate_count: number;
  avg_triage_time_hours: number;
  status: string;
}

export default function TriageProgramsPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [sortBy, setSortBy] = useState('pending_count');
  const [searchQuery, setSearchQuery] = useState('');

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: programsData, isLoading, error, refetch } = useApiQuery<{ programs: ProgramStats[]; total: number }>({
    endpoint: `/triage/programs?sort_by=${sortBy}&limit=100`,
  });

  const handleRefresh = async () => {
    await refetch();
    setLastUpdated(new Date());
  };

  const handleRowClick = (programId: string) => {
    router.push(`/triage/programs/${programId}`);
  };

  // Filter programs by search
  const filteredPrograms = programsData?.programs?.filter(program =>
    program.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    program.organization_name?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Programs"
          subtitle="Manage reports by program"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Info Banner */}
          {/* Search and Controls */}
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex-1 max-w-md">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search programs..."
                className="w-full px-4 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
              />
            </div>
            <div className="flex items-center gap-3">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
              >
                <option value="pending_count">Sort by Pending</option>
                <option value="total_reports">Sort by Total Reports</option>
                <option value="avg_triage_time">Sort by Avg Time</option>
              </select>
              <p className="text-xs text-[#94A3B8]">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
              <Button
                onClick={handleRefresh}
                variant="outline"
                size="sm"
                className="gap-2"
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading programs...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-[#EF4444] font-semibold">Failed to load programs</p>
                  <p className="text-sm text-[#94A3B8] mt-1">
                    {error instanceof Error ? error.message : 'Unknown error occurred'}
                  </p>
                  <Button
                    onClick={handleRefresh}
                    variant="outline"
                    size="sm"
                    className="mt-3"
                  >
                    Try Again
                  </Button>
                </div>
              </div>
            </div>
          ) : filteredPrograms.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-lg font-semibold text-[#F8FAFC] mb-2">No programs found</p>
              <p className="text-sm text-[#94A3B8]">
                {searchQuery ? 'Try adjusting your search query' : 'No programs available for triage'}
              </p>
            </div>
          ) : (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-[#0F172A] border-b border-[#334155] text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                <div className="col-span-3">Program Name</div>
                <div className="col-span-2">Organization</div>
                <div className="col-span-1 text-center">Total</div>
                <div className="col-span-1 text-center">Pending</div>
                <div className="col-span-1 text-center">Valid</div>
                <div className="col-span-1 text-center">Duplicates</div>
                <div className="col-span-2 text-center">Avg Triage Time</div>
                <div className="col-span-1 text-center">Status</div>
              </div>

              {/* Table Body */}
              <div className="divide-y divide-[#334155]">
                {filteredPrograms.map((program) => (
                  <div
                    key={program.id}
                    onClick={() => handleRowClick(program.id)}
                    className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-[#0F172A] cursor-pointer transition-colors group"
                  >
                    <div className="col-span-3 flex items-center gap-2">
                      <span className="font-medium text-[#F8FAFC] group-hover:text-[#3B82F6] transition-colors">
                        {program.name}
                      </span>
                      <ChevronRight className="w-4 h-4 text-[#94A3B8] group-hover:text-[#3B82F6] transition-colors" />
                    </div>
                    <div className="col-span-2 text-[#94A3B8] text-sm">
                      {program.organization_name || 'N/A'}
                    </div>
                    <div className="col-span-1 text-center">
                      <span className="inline-flex items-center justify-center px-2 py-1 rounded text-sm font-bold text-[#F8FAFC]">
                        {program.total_reports}
                      </span>
                    </div>
                    <div className="col-span-1 text-center">
                      <span className={`inline-flex items-center justify-center px-2 py-1 rounded text-sm font-bold ${
                        program.pending_count > 10 ? 'bg-[#EF4444] text-white' :
                        program.pending_count > 5 ? 'bg-[#F59E0B] text-white' :
                        'bg-[#3B82F6] text-white'
                      }`}>
                        {program.pending_count}
                      </span>
                    </div>
                    <div className="col-span-1 text-center">
                      <span className="inline-flex items-center justify-center px-2 py-1 rounded text-sm font-bold text-[#10B981]">
                        {program.valid_count}
                      </span>
                    </div>
                    <div className="col-span-1 text-center">
                      <span className="inline-flex items-center justify-center px-2 py-1 rounded text-sm font-bold text-[#F59E0B]">
                        {program.duplicate_count}
                      </span>
                    </div>
                    <div className="col-span-2 text-center text-[#94A3B8] text-sm">
                      {program.avg_triage_time_hours > 0 
                        ? `${program.avg_triage_time_hours.toFixed(1)}h`
                        : 'N/A'
                      }
                    </div>
                    <div className="col-span-1 text-center">
                      <span className={`inline-flex items-center justify-center px-2 py-1 rounded text-xs font-bold uppercase ${
                        program.status === 'active' ? 'bg-[#10B981] text-white' : 'bg-[#94A3B8] text-white'
                      }`}>
                        {program.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary Stats */}
          {filteredPrograms.length > 0 && (
            <div className="mt-6 grid grid-cols-4 gap-4">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Total Programs
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">
                  {filteredPrograms.length}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Total Reports
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">
                  {filteredPrograms.reduce((sum, p) => sum + p.total_reports, 0)}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Pending Triage
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {filteredPrograms.reduce((sum, p) => sum + p.pending_count, 0)}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Total Duplicates
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {filteredPrograms.reduce((sum, p) => sum + p.duplicate_count, 0)}
                </p>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
