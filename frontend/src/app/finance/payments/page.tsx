'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function FinancePaymentsPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') || 'pending';
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = statusFilter === 'all' 
    ? '/payments' 
    : `/payments?status=${statusFilter}`;

  const { data, isLoading } = useApiQuery<any>({
    endpoint,
  });

  const payments = data?.payments || [];

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      pending: { bg: 'bg-[#F59E0B]', label: 'PENDING' },
      approved: { bg: 'bg-[#3B82F6]', label: 'APPROVED' },
      completed: { bg: 'bg-[#10B981]', label: 'COMPLETED' },
      rejected: { bg: 'bg-[#EF4444]', label: 'REJECTED' },
      processing: { bg: 'bg-[#F59E0B]', label: 'PROCESSING' },
    };
    const config = statusMap[status] || { bg: 'bg-[#94A3B8]', label: status.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const handleLogout = () => {
    logout();
    router.replace('/auth/login');
  };

  // Filter payments by search
  const filteredPayments = payments.filter((payment: any) => {
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
          <div className="flex">
            {/* Sidebar */}
            <aside className="w-64 bg-[#020617] border-r border-[#1E293B] min-h-screen sticky top-0">
              <div className="p-6 border-b border-[#1E293B]">
                <Link href="/" className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#EF2330] rounded-lg flex items-center justify-center text-white font-bold text-lg">
                    F
                  </div>
                  <span className="text-[#F8FAFC] font-bold text-lg">FindBug</span>
                </Link>
              </div>

              <nav className="p-4">
                {/* Status Filters */}
                <div className="mb-6">
                  <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
                    Status
                  </h3>
                  <div className="space-y-1">
                    <Link
                      href="/finance/payments?status=pending"
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                        statusFilter === 'pending'
                          ? 'bg-[#1E40AF] text-[#F8FAFC]'
                          : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
                      }`}
                    >
                      <span className="w-2 h-2 rounded-full bg-[#F59E0B]"></span>
                      Pending Approval
                    </Link>
                    <Link
                      href="/finance/payments?status=approved"
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                        statusFilter === 'approved'
                          ? 'bg-[#1E40AF] text-[#F8FAFC]'
                          : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
                      }`}
                    >
                      <span className="w-2 h-2 rounded-full bg-[#3B82F6]"></span>
                      Approved
                    </Link>
                    <Link
                      href="/finance/payments?status=processing"
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                        statusFilter === 'processing'
                          ? 'bg-[#1E40AF] text-[#F8FAFC]'
                          : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
                      }`}
                    >
                      <span className="w-2 h-2 rounded-full bg-[#F59E0B]"></span>
                      Processing
                    </Link>
                    <Link
                      href="/finance/payments?status=completed"
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                        statusFilter === 'completed'
                          ? 'bg-[#1E40AF] text-[#F8FAFC]'
                          : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
                      }`}
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
                      href="/finance/dashboard"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                      </svg>
                      Dashboard
                    </Link>
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
                    <h1 className="text-2xl font-bold text-[#F8FAFC] mt-1">
                      {statusFilter === 'pending' && 'Pending Payments'}
                      {statusFilter === 'approved' && 'Approved Payments'}
                      {statusFilter === 'processing' && 'Processing Payments'}
                      {statusFilter === 'completed' && 'Completed Payments'}
                      {statusFilter === 'all' && 'All Payments'}
                    </h1>
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
                {/* Search and Actions */}
                <div className="flex items-center gap-3 mb-6">
                  <input
                    type="text"
                    placeholder="Search by researcher or report ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="flex-1 px-4 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] text-sm placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                  />
                  <Button variant="outline" size="sm">
                    Export
                  </Button>
                  {statusFilter === 'pending' && (
                    <Button className="bg-[#3B82F6] hover:bg-[#2563EB]" size="sm">
                      Bulk Approve
                    </Button>
                  )}
                </div>

                {/* Payments List */}
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
                    filteredPayments.map((payment: any) => (
                      <Link key={payment.id} href={`/finance/payments/${payment.id}`}>
                        <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-5 hover:border-[#3B82F6] transition-colors cursor-pointer">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h3 className="text-base font-semibold text-[#F8FAFC]">
                                  {payment.report_title || `Payment #${payment.id.slice(0, 8)}`}
                                </h3>
                                {getStatusBadge(payment.status)}
                              </div>
                              <p className="text-sm text-[#94A3B8]">
                                {payment.researcher_name || 'Researcher'} • {(payment.amount || 0).toLocaleString()} ETB • {new Date(payment.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="text-right ml-6">
                              <p className="text-xl font-bold text-[#10B981]">
                                ${(payment.amount || 0).toLocaleString()}
                              </p>
                              <p className="text-xs text-[#94A3B8] mt-1">
                                + ${((payment.amount || 0) * 0.3).toLocaleString()} commission
                              </p>
                            </div>
                          </div>
                        </div>
                      </Link>
                    ))
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
