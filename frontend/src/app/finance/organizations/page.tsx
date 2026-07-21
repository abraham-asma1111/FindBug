'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceOrganizationsPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data, isLoading } = useApiQuery<any>({
    endpoint: '/financial/organizations?limit=1000',
  });

  const organizations = data?.organizations || [];

  const filteredOrgs = organizations.filter((org: any) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        org.company_name?.toLowerCase().includes(query) ||
        org.name?.toLowerCase().includes(query) ||
        org.id?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const handleOrgClick = (org: any) => {
    router.push(`/finance/organizations/${org.id}`);
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Organizations"
          subtitle={`${filteredOrgs.length} organizations`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search organizations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading organizations...</p>
            </div>
          ) : filteredOrgs.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">No organizations found</p>
            </div>
          ) : (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[#334155]">
                      <th className="text-left py-4 px-6 text-sm font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Organization
                      </th>
                      <th className="text-left py-4 px-6 text-sm font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Industry
                      </th>
                      <th className="text-left py-4 px-6 text-sm font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Subscription
                      </th>
                      <th className="text-left py-4 px-6 text-sm font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="text-left py-4 px-6 text-sm font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Status
                      </th>
                      <th className="text-left py-4 px-6 text-sm font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredOrgs.map((org: any) => (
                      <tr 
                        key={org.id}
                        className="border-b border-[#334155] hover:bg-[#0F172A] transition-colors cursor-pointer"
                        onClick={() => handleOrgClick(org)}
                      >
                        <td className="py-4 px-6">
                          <div>
                            <p className="font-semibold text-[#F8FAFC]">
                              {org.company_name || org.name}
                            </p>
                            <p className="text-sm text-[#64748B] mt-1">
                              {org.email || 'No email'}
                            </p>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <p className="text-[#94A3B8]">
                            {org.industry || 'Not specified'}
                          </p>
                        </td>
                        <td className="py-4 px-6">
                          <span className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase bg-gradient-to-r from-[#F59E0B] to-[#D97706] text-white shadow-lg shadow-[#F59E0B]/20">
                            {org.subscription_type || 'Free'}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <p className="font-bold text-[#10B981]">
                            {org.subscription_amount ? `${org.subscription_amount.toLocaleString()} ETB` : '0 ETB'}
                          </p>
                          <p className="text-xs text-[#64748B] mt-1">per 4 months</p>
                        </td>
                        <td className="py-4 px-6">
                          <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase ${
                            org.subscription_status === 'active' ? 'bg-[#10B981]' : 'bg-[#94A3B8]'
                          } text-white`}>
                            {org.subscription_status || 'Inactive'}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOrgClick(org);
                            }}
                            className="text-[#3B82F6] hover:text-[#60A5FA] font-medium text-sm"
                          >
                            View Details →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
