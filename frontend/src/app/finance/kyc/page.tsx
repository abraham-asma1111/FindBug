'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceKYCPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const router = useRouter();
  const statusFilter = searchParams.get('status') || 'pending';
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch KYC verifications by status
  const { data: kycData, isLoading } = useApiQuery<any>({
    endpoint: `/kyc/verifications?status=${statusFilter}&limit=1000`,
    queryKey: [`/kyc/verifications`, statusFilter],
  });

  const kycVerifications = kycData?.verifications || [];

  // Filter by search
  const filteredItems = kycVerifications.filter((kyc: any) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        kyc.user?.email?.toLowerCase().includes(query) ||
        kyc.user?.full_name?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const getKYCStatusBadge = (kyc: any) => {
    const isFullyVerified = kyc.email_verified && kyc.persona_verified;
    if (isFullyVerified) {
      return <span className="px-2 py-1 rounded text-xs font-bold bg-[#10B981] text-white">✓ VERIFIED</span>;
    } else if (kyc.email_verified || kyc.persona_verified) {
      return <span className="px-2 py-1 rounded text-xs font-bold bg-[#F59E0B] text-white">PARTIAL</span>;
    } else {
      return <span className="px-2 py-1 rounded text-xs font-bold bg-[#64748B] text-white">NOT VERIFIED</span>;
    }
  };  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="KYC Verification"
          subtitle={`${filteredItems.length} KYC verifications for review`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Status Filter Tabs */}
          <div className="mb-6 flex gap-2">
            <Link href="/finance/kyc?status=pending">
              <Button variant={statusFilter === 'pending' ? 'warning' : 'secondary'} size="sm">
                Pending Review
              </Button>
            </Link>
            <Link href="/finance/kyc?status=approved">
              <Button variant={statusFilter === 'approved' ? 'success' : 'secondary'} size="sm">
                Approved
              </Button>
            </Link>
            <Link href="/finance/kyc?status=rejected">
              <Button variant={statusFilter === 'rejected' ? 'danger' : 'secondary'} size="sm">
                Rejected
              </Button>
            </Link>
          </div>

          {/* Search */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by researcher name or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {/* Items Table */}
          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="flex items-center justify-center">
                <svg className="animate-spin h-8 w-8 text-[#3B82F6]" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
              <p className="text-[#94A3B8] mt-4">Loading...</p>
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">No KYC verifications found</p>
            </div>
          ) : (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#334155]">
                    <th className="text-left pb-3 pr-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                      Researcher
                    </th>
                    <th className="text-left pb-3 pr-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                      Email
                    </th>
                    <th className="text-left pb-3 pr-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                      KYC Status
                    </th>
                    <th className="text-left pb-3 pr-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                      Email Verified
                    </th>
                    <th className="text-left pb-3 pr-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                      Persona Verified
                    </th>
                    <th className="text-left pb-3 pr-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                      Submitted
                    </th>
                    <th className="text-left pb-3 pr-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredItems.map((item: any) => (
                    <tr
                      key={item.id}
                      className="border-b border-[#334155] last:border-b-0 hover:bg-[#0F172A] transition cursor-pointer"
                      onClick={() => router.push(`/finance/kyc/${item.id}`)}
                    >
                      <td className="py-3 pr-4">
                        <span className="text-[#F8FAFC] font-medium">
                          {item.user?.full_name || 'Unknown'}
                        </span>
                      </td>
                      <td className="py-3 pr-4">
                        <span className="text-[#94A3B8]">{item.user?.email}</span>
                      </td>
                      <td className="py-3 pr-4">{getKYCStatusBadge(item)}</td>
                      <td className="py-3 pr-4">
                        <span className={`font-semibold ${item.email_verified ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                          {item.email_verified ? '✓' : '✗'}
                        </span>
                      </td>
                      <td className="py-3 pr-4">
                        <span className={`font-semibold ${item.persona_verified ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                          {item.persona_verified ? '✓' : '✗'}
                        </span>
                      </td>
                      <td className="py-3 pr-4">
                        <span className="text-[#94A3B8]">
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                      </td>
                      <td className="py-3 pr-4">
                        <Button
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/finance/kyc/${item.id}`);
                          }}
                          variant="secondary"
                          size="sm"
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
