'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

export default function AdminUserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const userId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const [actionPending, setActionPending] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: userDetails, isLoading, refetch } = useApiQuery<any>({
    endpoint: `/admin/users/${userId}`,
  });

  const handleStatusToggle = async () => {
    setActionPending(true);
    setMessage(null);
    try {
      const isActive = userDetails?.is_active;
      await api.post(`/admin/users/${userId}/status?is_active=${!isActive}`);
      setMessage({ 
        type: 'success', 
        text: `User ${!isActive ? 'activated' : 'deactivated'} successfully.` 
      });
      refetch?.();
    } catch {
      setMessage({ type: 'error', text: 'Action failed. Please try again.' });
    } finally {
      setActionPending(false);
    }
  };

  const handleDeleteUser = async () => {
    if (!confirm(`Are you sure you want to delete user "${userDetails?.email}"? This action cannot be undone.`)) {
      return;
    }
    
    setActionPending(true);
    setMessage(null);
    try {
      await api.post(`/admin/users/${userId}/delete`);
      setMessage({ type: 'success', text: 'User deleted successfully. Redirecting...' });
      setTimeout(() => router.push('/admin/users'), 2000);
    } catch {
      setMessage({ type: 'error', text: 'Delete failed. Please try again.' });
      setActionPending(false);
    }
  };

  const getRoleBadge = (role: string) => {
    const roleMap: Record<string, { bg: string; label: string }> = {
      researcher:       { bg: 'bg-[#3B71CA]', label: 'RESEARCHER' },
      organization:     { bg: 'bg-[#10B981]', label: 'ORGANIZATION' },
      triage_specialist:{ bg: 'bg-[#F59E0B]', label: 'TRIAGE' },
      finance_officer:  { bg: 'bg-[#EF2330]', label: 'FINANCE' },
      admin:            { bg: 'bg-[#8B5CF6]', label: 'ADMIN' },
      super_admin:      { bg: 'bg-[#EC4899]', label: 'SUPER ADMIN' },
    };
    const config = roleMap[role] || { bg: 'bg-[#64748B]', label: role?.toUpperCase() || 'UNKNOWN' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const InfoRow = ({ label, value }: { label: string; value: string | number | React.ReactNode }) => (
    <div className="flex justify-between py-2 border-b border-[#334155] last:border-0">
      <span className="text-sm text-[#94A3B8]">{label}</span>
      <span className="text-sm text-[#F8FAFC] font-medium">{value}</span>
    </div>
  );

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['admin']}>
        {user ? (
          <PortalShell
            user={user}
            title="User Details"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            headerAlign="center"
            eyebrowText="Admin Console"
            eyebrowClassName="text-xl tracking-[0.18em]"
            hideTitle
            hideSubtitle
            hideThemeToggle={true}
          >
            <div className="flex items-center justify-center py-12">
              <p className="text-[#94A3B8]">Loading user details…</p>
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  if (!userDetails) {
    return (
      <ProtectedRoute allowedRoles={['admin']}>
        {user ? (
          <PortalShell
            user={user}
            title="User Not Found"
            subtitle="The requested user could not be found"
            navItems={getPortalNavItems(user.role)}
            headerAlign="center"
            eyebrowText="Admin Console"
            eyebrowClassName="text-xl tracking-[0.18em]"
            hideTitle
            hideSubtitle
            hideThemeToggle={true}
          >
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-[#94A3B8] mb-4">User not found</p>
              <Link href="/admin/users">
                <Button variant="outline">← Back to Users</Button>
              </Link>
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="User Details"
          subtitle={userDetails.email}
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Header with Back Button and Actions */}
          <div className="flex items-center justify-between mb-6">
            <Link href="/admin/users">
              <Button variant="outline" size="sm">← Back</Button>
            </Link>
            <div className="flex gap-2">
              <Button
                variant={userDetails.is_active ? 'outline' : 'primary'}
                size="sm"
                disabled={actionPending}
                onClick={handleStatusToggle}
                className={
                  userDetails.is_active
                    ? 'border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white'
                    : 'bg-[#10B981] hover:bg-[#059669]'
                }
              >
                {userDetails.is_active ? 'Deactivate' : 'Activate'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={actionPending}
                onClick={handleDeleteUser}
                className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white"
              >
                Delete
              </Button>
            </div>
          </div>

          {/* Status message */}
          {message && (
            <div className={`mb-4 rounded-md px-4 py-3 text-sm font-medium ${
              message.type === 'success' ? 'bg-[#10B981]/20 text-[#10B981]' : 'bg-[#EF4444]/20 text-[#EF4444]'
            }`}>
              {message.text}
            </div>
          )}

          {/* Streamlined User Card */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
            {/* Header Section */}
            <div className="bg-[#0F172A] px-6 py-4 border-b border-[#334155]">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-[#3B71CA] flex items-center justify-center text-white font-bold text-lg">
                  {(userDetails.email || 'U')[0].toUpperCase()}
                </div>
                <div className="flex-1">
                  <h1 className="text-xl font-semibold text-[#F8FAFC]">{userDetails.email}</h1>
                  <div className="flex items-center gap-2 mt-1">
                    {getRoleBadge(userDetails.role)}
                    <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                      userDetails.is_active ? 'bg-[#10B981]' : 'bg-[#64748B]'
                    } text-white`}>
                      {userDetails.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Information Section */}
            <div className="p-6 space-y-6">
              {/* Account Information */}
              <div>
                <h3 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-3">Account Information</h3>
                <div className="space-y-0">
                  <InfoRow label="User ID" value={<span className="font-mono text-xs">{userDetails.id}</span>} />
                  <InfoRow label="Email" value={userDetails.email} />
                  <InfoRow label="Role" value={getRoleBadge(userDetails.role)} />
                  <InfoRow 
                    label="Email Verified" 
                    value={userDetails.email_verified ? '✓ Yes' : '✗ No'} 
                  />
                  <InfoRow 
                    label="MFA Enabled" 
                    value={userDetails.mfa_enabled ? '✓ Yes' : '✗ No'} 
                  />
                  <InfoRow 
                    label="Created" 
                    value={userDetails.created_at ? new Date(userDetails.created_at).toLocaleDateString() : 'N/A'} 
                  />
                  <InfoRow 
                    label="Last Login" 
                    value={userDetails.last_login ? new Date(userDetails.last_login).toLocaleDateString() : 'Never'} 
                  />
                </div>
              </div>

              {/* Researcher Profile */}
              {userDetails.researcher && (
                <div>
                  <h3 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-3">Researcher Profile</h3>
                  <div className="space-y-0">
                    <InfoRow label="Reputation Score" value={userDetails.researcher.reputation_score || 0} />
                    <InfoRow label="Total Reports" value={userDetails.researcher.total_reports || 0} />
                    <InfoRow label="Valid Reports" value={userDetails.researcher.valid_reports || 0} />
                    <InfoRow 
                      label="Total Earnings" 
                      value={`${(userDetails.researcher.total_earnings || 0).toLocaleString()} ETB`} 
                    />
                    {userDetails.researcher.specializations && (
                      <InfoRow 
                        label="Specializations" 
                        value={
                          Array.isArray(userDetails.researcher.specializations) 
                            ? userDetails.researcher.specializations.join(', ') 
                            : userDetails.researcher.specializations || 'None'
                        } 
                      />
                    )}
                  </div>
                </div>
              )}

              {/* Organization Profile */}
              {userDetails.organization && (
                <div>
                  <h3 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-3">Organization Profile</h3>
                  <div className="space-y-0">
                    <InfoRow label="Company Name" value={userDetails.organization.company_name || 'N/A'} />
                    <InfoRow label="Website" value={userDetails.organization.website || 'N/A'} />
                    <InfoRow 
                      label="Verified" 
                      value={userDetails.organization.is_verified ? '✓ Yes' : '✗ No'} 
                    />
                    <InfoRow label="Total Programs" value={userDetails.organization.total_programs || 0} />
                  </div>
                </div>
              )}

              {/* Staff Profile */}
              {userDetails.staff && (
                <div>
                  <h3 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-3">Staff Profile</h3>
                  <div className="space-y-0">
                    <InfoRow label="Department" value={userDetails.staff.department || 'N/A'} />
                    <InfoRow label="Position" value={userDetails.staff.position || 'N/A'} />
                  </div>
                </div>
              )}
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
