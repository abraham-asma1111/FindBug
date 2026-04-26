'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { useState } from 'react';
import Modal from '@/components/ui/Modal';

export default function AdminPlatformPage() {
  const user = useAuthStore((state) => state.user);
  const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: platformStats } = useApiQuery<any>({
    endpoint: '/admin/platform/status',
  });

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Platform"
          subtitle="Platform settings and configuration"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero Section */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Platform Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Platform Settings
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Configure platform settings, maintenance, and system status.
              </p>
            </div>
          </section>

          {/* Platform Status */}
          <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#94A3B8]">System Status</p>
              <p className="mt-2 text-lg font-semibold text-[#10B981]">
                {platformStats?.status === 'operational' ? '✓ Operational' : '⚠ Maintenance'}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#94A3B8]">Uptime</p>
              <p className="mt-2 text-lg font-semibold text-[#F8FAFC]">
                {platformStats?.uptime || '99.9'}%
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#94A3B8]">Active Users</p>
              <p className="mt-2 text-lg font-semibold text-[#3B82F6]">
                {platformStats?.active_users?.toLocaleString() || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#94A3B8]">API Requests</p>
              <p className="mt-2 text-lg font-semibold text-[#F59E0B]">
                {platformStats?.api_requests?.toLocaleString() || 0}
              </p>
            </div>
          </div>

          {/* Configuration Sections */}
          <div className="mt-6 space-y-6">
            {/* Maintenance Mode */}
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-[#F8FAFC]">Maintenance Mode</h2>
                  <p className="mt-1 text-sm text-[#94A3B8]">
                    Enable maintenance mode to temporarily disable platform access.
                  </p>
                </div>
                <Button
                  onClick={() => setShowMaintenanceModal(true)}
                  variant="outline"
                  className="border-[#EF2330] text-[#EF2330] hover:bg-[#EF2330] hover:text-white"
                >
                  Configure
                </Button>
              </div>
            </div>

            {/* Feature Flags */}
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-[#F8FAFC]">Feature Flags</h2>
                  <p className="mt-1 text-sm text-[#94A3B8]">
                    Enable or disable platform features for testing and rollout.
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Manage
                </Button>
              </div>
            </div>

            {/* Email Configuration */}
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-[#F8FAFC]">Email Configuration</h2>
                  <p className="mt-1 text-sm text-[#94A3B8]">
                    Configure email templates and notification settings.
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>
            </div>

            {/* Payment Gateway */}
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-[#F8FAFC]">Payment Gateway</h2>
                  <p className="mt-1 text-sm text-[#94A3B8]">
                    Configure payment processing and gateway settings.
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>
            </div>

            {/* Security Settings */}
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-[#F8FAFC]">Security Settings</h2>
                  <p className="mt-1 text-sm text-[#94A3B8]">
                    Configure security policies and compliance settings.
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>
            </div>
          </div>

          {/* Maintenance Modal */}
          <Modal
            isOpen={showMaintenanceModal}
            onClose={() => setShowMaintenanceModal(false)}
            title="Maintenance Mode"
          >
            <div className="space-y-4">
              <p className="text-[#94A3B8]">
                Enable maintenance mode to temporarily disable platform access for all users except administrators.
              </p>
              <div className="space-y-2">
                <label className="block text-sm text-[#F8FAFC]">
                  <input type="checkbox" className="mr-2" />
                  Enable Maintenance Mode
                </label>
                <textarea
                  placeholder="Maintenance message (optional)..."
                  className="w-full bg-[#0F172A] border border-[#334155] rounded px-3 py-2 text-[#F8FAFC] placeholder-[#64748B]"
                  rows={3}
                />
              </div>
              <div className="flex gap-3 justify-end">
                <Button
                  onClick={() => setShowMaintenanceModal(false)}
                  variant="outline"
                >
                  Cancel
                </Button>
                <Button
                  className="bg-[#EF2330] hover:bg-[#DC2026] text-white"
                >
                  Save
                </Button>
              </div>
            </div>
          </Modal>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
