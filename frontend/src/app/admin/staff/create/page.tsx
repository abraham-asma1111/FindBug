'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import PortalShell from '@/components/portal/PortalShell';
import StaffProvisionForm from '@/components/admin/StaffProvisionForm';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

export default function AdminStaffCreatePage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Staff Provisioning"
          subtitle="Provision triage, finance, operations, and admin accounts using the backend contract that already exists."
          navItems={getPortalNavItems(user.role)}
        >
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
            <SectionCard
              title="Create internal account"
              description="This page replaces the old `/admin/provision-user` prototype with the live `/admin/staff/create` flow."
            >
              <StaffProvisionForm />
            </SectionCard>

            <SectionCard
              title="Implementation notes"
              description="Current admin provisioning constraints from the backend."
            >
              <div className="space-y-4 text-sm leading-6 text-[#6d6760]">
                <p>Accepted role values: `triage_specialist`, `finance_officer`, `staff`, and `admin`.</p>
                <p>The backend expects query parameters named `email`, `full_name`, `department`, and `role`.</p>
                <p>Temporary passwords are generated server-side, so the frontend should not ask admins to invent one.</p>
              </div>
            </SectionCard>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
