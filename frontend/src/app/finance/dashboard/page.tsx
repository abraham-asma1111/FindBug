'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function FinanceDashboardPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch pending payments from REAL API
  const { data: pendingPaymentsData, isLoading } = useApiQuery<any>({
    endpoint: '/payments/history?status=pending&limit=100',
  });

  // Fetch all payments for stats calculation from REAL API
  const { data: allPaymentsData } = useApiQuery<any>({
    endpoint: '/payments/history?limit=1000',
  });

  const pendingPayments = pendingPaymentsData?.payments || [];
  const allPayments = allPaymentsData?.payments || [];

  // Calculate REAL statistics from backend data
  const stats = {
    pending_approval_amount: pendingPayments.reduce((sum: number, p: any) => sum + (p.amount || 0), 0),
    pending_payments: pendingPayments.length,
    this_month_paid: allPayments.filter((p: any) => {
      const date = new Date(p.created_at);
      const now = new Date();
      return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear() && p.status === 'completed';
    }).reduce((sum: number, p: any) => sum + (p.amount || 0), 0),
    platform_commission: allPayments.filter((p: any) => p.status === 'completed').reduce((sum: number, p: any) => sum + (p.amount || 0), 0) * 0.1,
    processing_amount: allPayments.filter((p: any) => p.status === 'processing').reduce((sum: number, p: any) => sum + (p.amount || 0), 0),
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-[#EF4444]',
      high: 'bg-[#F59E0B]',
      medium: 'bg-[#3B82F6]',
      low: 'bg-[#10B981]',
      info: 'bg-[#94A3B8]',
    };
    return colors[severity?.toLowerCase()] || 'bg-[#94A3B8]';
  };

  const handleLogout = () => {
    logout();
    router.replace('/auth/login');
  };

  // Filter payments based on active filter and search
  const filteredPayments = pendingPayments.filter((payment: any) => {
    // Apply filter
    if (activeFilter === 'high_priority' && payment.severity !== 'critical' && payment.severity !== 'high') {
      return false;
    }
    if (activeFilter === 'over_1000' && (payment.amount || 0) <= 1000) {
      return false;
    }
    if (activeFilter === 'this_week') {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      if (new Date(payment.created_at) < weekAgo) {
        return false;
      }
    }

    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        payment.researcher_name?.toLowerCase().includes(query) ||
        payment.report_number?.toLowerCase().includes(query) ||
        payment.id?.toLowerCase().includes(query)
      );
    }

    return true;
  });

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <div className="min-h-screen bg-[#0F172A]">
          {/* Two-column layout: Sidebar + Main Content */}
          <div className="flex">
            {/* Sidebar - Screenshot Style */}
            <aside className="w-64 bg-[#020617] border-r border-[#1E293B] min-h-screen sticky top-0">
              {/* Logo */}
              <div className="p-6 border-b border-[#1E293B]">
                <Link href="/" className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#EF2330] rounded-lg flex items-center justify-center text-white font-bold text-lg">
                    F
                  </div>
                  <span className="text-[#F8FAFC] font-bold text-lg">FindBug</span>
                </Link>
              </div>

              {/* Navigation */}
              <nav className="p-4">
                {/* Status Filters */}
                <div className="mb-6">
                  <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
                    Status
                  </h3>
                  <div className="space-y-1">
                    <Link
                      href="/finance/payments?status=pending"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium bg-[#1E40AF] text-[#F8FAFC]"
                    >
                      <span className="w-2 h-2 rounded-full bg-[#F59E0B]"></span>
                      Pending Approval
                    </Link>
                    <Link
                      href="/finance/payments?status=approved"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <span className="w-2 h-2 rounded-full bg-[#3B82F6]"></span>
                      Approved
                    </Link>
                    <Link
                      href="/finance/payments?status=processing"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <span className="w-2 h-2 rounded-full bg-[#F59E0B]"></span>
                      Processing
                    </Link>
                    <Link
                      href="/finance/payments?status=completed"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <span className="w-2 h-2 rounded-full bg-[#10B981]"></span>
                      Completed
                    </Link>
                  </div>
                </div>

                {/* Reports Section */}
                <div className="mb-6 pt-6 border-t border-[#1E293B]">
                  <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
                    Reports
                  </h3>
                  <div className="space-y-1">
                    <Link
                      href="/finance/reports"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      Financial Overview
                    </Link>
                    <Link
                      href="/finance/analytics"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Analytics
                    </Link>
                  </div>
                </div>

                {/* Management Section */}
                <div className="pt-6 border-t border-[#1E293B]">
                  <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
                    Management
                  </h3>
                  <div className="space-y-1">
                    <Link
                      href="/finance/payouts"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      Payouts
                    </Link>
                    <Link
                      href="/finance/kyc"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                      </svg>
                      KYC Verification
                    </Link>
                  </div>
                </div>
              </nav>
            </aside>

            {/* Main Content */}
            <div className="flex-1">
              {/* Top Header */}
              <header className="bg-[#020617] border-b border-[#1E293B] px-8 py-4 sticky top-0 z-10">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wide text-[#64748B]">Finance Portal</p>
                    <h1 className="text-2xl font-bold text-[#F8FAFC] mt-1">Pending Payments</h1>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={handleLogout}
                      className="px-4 py-2 bg-[#EF2330] hover:bg-[#DC2026] text-white rounded-lg text-sm font-medium transition"
                    >
                      Log Out
                    </button>
                  </div>
                </div>
              </header>

              {/* Main Content Area */}
              <main className="p-8">
                {/* Stats Grid - Screenshot Style */}
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-4 mb-6">
                  <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
                    <p className="text-xs text-[#94A3B8] uppercase tracking-wide mb-2">
                      Pending Approval
                    </p>
                    <p className="text-3xl font-bold text-[#F8FAFC] mb-1">
                      ${stats.pending_approval_amount.toLocaleString()}
                    </p>
                    <p className="text-xs text-[#94A3B8]">{stats.pending_payments} payments</p>
                  </div>
                  <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
                    <p className="text-xs text-[#94A3B8] uppercase tracking-wide mb-2">
                      This Month Paid
                    </p>
                    <p className="text-3xl font-bold text-[#F8FAFC] mb-1">
                      ${stats.this_month_paid.toLocaleString()}
                    </p>
                    <p className="text-xs text-[#10B981]">↑ 23% vs last month</p>
                  </div>
                  <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
                    <p className="text-xs text-[#94A3B8] uppercase tracking-wide mb-2">
                      Platform Commission
                    </p>
                    <p className="text-3xl font-bold text-[#F8FAFC] mb-1">
                      ${stats.platform_commission.toLocaleString()}
                    </p>
                    <p className="text-xs text-[#94A3B8]">30% of bounties</p>
                  </div>
                  <div className="bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
                    <p className="text-xs text-[#94A3B8] uppercase tracking-wide mb-2">
                      Processing
                    </p>
                    <p className="text-3xl font-bold text-[#F8FAFC] mb-1">
                      ${stats.processing_amount.toLocaleString()}
                    </p>
                    <p className="text-xs text-[#F59E0B]">{allPayments.filter((p: any) => p.status === 'processing').length} in progress</p>
                  </div>
                </div>

                {/* Charts Row - Screenshot Style */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                  {/* Payment Trends Chart */}
                  <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
                    <h3 className="text-base font-semibold text-[#F8FAFC] mb-4">Payment Trends</h3>
                    <div className="h-64 flex items-center justify-center text-[#94A3B8]">
                      <p>Chart visualization would go here</p>
                    </div>
                  </div>

                  {/* Payment Methods Chart */}
                  <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
                    <h3 className="text-base font-semibold text-[#F8FAFC] mb-4">Payment Methods</h3>
                    <div className="h-64 flex items-center justify-center text-[#94A3B8]">
                      <p>Donut chart would go here</p>
                    </div>
                  </div>
                </div>

                {/* Filter Buttons - Screenshot Style */}
                <div className="flex gap-2 mb-4 items-center">
                  <Button 
                    className={activeFilter === 'all' ? 'bg-[#3B82F6] hover:bg-[#2563EB]' : ''} 
                    variant={activeFilter === 'all' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setActiveFilter('all')}
                  >
                    All
                  </Button>
                  <Button 
                    variant={activeFilter === 'high_priority' ? 'primary' : 'outline'}
                    className={activeFilter === 'high_priority' ? 'bg-[#3B82F6] hover:bg-[#2563EB]' : ''}
                    size="sm"
                    onClick={() => setActiveFilter('high_priority')}
                  >
                    High Priority
                  </Button>
                  <Button 
                    variant={activeFilter === 'over_1000' ? 'primary' : 'outline'}
                    className={activeFilter === 'over_1000' ? 'bg-[#3B82F6] hover:bg-[#2563EB]' : ''}
                    size="sm"
                    onClick={() => setActiveFilter('over_1000')}
                  >
                    Over $1000
                  </Button>
                  <Button 
                    variant={activeFilter === 'this_week' ? 'primary' : 'outline'}
                    className={activeFilter === 'this_week' ? 'bg-[#3B82F6] hover:bg-[#2563EB]' : ''}
                    size="sm"
                    onClick={() => setActiveFilter('this_week')}
                  >
                    This Week
                  </Button>
                  <div className="flex-1"></div>
                  <input
                    type="text"
                    placeholder="Search by researcher or report ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="px-4 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] text-sm placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] w-80"
                  />
                </div>

                {/* Payment Cards - Screenshot Style with REAL DATA */}
                <div className="space-y-3">
                  {isLoading ? (
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
                      <p className="text-[#94A3B8]">Loading payments...</p>
                    </div>
                  ) : filteredPayments.length === 0 ? (
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
                      <p className="text-[#94A3B8]">No payments found</p>
                    </div>
                  ) : (
                    filteredPayments.map((payment: any) => {
                      const commission = (payment.amount || 0) * 0.3;
                      const total = (payment.amount || 0) + commission;
                      
                      return (
                        <div
                          key={payment.id}
                          className="bg-[#1E293B] rounded-lg border border-[#334155] p-5 hover:border-[#3B82F6] transition-colors"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h3 className="text-base font-semibold text-[#F8FAFC]">
                                  Report #{payment.report_number || payment.id.slice(0, 8)} - {payment.report_title || 'Vulnerability Report'}
                                </h3>
                                <span className="px-2 py-1 rounded text-xs font-bold uppercase bg-[#F59E0B] text-white">
                                  Pending Approval
                                </span>
                              </div>
                              <div className="flex items-center gap-4 text-sm text-[#94A3B8]">
                                <span className="flex items-center gap-1">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                  </svg>
                                  {payment.researcher_name || 'Researcher'}
                                </span>
                                <span>•</span>
                                <span>{payment.organization_name || 'Organization'}</span>
                                <span>•</span>
                                <span>⏱ Validated {payment.validated_at ? new Date(payment.validated_at).toLocaleDateString() : new Date(payment.created_at).toLocaleDateString()}</span>
                                {payment.severity && (
                                  <>
                                    <span>•</span>
                                    <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${getSeverityColor(payment.severity)} text-white`}>
                                      {payment.severity}
                                    </span>
                                  </>
                                )}
                              </div>
                            </div>
                            <div className="text-right ml-6">
                              <p className="text-2xl font-bold text-[#10B981]">
                                ${(payment.amount || 0).toLocaleString()}
                              </p>
                              <p className="text-xs text-[#94A3B8] mt-1">
                                + ${commission.toLocaleString()} commission
                              </p>
                              <p className="text-xs text-[#64748B]">
                                Total: ${total.toLocaleString()}
                              </p>
                            </div>
                          </div>
                          <div className="flex gap-2 mt-4 pt-4 border-t border-[#334155]">
                            <Link href={`/finance/payments/${payment.id}`}>
                              <Button variant="outline" size="sm">
                                View Details
                              </Button>
                            </Link>
                            <Button className="bg-[#3B82F6] hover:bg-[#2563EB]" size="sm">
                              Approve Payment
                            </Button>
                            <Button variant="outline" size="sm" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                              Reject
                            </Button>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </main>
            </div>
          </div>
        </div>
      ) : null}
    </ProtectedRoute>
  );
}
