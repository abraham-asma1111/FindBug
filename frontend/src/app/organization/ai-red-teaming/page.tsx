'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/ui/EmptyState';
import AIRedTeamingEngagementList from '@/components/organization/ai-red-teaming/AIRedTeamingEngagementList';
import AIRedTeamingEngagementCreateModal from '@/components/organization/ai-red-teaming/AIRedTeamingEngagementCreateModal';

export default function OrganizationAIRedTeamingPage() {
  const user = useAuthStore((state) => state.user);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Fetch AI Red Teaming engagements
  const { data: engagements, isLoading, error, refetch } = useApiQuery(
    '/ai-red-teaming/engagements',
    { enabled: !!user }
  );

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="AI Red Teaming"
          subtitle="Manage AI security testing engagements"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Header with Create Button */}
            <div className="flex items-start justify-between">
              <div className="flex-1 ml-12">
                <h2 className="text-3xl font-bold text-[#2d2a26] dark:text-slate-100">
                  AI Red Teaming Engagements
                </h2>
                <p className="mt-3 text-sm text-[#6d6760] dark:text-slate-400">
                  Test AI systems for prompt injection, jailbreaking, data leakage, and model vulnerabilities
                </p>
              </div>
              <Button onClick={() => setShowCreateModal(true)}>
                Create Engagement
              </Button>
            </div>

            {/* Error State */}
            {error && (
              <Card className="border-[#f2c0bc] bg-[#fff2f1]">
                <p className="text-sm text-[#b42318]">
                  {error.message || 'An error occurred'}
                </p>
              </Card>
            )}

            {/* Engagements List */}
            {isLoading ? (
              <Card>
                <div className="flex items-center justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                </div>
              </Card>
            ) : engagements && engagements.length > 0 ? (
              <AIRedTeamingEngagementList 
                engagements={engagements} 
                onUpdate={refetch}
              />
            ) : (
              <EmptyState
                title="No AI Red Teaming engagements"
                description="Create your first AI security testing engagement to identify vulnerabilities in your AI systems"
                action={
                  <Button onClick={() => setShowCreateModal(true)}>
                    Create Your First Engagement
                  </Button>
                }
              />
            )}
          </div>

          {/* Create Engagement Modal */}
          {showCreateModal && (
            <AIRedTeamingEngagementCreateModal
              onClose={() => setShowCreateModal(false)}
              onSuccess={() => {
                setShowCreateModal(false);
                refetch();
              }}
            />
          )}
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
