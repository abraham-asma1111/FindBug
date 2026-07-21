'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function OrganizationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const organizationId = params.id as string;
  const [activeTab, setActiveTab] = useState<'overview' | 'subscription' | 'payments' | 'programs'>('overview');
  
  // Programs tab filters
  const [programSearch, setProgramSearch] = useState('');
  const [programStatusFilter, setProgramStatusFilter] = useState<string>('all');
  const [programSortBy, setProgramSortBy] = useState<'name' | 'reports' | 'bounties' | 'researchers'>('name');

  // Fetch all organizations for navigation
  const { data: allOrgsData } = useApiQuery<any>({
    endpoint: '/financial/organizations?limit=1000',
  });

  const allOrganizations = allOrgsData?.organizations || [];
  const currentIndex = allOrganizations.findIndex((org: any) => org.id === organizationId);
  const previousOrg = currentIndex > 0 ? allOrganizations[currentIndex - 1] : null;
  const nextOrg = currentIndex < allOrganizations.length - 1 ? allOrganizations[currentIndex + 1] : null;

  useEffect(() => {
    document.documentElement.classList.add('dark');
    document.body.style.backgroundColor = '#0a0e1a';
  }, []);

  // Fetch organization details
  const { data: orgDetails, isLoading: detailsLoading } = useApiQuery<any>({
    endpoint: `/financial/organizations/${organizationId}`,
  });

  // Fetch organization programs
  const { data: orgPrograms } = useApiQuery<any>({
    endpoint: `/programs?organization_id=${organizationId}&enrich_stats=true`,
    enabled: activeTab === 'programs',
  });

  // Fetch organization payment history
  const { data: paymentHistory } = useApiQuery<any>({
    endpoint: `/subscriptions/organization/${organizationId}/payments`,
    enabled: activeTab === 'payments',
  });

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user && (
        <PortalShell
          user={user}
          title={orgDetails?.company_name || 'Organization Details'}
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
            <svg className="w-4 h-4 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[#F8FAFC] font-medium">
              {orgDetails?.company_name || 'Loading...'}
            </span>
          </nav>
        </div>

        {detailsLoading ? (
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#334155] border-t-[#3B82F6] mb-4"></div>
            <p className="text-[#94A3B8]">Loading organization details...</p>
          </div>
        ) : !orgDetails ? (
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
            <p className="text-[#94A3B8]">Organization not found</p>
          </div>
        ) : (
          <>
            {/* Organization Header Card - Matching Reference Design */}
            <div className="rounded-xl overflow-hidden mb-4 shadow-xl border border-[#334155]">
              <div 
                className="relative min-h-[200px]"
                style={{
                  background: orgDetails.branding?.cover_image_url
                    ? `linear-gradient(rgba(15, 23, 42, 0.4), rgba(15, 23, 42, 0.4)), url(http://localhost:8002/api/v1/files/serve/${orgDetails.branding.cover_image_url})`
                    : 'linear-gradient(135deg, #1e3a8a 0%, #1e293b 50%, #0f172a 100%)',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }}
              >
                <div className="flex items-center justify-between relative z-10 p-8">
                  {/* Left: Logo + Company Info */}
                  <div className="flex items-center gap-6">
                    {/* Logo Container - White Background */}
                    <div 
                      className="w-20 h-20 rounded-lg flex items-center justify-center shadow-xl overflow-hidden bg-white border border-[#e2e8f0] flex-shrink-0"
                    >
                      {orgDetails.branding?.logo_url ? (
                        <img
                          src={`http://localhost:8002/api/v1/files/serve/${orgDetails.branding.logo_url}`}
                          alt={orgDetails.company_name}
                          className="w-full h-full object-contain p-2"
                          onError={(e) => {
                            console.error('Logo failed to load:', orgDetails.branding.logo_url);
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      ) : (
                        <span className="text-3xl font-bold text-[#1e3a8a]">
                          {orgDetails.company_name?.charAt(0).toUpperCase()}
                        </span>
                      )}
                    </div>
                    
                    {/* Company Info */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <svg className="w-5 h-5 text-[#10b981]" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-[#10b981] text-sm font-semibold">Verified Organization</span>
                      </div>
                      <h1 
                        className="text-3xl font-bold text-white mb-3"
                        style={{ textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)' }}
                      >
                        {orgDetails.company_name}
                      </h1>
                      <div 
                        className="flex items-center gap-6 text-sm text-white"
                        style={{ textShadow: '0 1px 3px rgba(0, 0, 0, 0.5)' }}
                      >
                        {orgDetails.email && (
                          <span className="flex items-center gap-2">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            {orgDetails.email}
                          </span>
                        )}
                        {orgDetails.website && (
                          <span className="flex items-center gap-2">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                            </svg>
                            {orgDetails.website}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Right: Plan Badge */}
                  <div className="flex-shrink-0">
                    <span className="inline-block px-6 py-3 rounded-lg text-base font-bold uppercase bg-gradient-to-r from-[#f59e0b] to-[#d97706] text-white shadow-xl">
                      {orgDetails.subscription?.tier || 'FREE'} PLAN
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Total Programs</p>
                <p className="text-4xl font-bold text-[#F8FAFC] mb-1">
                  {orgDetails.program_count || 0}
                </p>
                <p className="text-[#10B981] text-sm font-medium">Active bounty programs</p>
              </div>

              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#8B5CF6]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Total Reports</p>
                <p className="text-4xl font-bold text-[#F8FAFC] mb-1">
                  {orgDetails.report_count || 0}
                </p>
                <p className="text-[#8B5CF6] text-sm font-medium">Vulnerability submissions</p>
              </div>

              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#10B981]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Bounties Paid</p>
                <p className="text-4xl font-bold text-[#10B981] mb-1">
                  {orgDetails.total_bounties_paid?.toLocaleString() || 0}
                </p>
                <p className="text-[#64748B] text-sm font-medium">ETB total payouts</p>
              </div>

              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[#F59E0B]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-[#64748B] text-sm font-medium uppercase tracking-wider mb-2">Subscription</p>
                <span className={`inline-block px-4 py-2 rounded-lg text-sm font-bold uppercase ${
                  orgDetails.subscription?.status === 'active' ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30' : 'bg-[#64748B]/20 text-[#64748B] border border-[#64748B]/30'
                }`}>
                  {orgDetails.subscription?.status || 'Inactive'}
                </span>
                <p className="text-[#64748B] text-sm font-medium mt-3">Current plan status</p>
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
                    <span className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Overview
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('subscription')}
                    className={`py-4 px-4 font-semibold text-base transition-all border-b-3 ${
                      activeTab === 'subscription'
                        ? 'border-[#3B82F6] text-[#3B82F6]'
                        : 'border-transparent text-[#64748B] hover:text-[#F8FAFC] hover:border-[#475569]'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      Subscription
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('payments')}
                    className={`py-4 px-4 font-semibold text-base transition-all border-b-3 ${
                      activeTab === 'payments'
                        ? 'border-[#3B82F6] text-[#3B82F6]'
                        : 'border-transparent text-[#64748B] hover:text-[#F8FAFC] hover:border-[#475569]'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      Payments
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('programs')}
                    className={`py-4 px-4 font-semibold text-base transition-all border-b-3 ${
                      activeTab === 'programs'
                        ? 'border-[#3B82F6] text-[#3B82F6]'
                        : 'border-transparent text-[#64748B] hover:text-[#F8FAFC] hover:border-[#475569]'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                      Programs
                    </span>
                  </button>
                </div>
              </div>

              {/* Tab Content */}
              <div className="p-6 bg-[#0F172A]/30">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    <div className="bg-[#1E293B]/50 rounded-xl p-8 border border-[#334155]/50 backdrop-blur-sm">
                      <h3 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                          <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                        </div>
                        Organization Information
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Company Name</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg">
                            {orgDetails.company_name}
                          </p>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Industry</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg">
                            {orgDetails.industry || 'Not specified'}
                          </p>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Registration Date</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg">
                            {orgDetails.created_at 
                              ? new Date(orgDetails.created_at).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })
                              : 'N/A'}
                          </p>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Verification Status</p>
                          <span className={`inline-block px-4 py-2 rounded-lg text-sm font-bold uppercase ${
                            orgDetails.is_verified ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30' : 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30'
                          }`}>
                            {orgDetails.is_verified ? 'Verified' : 'Pending'}
                          </span>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Contact Email</p>
                          <p className="text-[#F8FAFC] font-semibold text-lg break-all">
                            {orgDetails.email || 'N/A'}
                          </p>
                        </div>
                        <div className="bg-[#0F172A]/50 rounded-lg p-5 border border-[#334155]/30">
                          <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-3">Website</p>
                          <p className="text-[#3B82F6] font-semibold text-lg break-all hover:underline">
                            {orgDetails.website || 'N/A'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Subscription Tab */}
                {activeTab === 'subscription' && (
                  <div className="space-y-6">
                    {/* Subscription Header Card */}
                    <div className="bg-[#1E293B]/50 rounded-xl p-8 border border-[#334155]/50 backdrop-blur-sm">
                      <h3 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#F59E0B]/10 flex items-center justify-center">
                          <svg className="w-5 h-5 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                        </div>
                        Current Subscription Plan
                      </h3>

                      {/* Plan Type & Status - Prominent Display */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
                        <div className="bg-gradient-to-br from-[#F59E0B]/10 to-[#D97706]/10 rounded-xl p-6 border border-[#F59E0B]/20">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-12 h-12 rounded-lg bg-[#F59E0B]/20 flex items-center justify-center">
                              <svg className="w-6 h-6 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                              </svg>
                            </div>
                            <div>
                              <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-1">Plan Type</p>
                              <span className="inline-block px-5 py-2 rounded-lg text-base font-bold uppercase bg-gradient-to-r from-[#F59E0B] to-[#D97706] text-white shadow-lg shadow-[#F59E0B]/30">
                                {orgDetails.subscription?.tier || 'Free'}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="bg-gradient-to-br from-[#10B981]/10 to-[#059669]/10 rounded-xl p-6 border border-[#10B981]/20">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-12 h-12 rounded-lg bg-[#10B981]/20 flex items-center justify-center">
                              <svg className="w-6 h-6 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            </div>
                            <div>
                              <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider mb-1">Status</p>
                              <span className={`inline-block px-5 py-2 rounded-lg text-base font-bold uppercase ${
                                orgDetails.subscription?.status === 'active' 
                                  ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30' 
                                  : 'bg-[#64748B]/20 text-[#64748B] border border-[#64748B]/30'
                              }`}>
                                {orgDetails.subscription?.status || 'Inactive'}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Subscription Details Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {/* Subscription Fee */}
                        <div className="bg-[#0F172A]/50 rounded-lg p-6 border border-[#334155]/30">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                              <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            </div>
                            <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Subscription Fee</p>
                          </div>
                          <p className="text-[#F8FAFC] font-bold text-2xl">
                            {orgDetails.subscription?.subscription_fee 
                              ? `${orgDetails.subscription.subscription_fee.toLocaleString()} ETB`
                              : '0 ETB'}
                          </p>
                          <p className="text-[#64748B] text-sm mt-2">Quarterly payment</p>
                        </div>

                        {/* Billing Cycle */}
                        <div className="bg-[#0F172A]/50 rounded-lg p-6 border border-[#334155]/30">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-[#8B5CF6]/10 flex items-center justify-center">
                              <svg className="w-5 h-5 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                            </div>
                            <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Billing Cycle</p>
                          </div>
                          <p className="text-[#F8FAFC] font-bold text-xl">
                            Every {orgDetails.subscription?.billing_cycle_months || 4} months
                          </p>
                          <p className="text-[#64748B] text-sm mt-2">3 times per year</p>
                        </div>

                        {/* Start Date */}
                        <div className="bg-[#0F172A]/50 rounded-lg p-6 border border-[#334155]/30">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-[#10B981]/10 flex items-center justify-center">
                              <svg className="w-5 h-5 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                            <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Start Date</p>
                          </div>
                          <p className="text-[#F8FAFC] font-bold text-xl">
                            {orgDetails.subscription?.start_date 
                              ? new Date(orgDetails.subscription.start_date).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })
                              : 'N/A'}
                          </p>
                          <p className="text-[#64748B] text-sm mt-2">Subscription began</p>
                        </div>

                        {/* Current Period Start */}
                        <div className="bg-[#0F172A]/50 rounded-lg p-6 border border-[#334155]/30">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-[#06B6D4]/10 flex items-center justify-center">
                              <svg className="w-5 h-5 text-[#06B6D4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                            <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Current Period</p>
                          </div>
                          <p className="text-[#F8FAFC] font-bold text-xl">
                            {orgDetails.subscription?.current_period_start 
                              ? new Date(orgDetails.subscription.current_period_start).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })
                              : 'N/A'}
                          </p>
                          <p className="text-[#64748B] text-sm mt-2">Period started</p>
                        </div>

                        {/* Current Period End */}
                        <div className="bg-[#0F172A]/50 rounded-lg p-6 border border-[#334155]/30">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-[#EC4899]/10 flex items-center justify-center">
                              <svg className="w-5 h-5 text-[#EC4899]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                            <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Period Ends</p>
                          </div>
                          <p className="text-[#F8FAFC] font-bold text-xl">
                            {orgDetails.subscription?.current_period_end 
                              ? new Date(orgDetails.subscription.current_period_end).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })
                              : 'N/A'}
                          </p>
                          <p className="text-[#64748B] text-sm mt-2">Period ends</p>
                        </div>

                        {/* Next Billing Date */}
                        <div className="bg-gradient-to-br from-[#F59E0B]/10 to-[#D97706]/10 rounded-lg p-6 border border-[#F59E0B]/30">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-[#F59E0B]/20 flex items-center justify-center">
                              <svg className="w-5 h-5 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            </div>
                            <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Next Billing</p>
                          </div>
                          <p className="text-[#F8FAFC] font-bold text-xl">
                            {orgDetails.subscription?.next_billing_date 
                              ? new Date(orgDetails.subscription.next_billing_date).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })
                              : 'N/A'}
                          </p>
                          <p className="text-[#F59E0B] text-sm mt-2 font-semibold">Payment due date</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payment History Tab */}
                {activeTab === 'payments' && (
                  <div className="space-y-6">
                    <div className="bg-[#1E293B]/50 rounded-xl p-8 border border-[#334155]/50 backdrop-blur-sm">
                      <h3 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                          <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                          </svg>
                        </div>
                        Payment History
                      </h3>
                      {paymentHistory?.payments && paymentHistory.payments.length > 0 ? (
                        <div className="space-y-4">
                          {paymentHistory.payments.map((payment: any) => (
                            <div key={payment.payment_id} className="bg-[#0F172A]/50 rounded-xl p-6 border border-[#334155]/30 hover:border-[#3B82F6]/30 transition-all">
                              <div className="flex items-start justify-between mb-6">
                                <div className="flex items-center gap-4">
                                  <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${
                                    payment.status === 'paid' ? 'bg-[#10B981]/10' : 
                                    payment.status === 'pending' ? 'bg-[#F59E0B]/10' : 'bg-[#EF4444]/10'
                                  }`}>
                                    <svg className={`w-7 h-7 ${
                                      payment.status === 'paid' ? 'text-[#10B981]' : 
                                      payment.status === 'pending' ? 'text-[#F59E0B]' : 'text-[#EF4444]'
                                    }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                  </div>
                                  <div>
                                    <p className="text-[#F8FAFC] font-bold text-lg mb-1">
                                      Invoice #{payment.invoice_number}
                                    </p>
                                    <p className="text-[#64748B] text-sm">
                                      Created: {new Date(payment.created_at).toLocaleDateString('en-US', { 
                                        year: 'numeric', 
                                        month: 'short', 
                                        day: 'numeric' 
                                      })}
                                    </p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <p className="text-[#F8FAFC] font-bold text-2xl mb-2">
                                    {payment.amount.toLocaleString()} {payment.currency}
                                  </p>
                                  <span className={`inline-block px-4 py-2 rounded-lg text-sm font-bold uppercase ${
                                    payment.status === 'paid' ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30' : 
                                    payment.status === 'pending' ? 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30' : 
                                    'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30'
                                  }`}>
                                    {payment.status}
                                  </span>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-[#334155]/30">
                                <div className="bg-[#1E293B]/30 rounded-lg p-4">
                                  <div className="flex items-center gap-2 mb-2">
                                    <svg className="w-4 h-4 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <p className="text-[#64748B] text-xs font-semibold uppercase tracking-wider">Due Date</p>
                                  </div>
                                  <p className="text-[#F8FAFC] font-bold text-base">
                                    {new Date(payment.due_date).toLocaleDateString('en-US', { 
                                      year: 'numeric', 
                                      month: 'short', 
                                      day: 'numeric' 
                                    })}
                                  </p>
                                </div>
                                
                                {payment.paid_at && (
                                  <div className="bg-[#1E293B]/30 rounded-lg p-4">
                                    <div className="flex items-center gap-2 mb-2">
                                      <svg className="w-4 h-4 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                      </svg>
                                      <p className="text-[#64748B] text-xs font-semibold uppercase tracking-wider">Paid Date</p>
                                    </div>
                                    <p className="text-[#10B981] font-bold text-base">
                                      {new Date(payment.paid_at).toLocaleDateString('en-US', { 
                                        year: 'numeric', 
                                        month: 'short', 
                                        day: 'numeric' 
                                      })}
                                    </p>
                                  </div>
                                )}

                                {payment.payment_method && (
                                  <div className="bg-[#1E293B]/30 rounded-lg p-4">
                                    <div className="flex items-center gap-2 mb-2">
                                      <svg className="w-4 h-4 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                                      </svg>
                                      <p className="text-[#64748B] text-xs font-semibold uppercase tracking-wider">Payment Method</p>
                                    </div>
                                    <p className="text-[#F8FAFC] font-bold text-base capitalize">
                                      {payment.payment_method}
                                    </p>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12">
                          <div className="bg-[#3B82F6]/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-10 h-10 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </div>
                          <p className="text-[#94A3B8] text-lg font-medium">No payment history available</p>
                          <p className="text-[#64748B] text-sm mt-2">Payment records will appear here once transactions are made</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Programs Tab */}
                {activeTab === 'programs' && (
                  <div className="space-y-4">
                    {/* Filters and Search Bar */}
                    <div className="bg-[#1E293B]/50 rounded-xl p-5 border border-[#334155]/50">
                      <div className="flex flex-col md:flex-row gap-4">
                        {/* Search */}
                        <div className="flex-1">
                          <div className="relative">
                            <svg className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <input
                              type="text"
                              placeholder="Search programs by name..."
                              value={programSearch}
                              onChange={(e) => setProgramSearch(e.target.value)}
                              className="w-full pl-12 pr-4 py-3 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6] transition-colors"
                            />
                          </div>
                        </div>

                        {/* Status Filter */}
                        <div className="w-full md:w-48">
                          <select
                            value={programStatusFilter}
                            onChange={(e) => setProgramStatusFilter(e.target.value)}
                            className="w-full px-4 py-3 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] transition-colors"
                          >
                            <option value="all">All Status</option>
                            <option value="public">Public</option>
                            <option value="draft">Draft</option>
                            <option value="paused">Paused</option>
                            <option value="archived">Archived</option>
                          </select>
                        </div>

                        {/* Sort By */}
                        <div className="w-full md:w-48">
                          <select
                            value={programSortBy}
                            onChange={(e) => setProgramSortBy(e.target.value as any)}
                            className="w-full px-4 py-3 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] transition-colors"
                          >
                            <option value="name">Sort by Name</option>
                            <option value="reports">Sort by Reports</option>
                            <option value="bounties">Sort by Bounties</option>
                            <option value="researchers">Sort by Researchers</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    {/* Programs Table Card */}
                    <div className="bg-[#1E293B]/50 rounded-xl border border-[#334155]/50 overflow-hidden">
                      <div className="p-6 border-b border-[#334155]/50">
                        <h3 className="text-2xl font-bold text-[#F8FAFC] flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-[#8B5CF6]/10 flex items-center justify-center">
                            <svg className="w-5 h-5 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                          </div>
                          Bug Bounty Programs
                          {(() => {
                            const filtered = orgPrograms?.filter((program: any) => {
                              const matchesSearch = program.name.toLowerCase().includes(programSearch.toLowerCase());
                              const matchesStatus = programStatusFilter === 'all' || program.status === programStatusFilter;
                              return matchesSearch && matchesStatus;
                            }) || [];
                            return filtered.length > 0 && (
                              <span className="text-[#64748B] text-base font-normal">
                                ({filtered.length})
                              </span>
                            );
                          })()}
                        </h3>
                      </div>

                      {(() => {
                        // Filter programs
                        let filteredPrograms = orgPrograms?.filter((program: any) => {
                          const matchesSearch = program.name.toLowerCase().includes(programSearch.toLowerCase());
                          const matchesStatus = programStatusFilter === 'all' || program.status === programStatusFilter;
                          return matchesSearch && matchesStatus;
                        }) || [];

                        // Sort programs
                        filteredPrograms = [...filteredPrograms].sort((a: any, b: any) => {
                          switch (programSortBy) {
                            case 'name':
                              return a.name.localeCompare(b.name);
                            case 'reports':
                              return (b.total_reports || 0) - (a.total_reports || 0);
                            case 'bounties':
                              return (b.total_bounties_paid || 0) - (a.total_bounties_paid || 0);
                            case 'researchers':
                              return (b.total_researchers || 0) - (a.total_researchers || 0);
                            default:
                              return 0;
                          }
                        });

                        return filteredPrograms.length > 0 ? (
                          <div className="overflow-x-auto">
                            <table className="w-full">
                              <thead className="bg-[#0F172A]/50">
                                <tr>
                                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Program Name</th>
                                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Status</th>
                                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Bounty Range</th>
                                  <th className="px-6 py-4 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Reports</th>
                                  <th className="px-6 py-4 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Researchers</th>
                                  <th className="px-6 py-4 text-right text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Bounties Paid</th>
                                  <th className="px-6 py-4 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Pending</th>
                                  <th className="px-6 py-4 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Actions</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-[#334155]/30">
                                {filteredPrograms.map((program: any) => (
                                  <tr 
                                    key={program.id} 
                                    onClick={() => router.push(`/finance/programs/${program.id}`)}
                                    className="hover:bg-[#1E293B]/50 transition-colors cursor-pointer group"
                                  >
                                    <td className="px-6 py-4">
                                      <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] flex items-center justify-center flex-shrink-0">
                                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                          </svg>
                                        </div>
                                        <div>
                                          <p className="text-[#F8FAFC] font-semibold text-base group-hover:text-[#3B82F6] transition-colors">
                                            {program.name}
                                          </p>
                                          <p className="text-[#64748B] text-sm capitalize">
                                            {program.type || 'Bug Bounty'}
                                          </p>
                                        </div>
                                      </div>
                                    </td>
                                    <td className="px-6 py-4">
                                      <span className={`inline-block px-3 py-1 rounded-lg text-xs font-bold uppercase ${
                                        program.status === 'public' 
                                          ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30' 
                                          : program.status === 'draft'
                                          ? 'bg-[#64748B]/20 text-[#64748B] border border-[#64748B]/30'
                                          : program.status === 'paused'
                                          ? 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30'
                                          : 'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30'
                                      }`}>
                                        {program.status}
                                      </span>
                                    </td>
                                    <td className="px-6 py-4">
                                      <div>
                                        <p className="text-[#10B981] font-bold text-base">
                                          {program.min_bounty?.toLocaleString() || 0} - {program.max_bounty?.toLocaleString() || 0}
                                        </p>
                                        <p className="text-[#64748B] text-xs">ETB</p>
                                      </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                      <div>
                                        <p className="text-[#F8FAFC] font-bold text-lg">{program.total_reports || 0}</p>
                                        <p className="text-[#10B981] text-xs">{program.valid_reports || 0} valid</p>
                                      </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                      <div>
                                        <p className="text-[#F8FAFC] font-bold text-lg">{program.total_researchers || 0}</p>
                                        <p className="text-[#8B5CF6] text-xs">{program.researchers_with_reports || 0} active</p>
                                      </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                      <div>
                                        <p className="text-[#F8FAFC] font-bold text-base">{(program.total_bounties_paid || 0).toLocaleString()}</p>
                                        <p className="text-[#64748B] text-xs">ETB</p>
                                      </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                      <span className={`inline-block px-3 py-1 rounded-lg text-sm font-bold ${
                                        (program.pending_payments || 0) > 0 
                                          ? 'bg-[#F59E0B]/20 text-[#F59E0B]' 
                                          : 'bg-[#64748B]/20 text-[#64748B]'
                                      }`}>
                                        {program.pending_payments || 0}
                                      </span>
                                    </td>
                                    <td className="px-6 py-4">
                                      <div className="flex items-center justify-center gap-2">
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            router.push(`/finance/programs/${program.id}`);
                                          }}
                                          className="p-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors"
                                          title="View Details"
                                        >
                                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                          </svg>
                                        </button>
                                      </div>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <div className="text-center py-16">
                            <div className="bg-[#8B5CF6]/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                              <svg className="w-10 h-10 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                              </svg>
                            </div>
                            <p className="text-[#94A3B8] text-lg font-medium">
                              {programSearch || programStatusFilter !== 'all' 
                                ? 'No programs match your filters' 
                                : 'No programs found'}
                            </p>
                            <p className="text-[#64748B] text-sm mt-2">
                              {programSearch || programStatusFilter !== 'all'
                                ? 'Try adjusting your search or filter criteria'
                                : 'This organization hasn\'t created any bug bounty programs yet'}
                            </p>
                          </div>
                        );
                      })()}
                    </div>
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
