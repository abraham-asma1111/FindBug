'use client';

import { useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function TransactionDetailPage() {
  const router = useRouter();
  const params = useParams();
  const transactionId = params.id as string;
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch all transactions and find the specific one
  const { data: historyData, isLoading } = useApiQuery<any>({
    endpoint: '/payments/history?limit=1000',
  });

  // Find the specific transaction
  const transaction = historyData?.payments?.find((p: any) => p.payment_id === transactionId);

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user && (
          <PortalShell
            user={user}
            title="Transaction Details"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <div className="flex items-center justify-center h-64">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#334155] border-t-[#3B82F6]"></div>
            </div>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  if (!transaction) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user && (
          <PortalShell
            user={user}
            title="Transaction Not Found"
            subtitle="The requested transaction could not be found"
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <div className="text-center py-12">
              <p className="text-[#94A3B8] mb-4">Transaction not found</p>
              <button
                onClick={() => router.push('/finance/transactions')}
                className="px-6 py-2 bg-[#3B82F6] text-white rounded-lg hover:bg-[#2563EB] transition-colors"
              >
                Back to Transactions
              </button>
            </div>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  const statusColor = 
    transaction.status === 'completed' ? 'text-[#10B981] bg-[#10B981]/20' :
    transaction.status === 'approved' ? 'text-[#3B82F6] bg-[#3B82F6]/20' :
    transaction.status === 'pending' ? 'text-[#F59E0B] bg-[#F59E0B]/20' :
    transaction.status === 'failed' ? 'text-[#EF4444] bg-[#EF4444]/20' :
    'text-[#64748B] bg-[#64748B]/20';

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user && (
        <PortalShell
          user={user}
          title="Transaction Details"
          subtitle={`Transaction ID: ${transaction.transaction_id || `TXN-${transactionId.slice(0, 8)}`}`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Breadcrumb Navigation */}
          <div className="mb-6">
            <nav className="flex items-center gap-2 text-sm">
              <button
                onClick={() => router.push('/finance/dashboard')}
                className="text-[#64748B] hover:text-[#F8FAFC] transition-colors"
              >
                Finance
              </button>
              <svg className="w-4 h-4 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <button
                onClick={() => router.push('/finance/transactions')}
                className="text-[#64748B] hover:text-[#F8FAFC] transition-colors"
              >
                Transactions
              </button>
              <svg className="w-4 h-4 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <span className="text-[#F8FAFC] font-medium">
                {transaction.transaction_id || `TXN-${transactionId.slice(0, 8)}`}
              </span>
            </nav>
          </div>

          {/* Streamlined Single Card Layout */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8">
            {/* Transaction Overview Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Transaction Overview
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Status</span>
                  <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${statusColor}`}>
                    {transaction.status}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Transaction ID</span>
                  <span className="text-[#F8FAFC] font-mono text-sm text-right">
                    {transaction.transaction_id || `TXN-${transactionId.slice(0, 8)}`}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Payment ID</span>
                  <span className="text-[#F8FAFC] font-mono text-sm text-right">{transactionId}</span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Transaction Type</span>
                  <span className="inline-block px-3 py-1 rounded-lg text-xs font-bold uppercase bg-[#8B5CF6]/20 text-[#8B5CF6]">
                    Bounty Payment
                  </span>
                </div>
                {transaction.payment_method && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Payment Method</span>
                    <span className="text-[#F8FAFC] font-medium text-right capitalize">{transaction.payment_method}</span>
                  </div>
                )}
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Transaction Date</span>
                  <span className="text-[#F8FAFC] font-medium text-right">
                    {new Date(transaction.created_at).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
                {transaction.approved_at && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Approval Date</span>
                    <span className="text-[#F8FAFC] font-medium text-right">
                      {new Date(transaction.approved_at).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                )}
                {transaction.status === 'completed' && transaction.completed_at && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Completion Date</span>
                    <span className="text-[#F8FAFC] font-medium text-right">
                      {new Date(transaction.completed_at).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Amount Breakdown Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Financial Breakdown
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Researcher Payout</span>
                  <span className="text-[#F8FAFC] font-bold text-right">
                    {transaction.researcher_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'} ETB
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Platform Commission</span>
                  <span className="text-[#F8FAFC] font-bold text-right">
                    {transaction.commission_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'} ETB
                  </span>
                </div>
                <div className="pt-3 border-t border-[#334155]">
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#F8FAFC] font-bold flex-shrink-0">Total Transaction Amount</span>
                    <span className="text-[#10B981] font-bold text-2xl text-right">
                      {transaction.total_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'} ETB
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Researcher Information Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Researcher Information
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Researcher Name</span>
                  <span className="text-[#F8FAFC] font-medium text-right">{transaction.researcher_name || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Payout Amount</span>
                  <span className="text-[#10B981] font-bold text-lg text-right">
                    {transaction.researcher_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'} ETB
                  </span>
                </div>
              </div>
            </div>

            {/* Organization Information Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Organization Information
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Organization Name</span>
                  <span className="text-[#F8FAFC] font-medium text-right">{transaction.organization_name || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Total Amount Paid</span>
                  <span className="text-[#10B981] font-bold text-lg text-right">
                    {transaction.total_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'} ETB
                  </span>
                </div>
              </div>
            </div>

            {/* Related Vulnerability Report Section */}
            {transaction.report_id && (
              <div>
                <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                  Related Vulnerability Report
                </h2>
                <div className="space-y-4">
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Report Number</span>
                    <span className="text-[#F8FAFC] font-mono text-right">{transaction.report_number}</span>
                  </div>
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Report Title</span>
                    <span className="text-[#F8FAFC] font-medium text-right">{transaction.report_title}</span>
                  </div>
                  {transaction.report_severity && (
                    <div className="flex justify-between items-center gap-4">
                      <span className="text-[#94A3B8] flex-shrink-0">Severity Level</span>
                      <span className={`inline-block px-3 py-1 rounded-lg text-xs font-bold uppercase ${
                        transaction.report_severity === 'critical' ? 'bg-[#EF4444]/20 text-[#EF4444]' :
                        transaction.report_severity === 'high' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' :
                        transaction.report_severity === 'medium' ? 'bg-[#3B82F6]/20 text-[#3B82F6]' :
                        'bg-[#10B981]/20 text-[#10B981]'
                      }`}>
                        {transaction.report_severity}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
