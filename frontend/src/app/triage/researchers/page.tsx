'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { Search, AlertTriangle, User, TrendingUp, FileText, RefreshCw } from 'lucide-react';
import Link from 'next/link';

interface ResearcherData {
  id: string;
  username: string;
  email: string;
  reputation_score: number;
  total_reports: number;
  valid_reports: number;
  duplicate_reports: number;
  invalid_reports: number;
  spam_score: number;
}

export default function TriageResearchersPage() {
  const user = useAuthStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('total_reports');
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedSearchQuery(searchQuery.trim());
    }, 300);

    return () => window.clearTimeout(timeoutId);
  }, [searchQuery]);

  const queryParams = new URLSearchParams({
    sort_by: sortBy,
    limit: '100',
  });

  if (debouncedSearchQuery) {
    queryParams.set('search', debouncedSearchQuery);
  }

  const { data, isLoading, error, refetch } = useApiQuery<{
    researchers: ResearcherData[];
    total: number;
  }>({
    endpoint: `/triage/researchers?${queryParams.toString()}`,
    enabled: true,
  });

  useEffect(() => {
    if (data) {
      setLastUpdated(new Date());
    }
  }, [data]);

  const handleRefresh = async () => {
    await refetch();
  };
  const researchers = data?.researchers || [];

  const getSpamBadgeColor = (score: number) => {
    if (score >= 50) return 'bg-[#EF4444] text-white';
    if (score >= 30) return 'bg-[#F59E0B] text-white';
    return 'bg-[#10B981] text-white';
  };

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Researcher Management"
          subtitle="Monitor researchers and identify spam patterns"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Search and Filters */}
          <div className="mb-6 flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#94A3B8] w-5 h-5" />
              <input
                type="text"
                placeholder="Search by username or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
              />
              {searchQuery && (
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setDebouncedSearchQuery('');
                  }}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#94A3B8] hover:text-[#F8FAFC]"
                >
                  ×
                </button>
              )}
            </div>

            <div className="flex gap-2 items-center">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
              >
                <option value="total_reports">Most Reports</option>
                <option value="duplicates">Most Duplicates</option>
                <option value="spam_score">Highest Spam Score</option>
              </select>
              
              <div className="flex items-center gap-2 ml-2">
                <p className="text-xs text-[#94A3B8] whitespace-nowrap">
                  {lastUpdated.toLocaleTimeString()}
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
          </div>

          {/* Stats Overview */}
          {data && (
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Total Researchers</p>
                <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">{data.total}</p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">High Spam Risk</p>
                <p className="mt-2 text-2xl font-bold text-[#EF4444]">
                  {researchers.filter((r) => r.spam_score >= 50).length}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Medium Risk</p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {researchers.filter((r) => r.spam_score >= 30 && r.spam_score < 50).length}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Good Standing</p>
                <p className="mt-2 text-2xl font-bold text-[#10B981]">
                  {researchers.filter((r) => r.spam_score < 30).length}
                </p>
              </div>
            </div>
          )}

          {/* Researchers List */}
          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading researchers...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertTriangle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load researchers</p>
              </div>
            </div>
          ) : researchers.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <User className="w-12 h-12 text-[#94A3B8] mx-auto mb-3" />
              <p className="text-[#94A3B8]">
                {searchQuery ? 'No researchers match your search' : 'No researchers found'}
              </p>
              {searchQuery && (
                <Button
                  onClick={() => {
                    setSearchQuery('');
                    setDebouncedSearchQuery('');
                  }}
                  variant="outline"
                  className="mt-4"
                >
                  Clear Search
                </Button>
              )}
            </div>
          ) : (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-[#0F172A] border-b border-[#334155]">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Researcher
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Reputation
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Total Reports
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Valid
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Duplicates
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Invalid
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Spam Score
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#334155]">
                    {researchers.map((researcher) => (
                      <tr
                        key={researcher.id}
                        className="hover:bg-[#0F172A] transition-colors"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-[#3B82F6] flex items-center justify-center">
                              <User className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-[#F8FAFC]">
                                {researcher.username}
                              </p>
                              <p className="text-xs text-[#94A3B8]">
                                {researcher.email}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <TrendingUp className="w-4 h-4 text-[#10B981]" />
                            <span className="text-sm font-medium text-[#F8FAFC]">
                              {researcher.reputation_score}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="text-sm font-medium text-[#F8FAFC]">
                            {researcher.total_reports}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="text-sm font-medium text-[#10B981]">
                            {researcher.valid_reports}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="text-sm font-medium text-[#F59E0B]">
                            {researcher.duplicate_reports}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="text-sm font-medium text-[#EF4444]">
                            {researcher.invalid_reports}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${getSpamBadgeColor(researcher.spam_score)}`}>
                            {researcher.spam_score}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <Link href={`/triage/researchers/${researcher.id}`}>
                            <Button variant="outline" size="sm" className="gap-2">
                              <FileText className="w-4 h-4" />
                              View Reports
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Results Count */}
              <div className="px-6 py-3 bg-[#0F172A] border-t border-[#334155]">
                <p className="text-sm text-[#94A3B8]">
                  Showing {researchers.length} of {data?.total || 0} researchers
                  {debouncedSearchQuery && ` matching "${debouncedSearchQuery}"`}
                </p>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
