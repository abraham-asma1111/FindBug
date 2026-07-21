'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function FinanceReportsPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  
  // Financial Reports State
  const [reportType, setReportType] = useState('payments');
  const [dateRange, setDateRange] = useState('30d');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Calculate date range for financial reports
  const getDateRange = () => {
    const end = new Date();
    let start = new Date();
    
    switch (dateRange) {
      case '7d':
        start.setDate(end.getDate() - 7);
        break;
      case '30d':
        start.setDate(end.getDate() - 30);
        break;
      case '90d':
        start.setDate(end.getDate() - 90);
        break;
      case '1y':
        start.setFullYear(end.getFullYear() - 1);
        break;
      case 'ytd':
        start = new Date(end.getFullYear(), 0, 1);
        break;
      default:
        start.setDate(end.getDate() - 30);
    }
    
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  };

  const { start, end } = getDateRange();

  // Fetch report data based on type
  const { data: reportData, isLoading: reportLoading, refetch } = useApiQuery<any>({
    endpoint: reportType === 'payments' 
      ? `/finance/reports/payments?start_date=${start}&end_date=${end}&format=json`
      : reportType === 'payouts'
      ? `/finance/reports/payouts?start_date=${start}&end_date=${end}&format=json`
      : reportType === 'financial_summary'
      ? `/finance/reports/financial-summary?start_date=${start}&end_date=${end}`
      : `/finance/reports/tax?year=${new Date().getFullYear()}&format=json`,
  });

  const handleExportCSV = () => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api/v1';
    let url = '';
    
    if (reportType === 'payments') {
      url = `${baseUrl}/finance/reports/payments?start_date=${start}&end_date=${end}&format=csv`;
    } else if (reportType === 'payouts') {
      url = `${baseUrl}/finance/reports/payouts?start_date=${start}&end_date=${end}&format=csv`;
    } else if (reportType === 'tax') {
      url = `${baseUrl}/finance/reports/tax?year=${new Date().getFullYear()}&format=csv`;
    }
    
    if (url) {
      window.open(url, '_blank');
    }
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Financial Reports"
          subtitle="View and export financial data"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Financial Reports Content */}
            <div>
              {/* Report Configuration Section */}
              <div className="bg-[#1E293B] border border-[#334155] rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Report Configuration</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  {/* Report Type Selector */}
                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Report Type
                    </label>
                    <select
                      value={reportType}
                      onChange={(e) => setReportType(e.target.value)}
                      className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                    >
                      <option value="payments">Payment Reports</option>
                      <option value="payouts">Payout Reports</option>
                      <option value="financial_summary">Financial Summary</option>
                      <option value="tax">Tax Reports</option>
                    </select>
                  </div>

                  {/* Date Range Selector */}
                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Date Range
                    </label>
                    <select
                      value={dateRange}
                      onChange={(e) => setDateRange(e.target.value)}
                      className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                    >
                      <option value="7d">Last 7 Days</option>
                      <option value="30d">Last 30 Days</option>
                      <option value="90d">Last 90 Days</option>
                      <option value="1y">Last Year</option>
                      <option value="ytd">Year to Date</option>
                    </select>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end">
                  <Button
                    variant="primary"
                    size="md"
                    onClick={() => refetch()}
                    disabled={reportLoading}
                  >
                    {reportLoading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Loading...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Refresh Report
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Loading State */}
              {reportLoading && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
                  <div className="flex flex-col items-center gap-4">
                    <svg className="animate-spin h-12 w-12 text-[#3B82F6]" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p className="text-[#94A3B8]">Generating report...</p>
                  </div>
                </div>
              )}

              {/* Error State */}
              {!reportLoading && !reportData && (
                <div className="bg-[#1E293B] rounded-lg border border-[#DC2626] p-8 text-center">
                  <svg className="w-16 h-16 text-[#DC2626] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">Unable to Load Report</h3>
                  <p className="text-[#94A3B8] mb-4">There was an error loading the report data. Please try again.</p>
                  <Button variant="primary" size="md" onClick={() => refetch()}>
                    Retry
                  </Button>
                </div>
              )}

              {/* Report Data Display */}
              {!reportLoading && reportData && (
                <div className="space-y-6">
                  {/* Summary Cards */}
                  {reportData.summary && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {reportData.summary.total_amount !== undefined && (
                        <div className="bg-[#1E293B] border border-[#334155] rounded-lg p-6">
                          <p className="text-[#64748B] text-sm mb-2">Total Amount</p>
                          <p className="text-[#F8FAFC] text-3xl font-bold">
                            {reportData.summary.total_amount.toLocaleString()} ETB
                          </p>
                        </div>
                      )}
                      {reportData.summary.total_transactions !== undefined && (
                        <div className="bg-[#1E293B] border border-[#334155] rounded-lg p-6">
                          <p className="text-[#64748B] text-sm mb-2">Total Transactions</p>
                          <p className="text-[#F8FAFC] text-3xl font-bold">
                            {reportData.summary.total_transactions.toLocaleString()}
                          </p>
                        </div>
                      )}
                      {reportData.summary.average_amount !== undefined && (
                        <div className="bg-[#1E293B] border border-[#334155] rounded-lg p-6">
                          <p className="text-[#64748B] text-sm mb-2">Average Amount</p>
                          <p className="text-[#F8FAFC] text-3xl font-bold">
                            {reportData.summary.average_amount.toLocaleString()} ETB
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Data Table */}
                  {reportData.data && reportData.data.length > 0 ? (
                    <div className="bg-[#1E293B] border border-[#334155] rounded-lg overflow-hidden">
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead className="bg-[#0F172A] border-b border-[#334155]">
                            <tr>
                              {Object.keys(reportData.data[0]).map((key) => (
                                <th
                                  key={key}
                                  className="px-6 py-4 text-left text-xs font-semibold text-[#CBD5E1] uppercase tracking-wider whitespace-nowrap"
                                >
                                  {key.replace(/_/g, ' ')}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#334155]">
                            {reportData.data.map((row: any, idx: number) => (
                              <tr 
                                key={idx} 
                                onClick={() => {
                                  const id = row.payment_id || row.payout_id || row.user_id;
                                  if (id) {
                                    if (reportType === 'payments') {
                                      router.push(`/finance/reports/payments/${id}`);
                                    } else if (reportType === 'payouts') {
                                      router.push(`/finance/reports/payouts/${id}`);
                                    }
                                  }
                                }}
                                className="hover:bg-[#0F172A] transition-colors duration-150 cursor-pointer"
                              >
                                {Object.entries(row).map(([key, value]: [string, any], cellIdx) => (
                                  <td key={cellIdx} className="px-6 py-4 text-sm">
                                    <span className={`${
                                      typeof value === 'number' && key.includes('amount')
                                        ? 'font-semibold text-[#10B981]'
                                        : key.includes('status')
                                        ? value === 'completed' || value === 'approved' || value === 'paid'
                                          ? 'text-[#10B981] font-medium'
                                          : value === 'pending'
                                          ? 'text-[#F59E0B] font-medium'
                                          : value === 'failed' || value === 'rejected'
                                          ? 'text-[#EF4444] font-medium'
                                          : 'text-[#E2E8F0]'
                                        : key.includes('severity')
                                        ? value === 'critical'
                                          ? 'text-[#EF4444] font-semibold'
                                          : value === 'high'
                                          ? 'text-[#F97316] font-semibold'
                                          : value === 'medium'
                                          ? 'text-[#F59E0B] font-medium'
                                          : value === 'low'
                                          ? 'text-[#3B82F6] font-medium'
                                          : 'text-[#E2E8F0]'
                                        : 'text-[#E2E8F0]'
                                    }`}>
                                      {typeof value === 'number' && key.includes('amount')
                                        ? `${value.toLocaleString()} ETB`
                                        : typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)
                                        ? new Date(value).toLocaleDateString('en-US', { 
                                            year: 'numeric', 
                                            month: 'short', 
                                            day: 'numeric' 
                                          })
                                        : String(value)}
                                    </span>
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
                      <svg className="w-16 h-16 text-[#64748B] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Data Available</h3>
                      <p className="text-[#94A3B8]">
                        No {reportType.replace('_', ' ')} data found for the selected date range.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
