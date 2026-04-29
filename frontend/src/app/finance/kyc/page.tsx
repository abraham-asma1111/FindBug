'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import TransactionTable from '@/components/finance/TransactionTable';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceKYCPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') || 'pending';
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data, isLoading } = useApiQuery<any>({
    endpoint: `/kyc/verifications?status=${statusFilter}&limit=1000`,
  });

  const verifications = data?.verifications || [];

  const filteredVerifications = verifications.filter((kyc: any) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        kyc.user_name?.toLowerCase().includes(query) ||
        kyc.id?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const columns = [
    {
      key: 'id',
      label: 'KYC ID',
      sortable: true,
      render: (value: any) => (
        <span className="font-semibold text-[#F8FAFC]">#{value.slice(0, 8)}</span>
      ),
    },
    {
      key: 'user_name',
      label: 'Researcher',
      sortable: true,
      render: (value: any) => <span className="text-[#F8FAFC]">{value || 'Unknown'}</span>,
    },
    {
      key: 'document_type',
      label: 'Document Type',
      sortable: true,
      render: (value: any) => (
        <span className="text-[#94A3B8] capitalize">{value?.replace('_', ' ') || '-'}</span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      render: (value: any) => {
        const colors: Record<string, string> = {
          pending: 'bg-[#F59E0B]',
          approved: 'bg-[#10B981]',
          rejected: 'bg-[#EF4444]',
        };
        return (
          <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${colors[value] || 'bg-[#94A3B8]'} text-white`}>
            {value}
          </span>
        );
      },
    },
    {
      key: 'submitted_at',
      label: 'Submitted',
      sortable: true,
      render: (value: any) => <span className="text-[#94A3B8]">{new Date(value).toLocaleDateString()}</span>,
    },
  ];

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="KYC Verification"
          subtitle={`${filteredVerifications.length} verifications`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
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

          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by researcher or KYC ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading KYC verifications...</p>
            </div>
          ) : (
            <TransactionTable
              data={filteredVerifications}
              columns={columns}
              selectable={false}
              linkPrefix="/finance/kyc"
            />
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
