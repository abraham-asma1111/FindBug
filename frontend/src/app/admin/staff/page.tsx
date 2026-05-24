'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

export default function AdminStaffPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const deptFilter = searchParams.get('department') || 'all';
  const [actionPending, setActionPending] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = deptFilter === 'all' ? '/admin/staff' : `/admin/staff?department=${deptFilter}`;
  const { data, isLoading, refetch } = useApiQuery<any>({ endpoint });
  const staff = data?.staff || [];

  const handleStatusToggle = async (userId: string, currentStatus: string) => {
    setActionPending(userId);
    setMessage(null);
    try {
      const isActive = currentStatus !== 'active';
      await api.post(`/admin/users/${userId}/status?is_active=${isActive}`);
      setMessage({ type: 'success', text: `Staff member ${isActive ? 'activated' : 'deactivated'}.` });
      refetch?.();
    } catch {
      setMessage({ type: 'error', text: 'Action failed. Please try again.' });
    } finally {
      setActionPending(null);
    }
  };

  const getRoleBadge = (role: string) => {
    const roleMap: Record<string, { bg: string; label: string }> = {
      triage_specialist: { bg: 'bg-[#F59E0B]', label: 'TRIAGE' },
      finance_officer:   { bg: 'bg-[#EF2330]', label: 'FINANCE' },
      admin:             { bg: 'bg-[#8B5CF6]', label: 'ADMIN' },
      super_admin:       { bg: 'bg-[#EC4899]', label: 'SUPER ADMIN' },
      staff:             { bg: 'bg-[#64748B]', label: 'STAFF' },
    };
    const config = roleMap[role] || { bg: 'bg-[#94A3B8]', label: role?.toUpperCase() || 'STAFF' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const DEPT_FILTERS = [
    { value: 'all', label: 'All' },
    { value: 'triage', label: 'Triage' },
    { value: 'finance', label: 'Finance' },
    { value: 'admin', label: 'Admin' },
    { value: 'engineering', label: 'Engineering' },
  ];

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Staff"
          subtitle="Manage platform staff"
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
                Staff Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Platform Staff
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Manage triage specialists, finance officers, and administrators.
              </p>
            </div>
          </section>

          {/* Filter + Provision row */}
          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-2 flex-wrap">
              {DEPT_FILTERS.map(({ value, label }) => (
                <Link
                  key={value}
                  href={value === 'all' ? '/admin/staff' : `/admin/staff?department=${value}`}
                >
                  <Button
                    variant={deptFilter === value ? 'primary' : 'outline'}
                    size="sm"
                    className={deptFilter === value ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
                  >
                    {label}
                  </Button>
                </Link>
              ))}
            </div>
            <Link href="/admin/staff/create">
              <Button className="bg-[#EF2330] hover:bg-[#DC2026] text-white" size="sm">
                + Provision Staff
              </Button>
            </Link>
          </div>

          {/* Status message */}
          {message && (
            <div className={`mt-4 rounded-md px-4 py-3 text-sm font-medium ${
              message.type === 'success' ? 'bg-[#10B981]/20 text-[#10B981]' : 'bg-[#EF4444]/20 text-[#EF4444]'
            }`}>
              {message.text}
            </div>
          )}

          {/* Staff List */}
          <div className="mt-4">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading staff…</p>
              </div>
            ) : staff.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-10 text-center">
                <p className="text-[#94A3B8] mb-4">No staff members found.</p>
                <Link href="/admin/staff/create">
                  <Button className="bg-[#EF2330] hover:bg-[#DC2026] text-white">
                    Provision First Staff Member
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {staff.map((member: any) => (
                  <div
                    key={member.id}
                    className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 transition-colors hover:border-[#475569]"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold text-[#F8FAFC] truncate">
                          {member.full_name || member.email || 'Unknown'}
                        </h3>
                        <p className="text-sm text-[#94A3B8] truncate">
                          {member.email || '—'}
                          {member.department ? ` · ${member.department}` : ''}
                          {member.position ? ` · ${member.position}` : ''}
                        </p>
                        <p className="text-xs text-[#64748B] mt-1">
                          Since {member.created_at ? new Date(member.created_at).toLocaleDateString() : '—'}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {getRoleBadge(member.role)}
                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                          member.status === 'active' ? 'bg-[#10B981]' : 'bg-[#64748B]'
                        } text-white`}>
                          {member.status || 'UNKNOWN'}
                        </span>
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={actionPending === member.user_id}
                          onClick={() => handleStatusToggle(member.user_id, member.status)}
                          className={
                            member.status === 'active'
                              ? 'border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white text-xs px-2 py-1'
                              : 'border-[#10B981] text-[#10B981] hover:bg-[#10B981] hover:text-white text-xs px-2 py-1'
                          }
                        >
                          {actionPending === member.user_id ? '…' : member.status === 'active' ? 'Deactivate' : 'Activate'}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <p className="mt-4 text-xs text-[#64748B]">
            Showing {staff.length} staff member{staff.length !== 1 ? 's' : ''}
          </p>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
