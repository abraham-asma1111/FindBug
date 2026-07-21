'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';

export default function PayoutReportsPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Payout Reports"
          subtitle="Generate and export payout reports"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155] mb-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Generate Payout Report</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Date Range
                </label>
                <select className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]">
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                  <option value="90d">Last 90 Days</option>
                  <option value="1y">Last Year</option>
                </select>
              </div>

              <Button className="w-full">Generate Report</Button>
            </div>
          </div>

          <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Recent Reports</h2>
            <div className="text-center py-8 text-[#94A3B8]">
              <p>No recent payout reports</p>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
