'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceProgramDetailPage() {
  const params = useParams();
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const programId = params.id as string;
  const [activeTab, setActiveTab] = useState<'overview' | 'reports' | 'payments' | 'researchers'>('overview');

  useEffect(() => {
    document.documentElement.classList.add('dark');
    document.body.style.backgroundColor = '#0a0e1a';
  }, []);

  // Fetch program details with enriched stats
  const { data: programDetails, isLoading: detailsLoading } = useApiQuery<any>({
    endpoint: `/programs/${programId}?enrich_stats=true`,
  });

  // Get organization ID from program details to fetch all programs from same org
  const organizationId = programDetails?.organization_id;

  // Fetch all programs from the same organization for navigation
  const { data: allProgramsData } = useApiQuery<any>({
    endpoint: organizationId ? `/programs?organization_id=${organizationId}&enrich_stats=true` : null,
    enabled: !!organizationId,
  });

  const allPrograms = allProgramsData?.programs || [];
  const currentIndex = allPrograms.findIndex((prog: any) => prog.id === programId);
  const previousProgram = currentIndex > 0 ? allPrograms[currentIndex - 1] : null;
  const nextProgram = currentIndex < allPrograms.length - 1 ? allPrograms[currentIndex + 1] : null;

  // Fetch program reports
  const { data: programReports } = useApiQuery<any>({
    endpoint: `/reports?program_id=${programId}`,
    enabled: activeTab === 'reports',
  });

  // Fetch program payments
  const { data: programPayments } = useApiQuery<any>({
    endpoint: `/payments/history?program_id=${programId}`,
    enabled: activeTab === 'payments',
  });

  // Fetch program researchers
  const { data: programResearchers } = useApiQuery<any>({
    endpoint: `/programs/${programId}/participants`,
    enabled: activeTab === 'researchers',
  });

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user && (
        <PortalShell
          user={user}
          title={programDetails?.name || 'Program Details'}
          subtitle="Finance Officer View"
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
              onClick={() => router.push('/finance/organizations')}
              className="text-[#64748B] hover:text-[#F8FAFC] transition-colors"
            >
              Organizations
            </button>
            {programDetails?.organization && (
              <>
                <svg className="w-4 h-4 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                <button
                  onClick={() => router.push(`/finance/organizations/${programDetails.organization_id}`)}
                  className="text-[#64748B] hover:text-[#F8FAFC] transition-colors"
                >
                  {programDetails.organization.company_name}
                </button>
              </>
            )}
            <svg className="w-4 h-4 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[#F8FAFC] font-medium">
              {programDetails?.name || 'Loading...'}
            </span>
          </nav>
        </div>

        {detailsLoading ? (
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#334155] border-t-[#3B82F6] mb-4"></div>
            <p className="text-[#94A3B8]">Loading program details...</p>
          </div>
        ) : !programDetails ? (
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
            <p className="text-[#94A3B8]">Program not found</p>
          </div>
        ) : (
          <>
            {/* Program Header Card */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-8 border border-[#334155] shadow-xl mb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-6">
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] flex items-center justify-center shadow-lg">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-[#F8FAFC] mb-2">
                      {programDetails.name}
                    </h1>
                    <div className="flex items-center gap-4">
                      <span className={`px-4 py-2 rounded-lg text-sm font-bold uppercase ${
                        programDetails.status === 'public' 
                          ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30' 
                          : programDetails.status === 'draft'
                          ? 'bg-[#64748B]/20 text-[#64748B] border border-[#64748B]/30'
                          : programDetails.status === 'paused'
                          ? 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30'
                          : 'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30'
                      }`}>
                        {programDetails.status}
                      </span>
                      <span className="text-[#64748B] text-sm capitalize">
                        {programDetails.type || 'Bug Bounty'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-2">Bounty Range</p>
                  <p className="text-[#10B981] font-bold text-2xl">
                    {programDetails.min_bounty?.toLocaleString() || 0} - {programDetails.max_bounty?.toLocaleString() || 0}
                  </p>
                  <p className="text-[#64748B] text-sm mt-1">ETB</p>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Total Reports</p>
                <p className="text-4xl font-bold text-[#F8FAFC] mb-1">
                  {programDetails.total_reports || 0}
                </p>
                <p className="text-[#10B981] text-sm font-medium">{programDetails.valid_reports || 0} valid</p>
              </div>

              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#8B5CF6]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Researchers</p>
                <p className="text-4xl font-bold text-[#F8FAFC] mb-1">
                  {programDetails.total_researchers || 0}
                </p>
                <p className="text-[#8B5CF6] text-sm font-medium">{programDetails.researchers_with_reports || 0} active</p>
              </div>

              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#10B981]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Bounties Paid</p>
                <p className="text-4xl font-bold text-[#10B981] mb-1">
                  {(programDetails.total_bounties_paid || 0).toLocaleString()}
                </p>
                <p className="text-[#64748B] text-sm font-medium">ETB total</p>
              </div>

              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#F59E0B]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Pending Payments</p>
                <p className="text-4xl font-bold text-[#F59E0B] mb-1">
                  {programDetails.pending_payments || 0}
                </p>
                <p className="text-[#64748B] text-sm font-medium">Awaiting approval</p>
              </div>
            </div>

            {/* Tabs */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] overflow-hidden shadow-xl">
              <div className="border-b border-[#334155] bg-[#0F172A]/50 px-8 py-1">
                <div className="flex gap-8">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`py-4 px-4 font-semibold text-base transition-all border-b-3 ${
                      activeTab === 'overview'
                        ? 'border-[#3B82F6] text-[#3B82F6]'
                        : 'border-transparent text-[#64748B] hover:text-[#F8FAFC] hover:border-[#475569]'
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab('reports')}
                    className={`py-4 px-4 font-semibold text-base transition-all border-b-3 ${
                      activeTab === 'reports'
                        ? 'border-[#3B82F6] text-[#3B82F6]'
                        : 'border-transparent text-[#64748B] hover:text-[#F8FAFC] hover:border-[#475569]'
                    }`}
                  >
                    Reports
                  </button>
                  <button
                    onClick={() => setActiveTab('payments')}
                    className={`py-4 px-4 font-semibold text-base transition-all border-b-3 ${
                      activeTab === 'payments'
                        ? 'border-[#3B82F6] text-[#3B82F6]'
                        : 'border-transparent text-[#64748B] hover:text-[#F8FAFC] hover:border-[#475569]'
                    }`}
                  >
                    Payments
                  </button>
                  <button
                    onClick={() => setActiveTab('researchers')}
                    className={`py-4 px-4 font-semibold text-base transition-all border-b-3 ${
                      activeTab === 'researchers'
                        ? 'border-[#3B82F6] text-[#3B82F6]'
                        : 'border-transparent text-[#64748B] hover:text-[#F8FAFC] hover:border-[#475569]'
                    }`}
                  >
                    Researchers
                  </button>
                </div>
              </div>

              {/* Tab Content */}
              <div className="p-6 bg-[#0F172A]/30">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    <div className="bg-[#1E293B]/50 rounded-xl p-8 border border-[#334155]/50">
                      <h3 className="text-2xl font-bold text-[#F8FAFC] mb-6">Program Information</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Program Name</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg">{programDetails.name}</p>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Organization</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg">{programDetails.organization?.company_name || 'N/A'}</p>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Program Type</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg capitalize">{programDetails.type || 'Bug Bounty'}</p>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Created Date</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg">
                            {programDetails.created_at 
                              ? new Date(programDetails.created_at).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })
                              : 'N/A'}
                          </p>
                        </div>
                      </div>
                      {programDetails.description && (
                        <div className="mt-6 bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Description</p>
                          <p className="text-[#F8FAFC] leading-relaxed">{programDetails.description}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Reports Tab */}
                {activeTab === 'reports' && (
                  <div className="bg-[#1E293B]/50 rounded-xl border border-[#334155]/50 overflow-hidden">
                    <div className="p-6 border-b border-[#334155]/50">
                      <h3 className="text-2xl font-bold text-[#F8FAFC]">Program Reports</h3>
                    </div>
                    {programReports?.reports && programReports.reports.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="bg-[#0F172A]/50 border-b border-[#334155]/50">
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Report</th>
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Severity</th>
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Status</th>
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Bounty</th>
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Submitted</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#334155]/30">
                            {programReports.reports.map((report: any) => (
                              <tr 
                                key={report.id} 
                                className="hover:bg-[#1E293B]/30 transition-colors cursor-pointer"
                                onClick={() => router.push(`/finance/reports/${report.id}`)}
                              >
                                <td className="px-6 py-4">
                                  <div>
                                    <p className="text-[#F8FAFC] font-semibold">{report.title}</p>
                                    <p className="text-[#64748B] text-sm mt-1">{report.report_number}</p>
                                  </div>
                                </td>
                                <td className="px-6 py-4">
                                  <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase inline-block ${
                                    report.assigned_severity === 'critical' ? 'bg-[#EF4444]/20 text-[#EF4444]' :
                                    report.assigned_severity === 'high' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' :
                                    report.assigned_severity === 'medium' ? 'bg-[#3B82F6]/20 text-[#3B82F6]' :
                                    report.assigned_severity === 'low' ? 'bg-[#10B981]/20 text-[#10B981]' :
                                    'bg-[#64748B]/20 text-[#64748B]'
                                  }`}>
                                    {report.assigned_severity || 'Unassigned'}
                                  </span>
                                </td>
                                <td className="px-6 py-4">
                                  <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase inline-block ${
                                    report.status === 'valid' || report.status === 'resolved' ? 'bg-[#10B981]/20 text-[#10B981]' :
                                    report.status === 'triaged' || report.status === 'new' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' :
                                    'bg-[#64748B]/20 text-[#64748B]'
                                  }`}>
                                    {report.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4">
                                  {report.bounty_amount ? (
                                    <span className="text-[#10B981] font-bold">
                                      {report.bounty_amount.toLocaleString()} ETB
                                    </span>
                                  ) : (
                                    <span className="text-[#64748B]">—</span>
                                  )}
                                </td>
                                <td className="px-6 py-4">
                                  <span className="text-[#F8FAFC]">
                                    {new Date(report.submitted_at).toLocaleDateString('en-US', {
                                      year: 'numeric',
                                      month: 'short',
                                      day: 'numeric'
                                    })}
                                  </span>
                                </td>
                                <td className="px-6 py-4 text-right">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      router.push(`/finance/reports/${report.id}`);
                                    }}
                                    className="text-[#3B82F6] hover:text-[#60A5FA] font-semibold text-sm transition-colors"
                                  >
                                    View
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-center py-16">
                        <div className="w-16 h-16 rounded-full bg-[#334155]/30 flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <p className="text-[#94A3B8] text-lg">No reports found for this program</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Payments Tab */}
                {activeTab === 'payments' && (
                  <div className="bg-[#1E293B]/50 rounded-xl p-8 border border-[#334155]/50">
                    <h3 className="text-2xl font-bold text-[#F8FAFC] mb-6">Program Payments</h3>
                    {programPayments?.payments && programPayments.payments.length > 0 ? (
                      <div className="space-y-4">
                        {programPayments.payments.map((payment: any) => (
                          <div key={payment.payment_id} className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30 hover:border-[#3B82F6]/30 transition-all">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-3">
                                  <h4 className="text-[#F8FAFC] font-bold text-lg">{payment.report_title || 'Report Payment'}</h4>
                                  <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase ${
                                    payment.status === 'completed' ? 'bg-[#10B981]/20 text-[#10B981]' :
                                    payment.status === 'approved' ? 'bg-[#3B82F6]/20 text-[#3B82F6]' :
                                    payment.status === 'pending' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' :
                                    payment.status === 'failed' ? 'bg-[#EF4444]/20 text-[#EF4444]' :
                                    'bg-[#64748B]/20 text-[#64748B]'
                                  }`}>
                                    {payment.status}
                                  </span>
                                </div>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                  <div>
                                    <p className="text-[#64748B] mb-1">Researcher</p>
                                    <p className="text-[#F8FAFC] font-medium">{payment.researcher_name}</p>
                                  </div>
                                  <div>
                                    <p className="text-[#64748B] mb-1">Payment Method</p>
                                    <p className="text-[#F8FAFC] font-medium capitalize">{payment.payment_method || 'Not set'}</p>
                                  </div>
                                  <div>
                                    <p className="text-[#64748B] mb-1">Transaction ID</p>
                                    <p className="text-[#F8FAFC] font-mono text-xs">{payment.transaction_id || 'N/A'}</p>
                                  </div>
                                  <div>
                                    <p className="text-[#64748B] mb-1">KYC Status</p>
                                    <p className={`font-medium ${payment.kyc_verified ? 'text-[#10B981]' : 'text-[#F59E0B]'}`}>
                                      {payment.kyc_verified ? '✓ Verified' : '⚠ Not Verified'}
                                    </p>
                                  </div>
                                </div>
                                {payment.failure_reason && (
                                  <div className="mt-3 p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg">
                                    <p className="text-[#EF4444] text-sm">
                                      <span className="font-bold">Failure Reason:</span> {payment.failure_reason}
                                    </p>
                                  </div>
                                )}
                              </div>
                              <div className="text-right ml-6">
                                <p className="text-[#64748B] text-sm mb-1">Total Amount</p>
                                <p className="text-[#10B981] font-bold text-2xl mb-1">
                                  {payment.total_amount.toLocaleString()} ETB
                                </p>
                                <div className="text-xs text-[#64748B] space-y-1">
                                  <p>Researcher: {payment.researcher_amount.toLocaleString()} ETB</p>
                                  <p>Commission: {payment.commission_amount.toLocaleString()} ETB</p>
                                </div>
                                {payment.approved_at && (
                                  <p className="text-[#64748B] text-xs mt-2">
                                    Approved: {new Date(payment.approved_at).toLocaleDateString()}
                                  </p>
                                )}
                                {payment.payout_deadline && (
                                  <p className="text-[#F59E0B] text-xs mt-1">
                                    Deadline: {new Date(payment.payout_deadline).toLocaleDateString()}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <div className="w-16 h-16 rounded-full bg-[#334155]/30 flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <p className="text-[#94A3B8] text-lg">No payments found for this program</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Researchers Tab */}
                {activeTab === 'researchers' && (
                  <div className="bg-[#1E293B]/50 rounded-xl border border-[#334155]/50 overflow-hidden">
                    <div className="p-6 border-b border-[#334155]/50">
                      <h3 className="text-2xl font-bold text-[#F8FAFC]">Program Researchers</h3>
                    </div>
                    {programResearchers && programResearchers.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="bg-[#0F172A]/50 border-b border-[#334155]/50">
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Researcher</th>
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Email</th>
                              <th className="px-6 py-4 text-center text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Reports</th>
                              <th className="px-6 py-4 text-center text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Reputation</th>
                              <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Joined</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#334155]/30">
                            {programResearchers.map((researcher: any) => (
                              <tr 
                                key={researcher.id} 
                                className="hover:bg-[#1E293B]/30 transition-colors"
                              >
                                <td className="px-6 py-4">
                                  <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] flex items-center justify-center flex-shrink-0">
                                      <span className="text-white font-bold">
                                        {researcher.username?.charAt(0).toUpperCase()}
                                      </span>
                                    </div>
                                    <span className="text-[#F8FAFC] font-semibold">{researcher.username}</span>
                                  </div>
                                </td>
                                <td className="px-6 py-4">
                                  <span className="text-[#94A3B8]">{researcher.email}</span>
                                </td>
                                <td className="px-6 py-4 text-center">
                                  <span className="inline-flex items-center justify-center px-3 py-1 rounded-lg bg-[#3B82F6]/10 text-[#3B82F6] font-bold">
                                    {researcher.reports_count || 0}
                                  </span>
                                </td>
                                <td className="px-6 py-4 text-center">
                                  <span className="inline-flex items-center justify-center px-3 py-1 rounded-lg bg-[#F59E0B]/10 text-[#F59E0B] font-bold">
                                    {researcher.reputation_score || 0}
                                  </span>
                                </td>
                                <td className="px-6 py-4">
                                  <span className="text-[#F8FAFC]">
                                    {researcher.joined_at 
                                      ? new Date(researcher.joined_at).toLocaleDateString('en-US', {
                                          year: 'numeric',
                                          month: 'short',
                                          day: 'numeric'
                                        })
                                      : 'N/A'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-center py-16">
                        <div className="w-16 h-16 rounded-full bg-[#334155]/30 flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                          </svg>
                        </div>
                        <p className="text-[#94A3B8] text-lg">No researchers found for this program</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
