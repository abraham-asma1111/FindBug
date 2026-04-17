'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { AlertCircle, Link2, CheckCircle } from 'lucide-react';

interface DuplicateGroup {
  original_id: string;
  original_title: string;
  original_report_number: string;
  duplicates: Array<{
    id: string;
    report_number: string;
    title: string;
    submitted_at: string;
    bounty_amount: number | null;
  }>;
}

export default function TriageDuplicatesPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedReport, setSelectedReport] = useState<string | null>(null);

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch all reports and group duplicates
  const { data: reportsData, isLoading, error } = useApiQuery<{ reports: any[] }>({
    endpoint: '/triage/queue',
  });

  // Group duplicate reports
  const groups: DuplicateGroup[] = [];
  if (reportsData?.reports) {
    const duplicateMap = new Map<string, any[]>();
    
    reportsData.reports.forEach(report => {
      if (report.is_duplicate && report.duplicate_of) {
        if (!duplicateMap.has(report.duplicate_of)) {
          duplicateMap.set(report.duplicate_of, []);
        }
        duplicateMap.get(report.duplicate_of)?.push(report);
      }
    });

    duplicateMap.forEach((duplicates, originalId) => {
      const original = reportsData.reports.find(r => r.id === originalId);
      if (original && duplicates.length > 0) {
        groups.push({
          original_id: originalId,
          original_title: original.title,
          original_report_number: original.report_number,
          duplicates: duplicates.map(d => ({
            id: d.id,
            report_number: d.report_number,
            title: d.title,
            submitted_at: d.submitted_at,
            bounty_amount: d.bounty_amount,
          })),
        });
      }
    });
  }

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Duplicate Checker"
          subtitle="Identify and link duplicate reports"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Analyzing reports...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load duplicates</p>
              </div>
            </div>
          ) : groups.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <CheckCircle className="mx-auto h-12 w-12 text-[#3B82F6] mb-4" />
              <p className="text-lg font-semibold text-[#F8FAFC]">No duplicates found</p>
            </div>
          ) : (
            <div className="space-y-6">
              {groups.map((group) => (
                <div key={group.original_id} className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">
                    {group.original_title}
                  </h3>
                  <div className="space-y-3">
                    {group.duplicates.map((dup) => (
                      <div key={dup.id} className="flex items-center justify-between p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                        <div className="flex-1">
                          <p className="font-medium text-[#F8FAFC]">{dup.title}</p>
                          <div className="flex gap-4 mt-2 text-sm text-[#94A3B8]">
                            <span>{dup.report_number}</span>
                            <span>{new Date(dup.submitted_at).toLocaleDateString()}</span>
                            {dup.bounty_amount && <span>${dup.bounty_amount.toLocaleString()}</span>}
                          </div>
                        </div>
                        <Button className="gap-2">
                          <Link2 className="w-4 h-4" />
                          Link
                        </Button>
                      </div>
                    ))}
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
