'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { Folder, Search, AlertCircle, Clock } from 'lucide-react';

interface Program {
  id: string;
  name: string;
  status: string;
  total_reports: number;
  pending_reports: number;
  valid_reports: number;
  created_at: string;
}

interface ProgramsResponse {
  programs: Program[];
  total: number;
  limit: number;
  offset: number;
}

const statusColors: Record<string, string> = {
  active: 'bg-[#3B82F6] text-white',
  paused: 'bg-[#F59E0B] text-white',
  closed: 'bg-[#94A3B8] text-white',
};

export default function TriageProgramsPage() {
  const user = useAuthStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('pending_count');
  const [page, setPage] = useState(0);
  const limit = 20;

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const queryParams = new URLSearchParams();
  if (searchQuery) queryParams.append('search', searchQuery);
  queryParams.append('sort_by', sortBy);
  queryParams.append('limit', limit.toString());
  queryParams.append('offset', (page * limit).toString());

  const { data, isLoading, error } = useApiQuery<ProgramsResponse>({
    endpoint: `/triage/programs?${queryParams.toString()}`,
  });

  const programs = data?.programs || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Programs"
          subtitle="View program triage metrics"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Search and Sort */}
          <div className="mb-6 flex flex-col gap-4 sm:flex-row">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]" />
              <input
                type="text"
                placeholder="Search programs..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(0);
                }}
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-[#334155] bg-[#1E293B] text-[#F8FAFC] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
              />
            </div>
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                setPage(0);
              }}
              className="px-4 py-2 rounded-lg border border-[#334155] bg-[#1E293B] text-[#F8FAFC] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
            >
              <option value="pending_count">Most Pending</option>
              <option value="total_reports">Most Reports</option>
            </select>
          </div>

          {/* Stats */}
          <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Programs
              </p>
              <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">
                {total}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Reports
              </p>
              <p className="mt-2 text-2xl font-bold text-[#3B82F6]">
                {programs.reduce((sum, p) => sum + p.total_reports, 0)}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Pending Triage
              </p>
              <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                {programs.reduce((sum, p) => sum + p.pending_reports, 0)}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Valid Reports
              </p>
              <p className="mt-2 text-2xl font-bold text-[#3B82F6]">
                {programs.reduce((sum, p) => sum + p.valid_reports, 0)}
              </p>
            </div>
          </div>

          {/* Programs Table */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
            {isLoading ? (
              <div className="p-8 text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
                <p className="mt-4 text-[#94A3B8]">Loading programs...</p>
              </div>
            ) : error ? (
              <div className="p-8 text-center">
                <AlertCircle className="mx-auto h-8 w-8 text-[#EF4444]" />
                <p className="mt-4 text-[#EF4444]">Failed to load programs</p>
              </div>
            ) : programs.length === 0 ? (
              <div className="p-8 text-center">
                <Folder className="mx-auto h-12 w-12 text-[#94A3B8]" />
                <p className="mt-4 text-[#94A3B8]">No programs found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-[#334155] bg-[#0F172A]">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                        Program
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                        Total Reports
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                        Pending
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                        Valid
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                        Created
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#334155]">
                    {programs.map((program) => (
                      <tr
                        key={program.id}
                        className="hover:bg-[#334155] transition-colors"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-[#0F172A]">
                              <Folder className="w-5 h-5 text-[#94A3B8]" />
                            </div>
                            <div>
                              <p className="font-semibold text-[#F8FAFC]">
                                {program.name}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                              statusColors[program.status] || statusColors.active
                            }`}
                          >
                            {program.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="font-semibold text-[#3B82F6]">
                            {program.total_reports}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            {program.pending_reports > 0 && (
                              <Clock className="w-4 h-4 text-[#F59E0B]" />
                            )}
                            <span className="font-semibold text-[#F59E0B]">
                              {program.pending_reports}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="font-semibold text-[#3B82F6]">
                            {program.valid_reports}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-[#94A3B8]">
                          {program.created_at
                            ? new Date(program.created_at).toLocaleDateString()
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-[#94A3B8]">
                Page {page + 1} of {totalPages} ({total} total programs)
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  variant="outline"
                >
                  Previous
                </Button>
                <Button
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page === totalPages - 1}
                  variant="outline"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
