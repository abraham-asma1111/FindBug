'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceOrganizationsPage() {
  const user = useAuthStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data, isLoading } = useApiQuery<any>({
    endpoint: '/organizations?limit=1000',
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
          ) : (
            <div className="space-y-3">
              {filteredOrgs.map((org: any) => (
                <div key={org.id} className="bg-[#1E293B] rounded-lg border border-[#334155] p-5 hover:border-[#3B82F6] transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-[#F8FAFC] text-lg mb-1">
                        {org.company_name || org.name}
                      </h3>
                      <p className="text-sm text-[#94A3B8]">
                        {org.industry || 'Technology'} • {org.subscription_type || 'Free'} Plan
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-[#10B981]">
                        ${org.subscription_amount || 0}/month
                      </p>
                      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                        org.subscription_status === 'active' ? 'bg-[#10B981]' : 'bg-[#94A3B8]'
                      } text-white`}>
                        {org.subscription_status || 'Active'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
