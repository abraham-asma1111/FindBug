'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import Link from 'next/link';

export default function AdminAuditLogsPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const actionFilter = searchParams.get('action') || 'all';

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = actionFilter === 'all' 
    ? '/admin/audit-logs' 
    : `/admin/audit-logs?action=${actionFilter}`;

  const { data, isLoading } = useApiQuery<any>({
    endpoint,
  });

  const logs = data?.logs || [];

  const getActionBadge = (action: string) => {
    const actionMap: Record<string, { bg: string; label: string }> = {
      create: { bg: 'bg-[#10B981]', label: 'CREATE' },
      update: { bg: 'bg-[#3B82F6]', label: 'UPDATE' },
      delete: { bg: 'bg-[#EF4444]', label: 'DELETE' },
      approve: { bg: 'bg-[#10B981]', label: 'APPROVE' },
      reject: { bg: 'bg-[#EF4444]', label: 'REJECT' },
      login: { bg: 'bg-[#F59E0B]', label: 'LOGIN' },
      logout: { bg: 'bg-[#94A3B8]', label: 'LOGOUT' },
    };
    const config = actionMap[action] || { bg: 'bg-[#94A3B8]', label: action.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Audit Logs"
          subtitle="Platform activity and security logs"
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
                Audit Logs
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Activity Logs
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                View all platform activity and security events.
              </p>
            </div>
          </section>

          {/* Filter Tabs */}
          <div className="mt-6 flex gap-2 flex-wrap">
            <Link href="/admin/audit-logs">
              <Button 
                variant={actionFilter === 'all' ? 'primary' : 'outline'} 
                size="sm"
                className={actionFilter === 'all' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                All
              </Button>
            </Link>
            <Link href="/admin/audit-logs?action=create">
              <Button 
                variant={actionFilter === 'create' ? 'primary' : 'outline'} 
                size="sm"
                className={actionFilter === 'create' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Create
              </Button>
            </Link>
            <Link href="/admin/audit-logs?action=update">
              <Button 
                variant={actionFilter === 'update' ? 'primary' : 'outline'} 
                size="sm"
                className={actionFilter === 'update' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Update
              </Button>
            </Link>
            <Link href="/admin/audit-logs?action=delete">
              <Button 
                variant={actionFilter === 'delete' ? 'primary' : 'outline'} 
                size="sm"
                className={actionFilter === 'delete' ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
              >
                Delete
              </Button>
            </Link>
          </div>

          {/* Audit Logs List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading audit logs...</p>
              </div>
            ) : logs.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No audit logs found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {logs.map((log: any) => (
                  <div key={log.id} className="bg-[#1E293B] rounded-lg border border-[#334155] p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-[#F8FAFC] mb-1">
                          {log.description || log.action}
                        </h3>
                        <p className="text-sm text-[#94A3B8]">
                          {log.user_name} • {log.resource_type} • {new Date(log.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        {getActionBadge(log.action)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
