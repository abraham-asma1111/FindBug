'use client';

import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { AlertCircle, CheckCircle, ExternalLink, RefreshCw } from 'lucide-react';
import Link from 'next/link';

interface DuplicateGroup {
  original_id: string;
  original_title: string;
  original_report_number: string;
  duplicates: Array<{
    id: string;
    report_number: string;
    title: string;
    submitted_at: string;
    bounty_amount: number | null;
    status: string;
  }>;
}

export default function TriageDuplicatesPage() {
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [selectedProgram, setSelectedProgram] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch programs list
  const { data: programsData } = useApiQuery<{ programs: any[] }>({
    endpoint: '/triage/programs?limit=100',
  });

  // Fetch ALL reports (not just new/triaged) to find duplicates
  // We need to fetch reports with all statuses because duplicates can have status='invalid' or 'duplicate'
  const { data: reportsData, isLoading, error, refetch } = useApiQuery<{ reports: any[] }>({
    endpoint: '/reports?limit=100',
  });

  const handleRefresh = async () => {
    // Invalidate all triage-related queries for synchronization
    queryClient.invalidateQueries({ 
      predicate: (query) => {
        const key = query.queryKey[0];
        return typeof key === 'string' && (
          key.includes('/triage/queue') ||
          key.includes('/triage/statistics') ||
          key.includes('/triage/researchers')
        );
      }
    });
    
    await refetch();
    setLastUpdated(new Date());
  };

  // Auto-refresh when page becomes visible (user navigates back)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        refetch();
        setLastUpdated(new Date());
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [refetch]);

  // Group duplicate reports with filtering
  const groups: DuplicateGroup[] = [];
  if (reportsData?.reports) {
    // Filter reports by program if selected
    let filteredReports = reportsData.reports;
    if (selectedProgram !== 'all') {
      filteredReports = reportsData.reports.filter(r => r.program_id === selectedProgram);
    }
    
    // Get all reports with status='duplicate' (exclude invalid/spam)
    const duplicateReports = filteredReports.filter(
      report => report.status === 'duplicate' && report.is_duplicate
    );
    
    if (duplicateReports.length > 0) {
      // Sort by submission time to find the first one (ORIGINAL)
      const sortedReports = [...duplicateReports].sort((a, b) => 
        new Date(a.submitted_at).getTime() - new Date(b.submitted_at).getTime()
      );
      
      // First report is the ORIGINAL (submitted first)
      const original = sortedReports[0];
      
      // Rest are duplicates (submitted after the original)
      const duplicates = sortedReports.slice(1).map(d => ({
        id: d.id,
        report_number: d.report_number,
        title: d.title,
        submitted_at: d.submitted_at,
        bounty_amount: d.bounty_amount,
        status: d.status,
      }));
      
      groups.push({
        original_id: original.id,
        original_title: original.title,
        original_report_number: original.report_number,
        duplicates: duplicates,
      });
    }
  }

  // Apply search filter
  const filteredGroups = searchQuery
    ? groups.filter(g => 
        g.original_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        g.original_report_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        g.duplicates.some(d => 
          d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.report_number.toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    : groups;

  const totalDuplicates = filteredGroups.reduce((sum, g) => sum + g.duplicates.length, 0);

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Duplicate Checker"
          subtitle="View all reports marked as duplicates across the platform"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Filters */}
          <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Program Filter */}
            <div>
              <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                Filter by Program
              </label>
              <select
                value={selectedProgram}
                onChange={(e) => setSelectedProgram(e.target.value)}
                className="w-full px-4 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#06B6D4] focus:border-transparent"
              >
                <option value="all">All Programs</option>
                {programsData?.programs?.map((program) => (
                  <option key={program.id} value={program.id}>
                    {program.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                Search Reports
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title or report number..."
                className="w-full px-4 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#A855F7] focus:border-transparent"
              />
            </div>

            {/* Clear Filters */}
            <div className="flex items-end">
              <Button
                onClick={() => {
                  setSelectedProgram('all');
                  setSearchQuery('');
                }}
                variant="outline"
                size="sm"
                className="w-full"
                disabled={selectedProgram === 'all' && !searchQuery}
              >
                Clear Filters
              </Button>
            </div>
          </div>

          {/* Stats and Refresh */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex gap-4">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Duplicate Groups
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">
                  {filteredGroups.length}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Total Duplicates
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {totalDuplicates}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
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
              <p className="mt-4 text-[#94A3B8]">Analyzing reports...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-[#EF4444] font-semibold">Failed to load duplicates</p>
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
          ) : filteredGroups.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <CheckCircle className="mx-auto h-12 w-12 text-[#06B6D4] mb-4" />
              <p className="text-lg font-semibold text-[#F8FAFC] mb-2">
                {searchQuery || selectedProgram !== 'all' ? 'No matching duplicates found' : 'No duplicates found'}
              </p>
              <p className="text-sm text-[#94A3B8] max-w-md mx-auto">
                {searchQuery || selectedProgram !== 'all' 
                  ? 'Try adjusting your filters or search query to see more results.'
                  : 'There are currently no reports marked as duplicates in the system. When triage specialists mark reports as duplicates, they will appear here grouped by their original report.'
                }
              </p>
              {(searchQuery || selectedProgram !== 'all') && (
                <Button
                  onClick={() => {
                    setSelectedProgram('all');
                    setSearchQuery('');
                  }}
                  variant="outline"
                  size="sm"
                  className="mt-4"
                >
                  Clear Filters
                </Button>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {filteredGroups.map((group) => (
                <div key={group.original_id} className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  {/* Original Report - Clearly Distinguished */}
                  <div className="mb-4 pb-4 border-b-2 border-[#06B6D4]">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="px-3 py-1.5 rounded-md text-sm font-bold bg-gradient-to-r from-[#06B6D4] to-[#0891B2] text-white uppercase tracking-wide shadow-lg">
                        ⭐ ORIGINAL REPORT
                      </span>
                      <span className="text-sm font-mono text-[#06B6D4] font-semibold">{group.original_report_number}</span>
                    </div>
                    <h3 className="text-xl font-bold text-[#F8FAFC] mb-3">
                      {group.original_title}
                    </h3>
                    <div className="flex items-center gap-4 mb-4">
                      <span className="text-sm text-[#10B981] font-semibold">
                        ✓ Submitted first - Eligible for 100% bounty
                      </span>
                    </div>
                    <Link href={`/triage/reports/${group.original_id}`}>
                      <Button variant="outline" size="sm" className="gap-2 border-[#06B6D4] text-[#06B6D4] hover:bg-[#06B6D4] hover:text-white">
                        <ExternalLink className="w-4 h-4" />
                        View Original Report
                      </Button>
                    </Link>
                  </div>

                  {/* Duplicate Reports */}
                  <div>
                    <p className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-3">
                      Duplicates ({group.duplicates.length})
                    </p>
                    <div className="space-y-3">
                      {group.duplicates.map((dup) => (
                        <div key={dup.id} className="flex items-center justify-between p-4 bg-[#0F172A] rounded-lg border border-[#334155] hover:border-[#A855F7] transition-colors">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-mono text-[#A855F7]">{dup.report_number}</span>
                              <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                dup.status === 'duplicate' ? 'bg-[#F59E0B] text-white' : 'bg-[#94A3B8] text-white'
                              }`}>
                                {dup.status}
                              </span>
                            </div>
                            <p className="font-medium text-[#F8FAFC] mb-2">{dup.title}</p>
                            <div className="flex gap-4 text-sm text-[#94A3B8]">
                              <span>Submitted {new Date(dup.submitted_at).toLocaleDateString()}</span>
                              {dup.bounty_amount && (
                                <span className="text-[#10B981]">${dup.bounty_amount.toLocaleString()}</span>
                              )}
                            </div>
                          </div>
                          <Link href={`/triage/reports/${dup.id}`}>
                            <Button variant="outline" size="sm" className="gap-2 border-[#A855F7] text-[#A855F7] hover:bg-[#A855F7] hover:text-white">
                              <ExternalLink className="w-4 h-4" />
                              View
                            </Button>
                          </Link>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
