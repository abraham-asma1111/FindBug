'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import SimpleTabs from '@/components/ui/SimpleTabs';
import EmptyState from '@/components/ui/EmptyState';
import PTaaSEngagementList from '@/components/organization/services/ptaas/PTaaSEngagementList';
import CodeReviewEngagementList from '@/components/organization/services/code-review/CodeReviewEngagementList';
import LiveEventsList from '@/components/organization/services/live-events/LiveEventsList';
import AIRedTeamingEngagementList from '@/components/organization/services/ai-red-teaming/AIRedTeamingEngagementList';

export default function OrganizationServicesPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState('matching');

  const tabs = [
    { id: 'matching', label: 'Matching', count: 0 },
    { id: 'ptaas', label: 'PTaaS', count: 0 },
    { id: 'ai-red-teaming', label: 'AI Red Teaming', count: 0 },
    { id: 'code-review', label: 'Code Review', count: 0 },
    { id: 'live-events', label: 'Live Events', count: 0 },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'matching':
        return (
          <EmptyState
            title="Matching Service"
            description="Intelligent researcher matching and invitation management. Connect with the right security experts for your programs."
            action={undefined}
          />
        );
      case 'ptaas':
        return <PTaaSEngagementList />;
      case 'ai-red-teaming':
        return <AIRedTeamingEngagementList />;
      case 'code-review':
        return <CodeReviewEngagementList />;
      case 'live-events':
        return <LiveEventsList />;
      default:
        return null;
    }
  };

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Services Management"
          subtitle=""
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
        >
          {/* Hero Section */}
          <section className="rounded-[36px] border border-[#d8d0c8] bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(255,255,255,0.72)_35%,rgba(244,195,139,0.28)_75%),linear-gradient(135deg,#f7efe6_0%,#f6e8d3_45%,#efe1cf_100%)] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#8b8177]">
                Specialized Services
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                Manage security testing services and engagements.
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#5f5851] sm:text-base">
                Access specialized security services including PTaaS, AI Red Teaming, Code Review, Live Events, and intelligent researcher matching.
              </p>
            </div>
          </section>

          {/* Tabs */}
          <div className="mt-8">
            <SimpleTabs
              tabs={tabs}
              activeTab={activeTab}
              onChange={setActiveTab}
            />
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {renderTabContent()}
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
