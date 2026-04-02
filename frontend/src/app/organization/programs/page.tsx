'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Tabs from '@/components/ui/Tabs';
import EmptyState from '@/components/ui/EmptyState';
import ProgramList from '@/components/organization/programs/ProgramList';
import ProgramCreateModal from '@/components/organization/programs/ProgramCreateModal';

export default function OrganizationProgramsPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState('active');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Fetch programs based on active tab
  const { data: programs, isLoading, error, refetch } = useApiQuery(
    activeTab === 'archived' ? '/programs/archived' : '/programs/my-programs',
    { enabled: !!user }
  );

  // Filter programs by status for tabs
  const activePrograms = programs?.filter((p: any) => 
    p.status === 'public' || p.status === 'paused'
  ) || [];
  
  const draftPrograms = programs?.filter((p: any) => 
    p.status === 'draft'
  ) || [];

  const tabs = [
    { id: 'active', label: 'Active Programs', count: activePrograms.length },
    { id: 'drafts', label: 'Drafts', count: draftPrograms.length },
    { id: 'archived', label: 'Archived', count: activeTab === 'archived' ? programs?.length || 0 : 0 },
  ];

  const getCurrentPrograms = () => {
    if (activeTab === 'archived') return programs || [];
    if (activeTab === 'drafts') return draftPrograms;
    return activePrograms;
  };

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Programs Management"
          subtitle="Create and manage your bug bounty programs"
          navItems={getPortalNavItems(user.role)}
        >
          <div className="space-y-6">
            {/* Header with Create Button */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-[#2d2a26]">Bug Bounty Programs</h2>
                <p className="mt-1 text-sm text-[#6d6760]">
                  Manage your security programs and invite researchers
                </p>
              </div>
              <Button onClick={() => setShowCreateModal(true)}>
                + Create Program
              </Button>
            </div>

            {/* Tabs */}
            <Tabs
              tabs={tabs}
              activeTab={activeTab}
              onChange={setActiveTab}
            />

            {/* Error State */}
            {error && (
              <Card className="border-[#f2c0bc] bg-[#fff2f1]">
                <p className="text-sm text-[#b42318]">{error}</p>
              </Card>
            )}

            {/* Programs List */}
            {isLoading ? (
              <Card>
                <div className="flex items-center justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                </div>
              </Card>
            ) : getCurrentPrograms().length > 0 ? (
              <ProgramList 
                programs={getCurrentPrograms()} 
                onUpdate={refetch}
                isArchived={activeTab === 'archived'}
              />
            ) : (
              <EmptyState
                title={
                  activeTab === 'drafts' 
                    ? 'No draft programs' 
                    : activeTab === 'archived'
                    ? 'No archived programs'
                    : 'No active programs'
                }
                description={
                  activeTab === 'drafts'
                    ? 'Draft programs will appear here'
                    : activeTab === 'archived'
                    ? 'Archived programs will appear here'
                    : 'Create your first bug bounty program to get started'
                }
                action={
                  activeTab === 'active' ? (
                    <Button onClick={() => setShowCreateModal(true)}>
                      Create Your First Program
                    </Button>
                  ) : undefined
                }
              />
            )}
          </div>

          {/* Create Program Modal */}
          {showCreateModal && (
            <ProgramCreateModal
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
