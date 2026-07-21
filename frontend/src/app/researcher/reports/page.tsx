'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import SectionCard from '@/components/dashboard/SectionCard';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import ReportList from '@/components/researcher/reports/ReportList';
import ReportSubmissionForm from '@/components/researcher/reports/ReportSubmissionForm';

export default function ReportsPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState('my-reports');

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Reports"
          subtitle="Manage your vulnerability reports and submissions"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          {/* Tabs */}
          <div className="mb-6 flex justify-center">
            <div className="flex gap-6">
              <button
                onClick={() => setActiveTab('my-reports')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'my-reports'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300 hover:bg-[#eadfd3] dark:hover:bg-neutral-700'
                }`}
              >
                My Reports
              </button>
              <button
                onClick={() => setActiveTab('submit-new')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'submit-new'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300 hover:bg-[#eadfd3] dark:hover:bg-neutral-700'
                }`}
              >
                Submit New
              </button>
              <button
                onClick={() => setActiveTab('drafts')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'drafts'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300 hover:bg-[#eadfd3] dark:hover:bg-neutral-700'
                }`}
              >
                Drafts
              </button>
              <button
                onClick={() => setActiveTab('templates')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'templates'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300 hover:bg-[#eadfd3] dark:hover:bg-neutral-700'
                }`}
              >
                Templates
              </button>
            </div>
          </div>

          {/* Content */}
          {activeTab === 'my-reports' && (
            <SectionCard
              title="My Reports"
              description="All your submitted vulnerability reports with status and rewards."
              headerAlign="center"
            >
              <ReportList />
            </SectionCard>
          )}

          {activeTab === 'submit-new' && (
            <SectionCard
              title="Submit New Report"
              description="Submit a new vulnerability report to a program."
              headerAlign="center"
            >
              <ReportSubmissionForm />
            </SectionCard>
          )}

          {activeTab === 'drafts' && (
            <SectionCard
              title="Draft Reports"
              description="Your saved draft reports."
              headerAlign="center"
            >
              <div className="py-10 text-center">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                  No drafts found
                </p>
                <p className="mt-2 text-sm text-[#6d6760]">
                  You don't have any draft reports. Start a new report and save it as draft.
                </p>
              </div>
            </SectionCard>
          )}

          {activeTab === 'templates' && (
            <SectionCard
              title="Report Templates"
              description="Create and manage report templates."
              headerAlign="center"
            >
              <div className="py-10 text-center">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                  No templates found
                </p>
                <p className="mt-2 text-sm text-[#6d6760]">
                  Create report templates to speed up your submission process.
                </p>
              </div>
            </SectionCard>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
