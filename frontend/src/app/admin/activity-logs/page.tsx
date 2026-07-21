'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { Clock, Globe } from 'lucide-react';

export default function AdminAuditLogsPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const [filter, setFilter] = useState('all');
  const endpoint = filter !== 'all'
    ? `/admin/audit-logs?action_type=${filter}`
    : '/admin/audit-logs';
  const { data, isLoading } = useApiQuery({
    endpoint,
  });

  const logs = data?.logs || [];

  const getSeverityBadge = (severity: string) => {
    const map: Record<string, string> = {
      info: 'bg-[#3B82F6] text-white',
      low: 'bg-[#10B981] text-white',
      medium: 'bg-[#F59E0B] text-white',
      high: 'bg-[#EF4444] text-white',
      critical: 'bg-[#991B1B] text-white',
    };
    return (
      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${map[severity?.toLowerCase()] || 'bg-[#64748B] text-white'}`}>
        {severity?.toUpperCase() || 'INFO'}
      </span>
    );
  };

  const getCategoryConfig = (category: string) => {
    const config: Record<string, { color: string, bg: string, text: string }> = {
      report:   { color: 'border-l-[#38BDF8]', bg: 'bg-[#0ea5e9]/10', text: 'text-[#38BDF8]' },
      bounty:   { color: 'border-l-[#10B981]', bg: 'bg-[#10b981]/10', text: 'text-[#10B981]' },
      user:     { color: 'border-l-[#8B5CF6]', bg: 'bg-[#8b5cf6]/10', text: 'text-[#8B5CF6]' },
      program:  { color: 'border-l-[#F59E0B]', bg: 'bg-[#f59e0b]/10', text: 'text-[#F59E0B]' },
      admin:    { color: 'border-l-[#EF4444]', bg: 'bg-[#ef4444]/10', text: 'text-[#EF4444]' },
      config:   { color: 'border-l-[#F97316]', bg: 'bg-[#f97316]/10', text: 'text-[#F97316]' },
      ptaas:    { color: 'border-l-[#EC4899]', bg: 'bg-[#ec4899]/10', text: 'text-[#EC4899]' },
      auth:     { color: 'border-l-[#6366F1]', bg: 'bg-[#6366f1]/10', text: 'text-[#6366F1]' },
      security: { color: 'border-l-[#DC2626]', bg: 'bg-[#dc2626]/10', text: 'text-[#DC2626]' },
    };
    return config[category] || { color: 'border-l-[#475569]', bg: 'bg-[#475569]/10', text: 'text-[#94A3B8]' };
  };

  return (
    <ProtectedRoute allowedRoles={['admin']}>
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
                System-wide audit trail for security, authentication, and platform operations.
              </p>
              
              {/* Filters */}
              <div className="mt-8 flex flex-wrap justify-center gap-2">
                {[
                  { key: 'all',      label: 'All Events' },
                  { key: 'report',   label: 'Reports' },
                  { key: 'bounty',   label: 'Bounties' },
                  { key: 'user',     label: 'Users' },
                  { key: 'program',  label: 'Programs' },
                  { key: 'ptaas',    label: 'PTaaS' },
                  { key: 'admin',    label: 'Admin' },
                  { key: 'config',   label: 'Config' },
                  { key: 'auth',     label: 'Auth' },
                  { key: 'security', label: 'Security' },
                ].map(({ key, label }) => (
                  <button
                    key={key}
                    onClick={() => setFilter(key)}
                    className={`px-4 py-2 rounded-full text-xs font-semibold transition-all duration-200 border shadow-sm ${
                      filter === key
                        ? 'bg-[#1E293B] border-[#38BDF8] text-[#F8FAFC] shadow-[#38BDF8]/20'
                        : 'bg-[#0F172A] border-[#334155] text-[#94A3B8] hover:text-[#F8FAFC] hover:border-[#475569] hover:bg-[#1E293B]'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* Audit Logs List - Streamlined Cards */}
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
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
                {logs.map((log: any, index: number) => {
                  const config = getCategoryConfig(log.category);
                  return (
                    <div key={log.id}>
                      <div 
                        className={`px-5 py-4 hover:bg-[#263348]/50 transition-colors duration-150 border-l-[3px] ${config.color}`}
                      >
                        {/* Header Row: Category, Event Type, Severity, Timestamp */}
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <span className={`text-sm font-bold uppercase tracking-wide ${config.text}`}>
                              {log.category}
                            </span>
                            <span className="font-mono text-xs font-semibold text-[#CBD5E1] bg-[#0F172A] px-2.5 py-1 rounded border border-[#334155]">
                              {log.event_type}
                            </span>
                            {log.severity && getSeverityBadge(log.severity)}
                          </div>
                          
                          <div className="flex items-center gap-2 text-sm text-[#94A3B8] bg-[#0F172A] px-3 py-1.5 rounded border border-[#334155]">
                            <Clock className="w-4 h-4" />
                            <time className="font-semibold">
                              {log.timestamp ? new Date(log.timestamp).toLocaleString(undefined, {
                                month: 'short', 
                                day: 'numeric', 
                                hour: '2-digit', 
                                minute: '2-digit'
                              }) : '—'}
                            </time>
                          </div>
                        </div>
                        
                        {/* Description */}
                        <p className="text-[15px] text-[#F1F5F9] font-medium leading-relaxed mb-3">
                          {log.description}
                        </p>
                        
                        {/* Footer Row: Actor and IP */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2.5">
                            <span className="text-sm font-semibold text-[#E2E8F0]">
                              {log.display_name || log.organization_name || log.target_username || log.user_email || 'System'}
                            </span>
                            {log.actor_role && (
                              <span className="text-[10px] px-2 py-1 rounded bg-[#0F172A] text-[#CBD5E1] border border-[#475569] uppercase tracking-wider font-bold">
                                {log.actor_role}
                              </span>
                            )}
                          </div>
                          
                          {log.ip_address && (
                            <div className="flex items-center gap-1.5 text-xs text-[#94A3B8] font-mono bg-[#0F172A] px-2.5 py-1 rounded border border-[#334155]">
                              <Globe className="w-3.5 h-3.5" />
                              <span className="font-semibold">{log.ip_address}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* Thick horizontal separator (except for last item) */}
                      {index < logs.length - 1 && (
                        <div className="h-[2px] bg-gradient-to-r from-transparent via-[#475569] to-transparent"></div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <p className="mt-4 text-xs text-[#64748B]">
            Showing {logs.length} log entr{logs.length !== 1 ? 'ies' : 'y'}
          </p>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
