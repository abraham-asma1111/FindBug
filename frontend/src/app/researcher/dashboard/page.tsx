'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatCompactNumber, formatCurrency, formatDateTime, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface ResearcherSubmission {
  id?: string;
  report_number?: string;
  title: string;
  status?: string;
  assigned_severity?: string | null;
  submitted_at?: string | null;
  bounty_amount?: number | null;
}

interface ResearcherDashboardData {
  overview: {
    total_submissions: number;
    submissions_by_status: Record<string, number>;
    active_programs: number;
  };
  earnings: {
    total_earnings: number;
    pending_earnings: number;
    paid_earnings: number;
  };
  reputation: {
    score: number;
    rank: number;
    total_researchers: number;
    percentile: number;
  };
  recent_submissions: ResearcherSubmission[];
  monthly_trend: Array<{
    month: string;
    submissions: number;
    earnings: number;
  }>;
}

const statusTone: Record<string, string> = {
  new: 'bg-[#eef5fb] text-[#2d78a8]',
  triaged: 'bg-[#faf1e1] text-[#9a6412]',
  valid: 'bg-[#eef7ef] text-[#24613a]',
  invalid: 'bg-[#fff2f1] text-[#b42318]',
  resolved: 'bg-[#f3ede6] text-[#5f5851]',
};

export default function ResearcherDashboardPage() {
  const user = useAuthStore((state) => state.user);
  const [data, setData] = useState<ResearcherDashboardData | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/dashboard/researcher');
        if (!cancelled) {
          setData(response.data);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load researcher dashboard.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  if (!user) {
    return null;
  }

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      <PortalShell
        user={user}
        title="Researcher Overview"
        subtitle="Track submission throughput, earnings, and reputation from the first cross-role bug bounty slice."
        navItems={getPortalNavItems(user.role)}
      >
        {error ? (
          <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
            {error}
          </div>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Total Submissions"
            value={isLoading ? '...' : formatCompactNumber(data?.overview.total_submissions)}
            helper="Lifetime reports submitted"
          />
          <StatCard
            label="Active Programs"
            value={isLoading ? '...' : formatCompactNumber(data?.overview.active_programs)}
            helper="Programs you are currently active in"
          />
          <StatCard
            label="Total Earnings"
            value={isLoading ? '...' : formatCurrency(data?.earnings.total_earnings)}
            helper={`Pending ${formatCurrency(data?.earnings.pending_earnings)}`}
          />
          <StatCard
            label="Reputation"
            value={isLoading ? '...' : formatCompactNumber(data?.reputation.score)}
            helper={
              data
                ? `Rank ${data.reputation.rank || '-'} of ${data.reputation.total_researchers || 0}`
                : 'Leaderboard position'
            }
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
          <SectionCard
            title="Submission Pipeline"
            description="Current report status distribution from the backend dashboard service."
          >
            <div className="grid gap-3 sm:grid-cols-2">
              {Object.entries(data?.overview.submissions_by_status ?? {}).map(([status, count]) => (
                <div key={status} className="rounded-2xl bg-[#faf6f1] px-4 py-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">{status}</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{count}</p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard
            title="Reputation Snapshot"
            description="How you currently rank against the researcher pool."
          >
            <div className="space-y-4 text-sm text-[#6d6760]">
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Percentile</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                  {data ? `${data.reputation.percentile}%` : '...'}
                </p>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Paid Earnings</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                  {isLoading ? '...' : formatCurrency(data?.earnings.paid_earnings)}
                </p>
              </div>
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(0,0.7fr)]">
          <SectionCard
            title="Recent Submissions"
            description="The most recent reports returned by the backend dashboard endpoint."
          >
            <div className="space-y-3">
              {data?.recent_submissions?.length ? (
                data.recent_submissions.map((submission) => (
                  <div
                    key={submission.id || submission.report_number || submission.title}
                    className="rounded-2xl border border-[#e6ddd4] bg-[#fcfaf7] p-4"
                  >
                    <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-[#2d2a26]">
                          {submission.report_number ? `${submission.report_number} · ` : ''}
                          {submission.title}
                        </p>
                        <p className="mt-2 text-sm text-[#6d6760]">
                          Submitted {formatDateTime(submission.submitted_at)}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {submission.status ? (
                          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusTone[submission.status] || 'bg-[#f3ede6] text-[#5f5851]'}`}>
                            {submission.status}
                          </span>
                        ) : null}
                        {submission.assigned_severity ? (
                          <span className="rounded-full bg-[#fbe9e3] px-3 py-1 text-xs font-semibold text-[#9a4a18]">
                            {submission.assigned_severity}
                          </span>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading recent submissions...' : 'No recent submissions yet.'}
                </p>
              )}
            </div>
          </SectionCard>

          <SectionCard
            title="Monthly Trend"
            description="Submission and earnings trend from the last six months."
          >
            <div className="space-y-3">
              {data?.monthly_trend?.length ? (
                data.monthly_trend.map((entry) => (
                  <div key={entry.month} className="rounded-2xl bg-[#faf6f1] p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-[#2d2a26]">{entry.month}</p>
                        <p className="mt-1 text-xs uppercase tracking-[0.2em] text-[#8b8177]">Monthly activity</p>
                      </div>
                      <div className="text-right text-sm text-[#6d6760]">
                        <p>{entry.submissions} submissions</p>
                        <p className="font-semibold text-[#2d2a26]">{formatCurrency(entry.earnings)}</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading trend data...' : 'No trend data available yet.'}
                </p>
              )}
            </div>
          </SectionCard>
        </div>
      </PortalShell>
    </ProtectedRoute>
  );
}
