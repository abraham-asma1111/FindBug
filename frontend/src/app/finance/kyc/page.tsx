'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function FinanceKYCPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') || 'all';

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = statusFilter === 'all' 
    ? '/kyc/verifications' 
    : `/kyc/verifications?status=${statusFilter}`;

  const { data, isLoading } = useApiQuery<any>({
    endpoint,
  });

  const verifications = data?.verifications || [];

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      pending: { bg: 'bg-[#F59E0B]', label: 'PENDING' },
      approved: { bg: 'bg-[#10B981]', label: 'APPROVED' },
      rejected: { bg: 'bg-[#EF4444]', label: 'REJECTED' },
      under_review: { bg: 'bg-[#3B82F6]', label: 'UNDER REVIEW' },
    };
    const config = statusMap[status] || { bg: 'bg-[#94A3B8]', label: status.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="KYC Management"
          subtitle="Manage KYC verification requests"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Finance Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero Section */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                KYC Verification
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Identity Verification
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Review and approve KYC documents for researcher identity verification.
              </p>
            </div>
          </section>

          {/* Filter Tabs */}
          <div className="mt-6 flex gap-2 flex-wrap">
            <Link href="/finance/kyc">
              <Button 
                variant={statusFilter === 'all' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'all' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                All
              </Button>
            </Link>
            <Link href="/finance/kyc?status=pending">
              <Button 
                variant={statusFilter === 'pending' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'pending' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Pending Review
              </Button>
            </Link>
            <Link href="/finance/kyc?status=approved">
              <Button 
                variant={statusFilter === 'approved' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'approved' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Approved
              </Button>
            </Link>
            <Link href="/finance/kyc?status=rejected">
              <Button 
                variant={statusFilter === 'rejected' ? 'primary' : 'outline'} 
                size="sm"
                className={statusFilter === 'rejected' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Rejected
              </Button>
            </Link>
          </div>

          {/* KYC List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading KYC verifications...</p>
              </div>
            ) : verifications.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No KYC verifications found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {verifications.map((verification: any) => (
                  <Link key={verification.id} href={`/finance/kyc/${verification.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {verification.researcher_name || 'Researcher'}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {verification.document_type || 'ID Document'} • {new Date(verification.submitted_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {getStatusBadge(verification.status)}
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
