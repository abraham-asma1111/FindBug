'use client';

import { useEffect, useMemo } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import BountyTrendChart from '@/components/ui/BountyTrendChart';

export default function AdminFinancePage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // ── Same endpoints as Finance Officer Portal ──────────────────────────────
  const { data: kpisData }         = useApiQuery<any>({ endpoint: '/finance/analytics/executive-kpis' });
  const { data: bountyData }       = useApiQuery<any>({ endpoint: '/finance/analytics/bounty-economics' });
  const { data: recentPayments }   = useApiQuery<any>({ endpoint: '/finance/analytics/recent-payments?limit=10' });
  const { data: topPrograms }      = useApiQuery<any>({ endpoint: '/finance/analytics/top-programs-by-reports?limit=5' });
  const { data: programData }      = useApiQuery<any>({ endpoint: '/finance/analytics/program-economics' });

  // ── KPI values ────────────────────────────────────────────────────────────
  const totalRevenue     = kpisData?.total_revenue     ?? 0;
  const totalPayouts     = kpisData?.total_payouts     ?? 0;
  const netProfit        = kpisData?.net_profit        ?? 0;
  const pendingPayouts   = kpisData?.pending_payouts   ?? 0;
  const revenueGrowth    = kpisData?.revenue_growth    ?? 0;

  // ── 12-month bounty trend chart (zero-filled scaffold) ───────────────────
  const chartData = useMemo(() => {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const scaffold = months.map(m => ({ date: m, amount: 0, commission: 0 }));
    bountyData?.monthly_trend?.forEach((t: any) => {
      const label: string = t.month_label || t.month || '';
      const short = label.length > 3
        ? new Date(label + '-01').toLocaleString('en-US', { month: 'short' })
        : label;
      const idx = months.indexOf(short);
      if (idx !== -1) {
        scaffold[idx].amount     = t.total_bounties  ?? 0;
        scaffold[idx].commission = t.total_commission ?? 0;
      }
    });
    return scaffold;
  }, [bountyData]);

  const payments = recentPayments?.payments ?? [];
  const programs  = topPrograms?.programs   ?? [];

  const severityColor: Record<string, string> = {
    critical: 'bg-[#EF4444] text-white',
    high:     'bg-[#F59E0B] text-white',
    medium:   'bg-[#FBBF24] text-white',
    low:      'bg-[#10B981] text-white',
  };
  const statusColor: Record<string, string> = {
    completed:  'bg-[#10B981] text-white',
    approved:   'bg-[#3B82F6] text-white',
    processing: 'bg-[#F59E0B] text-white',
    pending:    'bg-[#94A3B8] text-white',
  };

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Finance"
          subtitle="Platform financial overview"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* ── KPI Cards ──────────────────────────────────────────────── */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 mb-6">
            <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Platform Revenue</p>
              <p className="mt-2 text-3xl font-bold text-[#10B981]">ETB {totalRevenue.toLocaleString()}</p>
              <p className="mt-1 text-xs text-[#64748B]">
                {revenueGrowth >= 0 ? '↑' : '↓'} {Math.abs(revenueGrowth).toFixed(1)}% from last month
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Total Paid Out</p>
              <p className="mt-2 text-3xl font-bold text-[#EF4444]">ETB {totalPayouts.toLocaleString()}</p>
              <p className="mt-1 text-xs text-[#64748B]">Researcher payouts</p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Net Profit</p>
              <p className="mt-2 text-3xl font-bold text-[#3B82F6]">ETB {netProfit.toLocaleString()}</p>
              <p className="mt-1 text-xs text-[#64748B]">Platform commission</p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Pending Payouts</p>
              <p className="mt-2 text-3xl font-bold text-[#F59E0B]">ETB {pendingPayouts.toLocaleString()}</p>
              <p className="mt-1 text-xs text-[#64748B]">Awaiting processing</p>
            </div>
          </div>

          {/* ── Trend Chart + Top Programs ─────────────────────────────── */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-6">
            <div className="lg:col-span-8 bg-[#0F172A] rounded-xl p-5 border border-[#1E3A5F]">
              <h2 className="text-base font-semibold text-[#F8FAFC] mb-1">Bounty Payment Trend</h2>
              <p className="text-xs text-[#475569] mb-3">Last 12 Months</p>
              <BountyTrendChart data={chartData} height={260} />
            </div>
            <div className="lg:col-span-4 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="flex items-center justify-between p-4 border-b border-[#334155]">
                <h2 className="text-sm font-semibold text-[#F8FAFC]">Top Programs by Reports</h2>
              </div>
              <div className="divide-y divide-[#334155]">
                {programs.length > 0 ? programs.map((p: any, i: number) => (
                  <div key={p.program_id || i} className="flex items-center justify-between p-3">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-[#3B82F6]/20 text-[#3B82F6] text-xs font-bold flex items-center justify-center">{i + 1}</span>
                      <span className="text-sm text-[#F8FAFC] truncate max-w-[130px]">{p.program_name}</span>
                    </div>
                    <span className="text-sm font-bold text-[#3B82F6]">{p.report_count} reports</span>
                  </div>
                )) : (
                  <div className="py-8 text-center text-[#64748B] text-xs">No data yet</div>
                )}
              </div>
            </div>
          </div>

          {/* ── Recent Payouts Table ───────────────────────────────────── */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] mb-6">
            <div className="flex items-center justify-between p-4 border-b border-[#334155]">
              <h2 className="text-base font-semibold text-[#F8FAFC]">Recent Payouts</h2>
            </div>
            {payments.length === 0 ? (
              <div className="py-10 text-center text-[#64748B] text-sm">No payouts found</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#334155]">
                      <th className="text-left py-2 px-3 text-xs font-semibold text-[#94A3B8] uppercase">Researcher</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-[#94A3B8] uppercase">Report</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-[#94A3B8] uppercase">Program</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-[#94A3B8] uppercase">Severity</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-[#94A3B8] uppercase">Amount</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-[#94A3B8] uppercase">Status</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-[#94A3B8] uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.map((p: any) => (
                      <tr key={p.payment_id} className="border-b border-[#334155]/50 hover:bg-[#334155]/20 transition-colors">
                        <td className="py-2.5 px-3">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-full flex items-center justify-center text-white text-xs font-bold">
                              {(p.researcher_name || 'R')[0].toUpperCase()}
                            </div>
                            <span className="text-xs text-[#F8FAFC] font-medium">{p.researcher_name || 'Unknown'}</span>
                          </div>
                        </td>
                        <td className="py-2.5 px-3 text-xs text-[#94A3B8]">
                          {p.report_number ? `#${p.report_number}` : p.report_title || '—'}
                        </td>
                        <td className="py-2.5 px-3 text-xs text-[#94A3B8] max-w-[100px] truncate">{p.program_name || '—'}</td>
                        <td className="py-2.5 px-3">
                          {p.severity
                            ? <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${severityColor[p.severity.toLowerCase()] ?? 'bg-[#64748B] text-white'}`}>{p.severity}</span>
                            : <span className="text-xs text-[#64748B]">—</span>}
                        </td>
                        <td className="py-2.5 px-3 text-right text-xs font-bold text-[#10B981]">
                          ETB {p.researcher_amount?.toLocaleString()}
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${statusColor[p.status] ?? 'bg-[#64748B] text-white'}`}>{p.status}</span>
                        </td>
                        <td className="py-2.5 px-3 text-right text-xs text-[#94A3B8]">
                          {(p.completed_at || p.created_at)
                            ? new Date(p.completed_at || p.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                            : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
