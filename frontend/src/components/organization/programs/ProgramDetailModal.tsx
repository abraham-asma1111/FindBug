'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import SimpleTabs from '@/components/ui/SimpleTabs';
import { useApiQuery } from '@/hooks/useApiQuery';
import { formatCurrency, formatDateTime } from '@/lib/portal';
import Card from '@/components/ui/Card';
import RewardEditModal from './RewardEditModal';
import ScopeAddModal from './ScopeAddModal';
import ScopeVerificationWizard from './ScopeVerificationWizard';
import VerificationStatusBadge from './VerificationStatusBadge';
import { api } from '@/lib/api';

interface Program {
  id: string;
  name: string;
  description?: string;
  type: string;
  status: string;
  visibility: string;
  budget?: number;
  scope?: string;
  rules?: string;
  created_at: string;
  updated_at?: string;
}

interface ProgramDetailModalProps {
  program: Program;
  onClose: () => void;
  onUpdate: () => void;
  isArchived?: boolean;
}

export default function ProgramDetailModal({ 
  program, 
  onClose, 
  onUpdate,
  isArchived = false 
}: ProgramDetailModalProps) {
  console.log('ProgramDetailModal rendered with program:', program);
  console.log('Program status:', program.status);
  console.log('Is archived:', isArchived);
  
  const [activeTab, setActiveTab] = useState('overview');
  const [showRewardEditModal, setShowRewardEditModal] = useState(false);
  const [showScopeAddModal, setShowScopeAddModal] = useState(false);
  // Verification wizard state
  const [verifyingScope, setVerifyingScope] = useState<{ id: string; domain: string } | null>(null);

  // Fetch per-program verification summary (for publish gate + scope badges)
  const { data: verificationSummary, refetch: refetchVerification } = useApiQuery(
    `/programs/${program.id}/verification-status`,
    { enabled: true }
  );

  // Helper: get verification status for a specific scope
  const getScopeVerification = (scopeId: string) => {
    if (!verificationSummary?.scopes) return null;
    return verificationSummary.scopes.find((s: any) => s.scope_id === scopeId) || null;
  };

  const VERIFIABLE_TYPES = new Set(['domain', 'web_app', 'api']);

  // Fetch program details
  const { data: programDetails } = useApiQuery(`/programs/${program.id}`, {
    enabled: true,
  });

  // Fetch scopes
  const { data: scopes, refetch: refetchScopes } = useApiQuery(`/programs/${program.id}/scopes`, {
    enabled: activeTab === 'scope',
  });

  // Fetch rewards
  const { data: rewards } = useApiQuery(`/programs/${program.id}/rewards`, {
    enabled: activeTab === 'rewards',
  });

  // Direct API calls instead of useApiMutation
  const [isPublishing, setIsPublishing] = useState(false);
  const [isPausing, setIsPausing] = useState(false);
  const [isResuming, setIsResuming] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [isArchiving, setIsArchiving] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);

  const handlePublish = async (e?: React.MouseEvent) => {
    e?.preventDefault();
    e?.stopPropagation();
    
    console.log('=== PUBLISH BUTTON CLICKED ===');
    console.log('Program ID:', program.id);
    console.log('Program status:', program.status);
    
    if (!program.id) {
      alert('Error: Program ID is missing');
      return;
    }
    
    try {
      setIsPublishing(true);
      const endpoint = `/programs/${program.id}/publish`;
      console.log('Making API call to:', endpoint);
      console.log('Full URL:', `${api.defaults.baseURL}${endpoint}`);
      
      const response = await api.post(endpoint);
      console.log('Publish response:', response.data);
      
      alert('Program published successfully!');
      onUpdate();
      onClose();
    } catch (error: any) {
      console.error('=== PUBLISH ERROR ===');
      console.error('Error object:', error);
      console.error('Response:', error.response);
      console.error('Response data:', error.response?.data);
      alert(error.response?.data?.detail || 'Failed to publish program');
    } finally {
      setIsPublishing(false);
      console.log('=== PUBLISH COMPLETE ===');
    }
  };

  const handlePause = async () => {
    try {
      setIsPausing(true);
      await api.post(`/programs/${program.id}/pause`);
      alert('Program paused successfully!');
      onUpdate();
      onClose();
    } catch (error: any) {
      console.error('Pause error:', error);
      alert(error.response?.data?.detail || 'Failed to pause program');
    } finally {
      setIsPausing(false);
    }
  };

  const handleResume = async () => {
    try {
      setIsResuming(true);
      await api.post(`/programs/${program.id}/resume`);
      alert('Program resumed successfully!');
      onUpdate();
      onClose();
    } catch (error: any) {
      console.error('Resume error:', error);
      alert(error.response?.data?.detail || 'Failed to resume program');
    } finally {
      setIsResuming(false);
    }
  };

  const handleClose = async () => {
    if (!confirm('Are you sure you want to close this program? This action cannot be undone.')) {
      return;
    }
    try {
      setIsClosing(true);
      await api.post(`/programs/${program.id}/close`);
      alert('Program closed successfully!');
      onUpdate();
      onClose();
    } catch (error: any) {
      console.error('Close error:', error);
      alert(error.response?.data?.detail || 'Failed to close program');
    } finally {
      setIsClosing(false);
    }
  };

  const handleArchive = async () => {
    try {
      setIsArchiving(true);
      await api.post(`/programs/${program.id}/archive`);
      alert('Program archived successfully!');
      onUpdate();
      onClose();
    } catch (error: any) {
      console.error('Archive error:', error);
      alert(error.response?.data?.detail || 'Failed to archive program');
    } finally {
      setIsArchiving(false);
    }
  };

  const handleRestore = async () => {
    try {
      setIsRestoring(true);
      await api.post(`/programs/${program.id}/restore`);
      alert('Program restored successfully!');
      onUpdate();
      onClose();
    } catch (error: any) {
      console.error('Restore error:', error);
      alert(error.response?.data?.detail || 'Failed to restore program');
    } finally {
      setIsRestoring(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'scope', label: 'Scope' },
    { id: 'rewards', label: 'Rewards' },
    { id: 'settings', label: 'Settings' },
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Status Badges */}
      <div className="flex flex-wrap items-center gap-2">
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
          program.type === 'bounty' 
            ? 'bg-[#edf5fb] text-[#2d78a8] dark:bg-blue-900 dark:text-blue-200' 
            : 'bg-[#f3e8ff] text-[#6b21a8] dark:bg-purple-900 dark:text-purple-200'
        }`}>
          {program.type.toUpperCase()}
        </span>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
          program.status === 'public' 
            ? 'bg-[#e6f7ed] text-[#0d7a3d] dark:bg-green-900 dark:text-green-200'
            : program.status === 'draft'
            ? 'bg-[#faf1e1] text-[#9a6412] dark:bg-yellow-900 dark:text-yellow-200'
            : program.status === 'paused'
            ? 'bg-[#fff4e6] text-[#b54708] dark:bg-orange-900 dark:text-orange-200'
            : 'bg-[#f3ede6] text-[#5f5851] dark:bg-slate-700 dark:text-slate-300'
        }`}>
          {program.status.charAt(0).toUpperCase() + program.status.slice(1)}
        </span>
        <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851] dark:bg-slate-700 dark:text-slate-300">
          {program.visibility}
        </span>
      </div>

      {/* Description */}
      <div>
        <h4 className="text-sm font-semibold text-[#2d2a26] dark:text-slate-100 mb-2">Description</h4>
        <p className="text-sm text-[#6d6760] dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
          {program.description || 'No description provided'}
        </p>
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="bg-[#faf6f1] dark:bg-[#111111] dark:border-gray-700">
          <p className="text-xs text-[#8b8177] dark:text-slate-400 mb-1">Budget</p>
          <p className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100">
            {program.budget ? formatCurrency(program.budget) : 'Not set'}
          </p>
        </Card>

        <Card className="bg-[#faf6f1] dark:bg-[#111111] dark:border-gray-700">
          <p className="text-xs text-[#8b8177] dark:text-slate-400 mb-1">Created</p>
          <p className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100">
            {formatDateTime(program.created_at)}
          </p>
        </Card>
      </div>

      {/* Rules */}
      {program.rules && (
        <div>
          <h4 className="text-sm font-semibold text-[#2d2a26] dark:text-slate-100 mb-2">Program Rules</h4>
          <div className="rounded-xl bg-[#faf6f1] dark:bg-[#111111] border border-[#e6ddd4] dark:border-gray-700 p-4">
            <p className="text-sm text-[#6d6760] dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {program.rules}
            </p>
          </div>
        </div>
      )}
    </div>
  );

  const renderScope = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-[#2d2a26] dark:text-slate-100">In-Scope Assets</h4>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setShowScopeAddModal(true)}
        >
          + Add Scope
        </Button>
      </div>

      {/* Verification summary banner */}
      {verificationSummary && !verificationSummary.all_verified && program.status === 'draft' && (
        <div style={{
          background: 'rgba(99,102,241,0.08)',
          border: '1px solid rgba(99,102,241,0.25)',
          borderRadius: 10,
          padding: '10px 14px',
          fontSize: 13,
          color: '#818cf8',
        }}>
          🔐 Some scopes require domain verification before this program can be published.
        </div>
      )}

      {scopes && scopes.length > 0 ? (
        <div className="space-y-3">
          {scopes.map((scope: any) => {
            const ver = getScopeVerification(scope.id);
            const needsVerification = VERIFIABLE_TYPES.has(scope.asset_type) && scope.is_in_scope;
            const isVerified = ver?.verification_status === 'verified';

            return (
              <Card key={scope.id} className="bg-[#faf6f1] dark:bg-[#111111] dark:border-gray-700">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="text-sm font-semibold text-[#2d2a26] dark:text-slate-100">{scope.asset_type}</p>
                      {needsVerification && (
                        <VerificationStatusBadge
                          status={ver?.verification_status || 'unverified'}
                          size="sm"
                        />
                      )}
                    </div>
                    <p className="text-sm text-[#6d6760] dark:text-slate-300 mt-1">{scope.asset_identifier}</p>
                    {scope.description && (
                      <p className="text-xs text-[#8b8177] dark:text-slate-400 mt-1">{scope.description}</p>
                    )}
                    {ver?.verified_at && (
                      <p className="text-xs text-emerald-500 mt-1">✓ Verified {new Date(ver.verified_at).toLocaleDateString()}</p>
                    )}
                    {ver?.failure_reason && !isVerified && (
                      <p className="text-xs text-red-400 mt-1 truncate max-w-xs" title={ver.failure_reason}>
                        ✗ {ver.failure_reason}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      scope.is_in_scope
                        ? 'bg-[#e6f7ed] text-[#0d7a3d] dark:bg-green-900 dark:text-green-200'
                        : 'bg-[#fde9e7] text-[#9d1f1f] dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {scope.is_in_scope ? 'In Scope' : 'Out of Scope'}
                    </span>
                    {needsVerification && !isVerified && (
                      <button
                        onClick={() => setVerifyingScope({ id: scope.id, domain: scope.asset_identifier })}
                        style={{
                          fontSize: 11, fontWeight: 700, color: '#818cf8',
                          background: 'rgba(99,102,241,0.10)', border: '1px solid rgba(99,102,241,0.25)',
                          borderRadius: 6, padding: '3px 10px', cursor: 'pointer',
                        }}
                      >
                        🔐 Verify Now
                      </button>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card className="bg-[#faf6f1] dark:bg-[#111111] dark:border-gray-700">
          <p className="text-sm text-[#6d6760] dark:text-slate-300 text-center py-8">
            {program.scope || 'No scope defined yet. Click "+ Add Scope" to add assets.'}
          </p>
        </Card>
      )}
    </div>
  );

  const renderRewards = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-[#2d2a26] dark:text-slate-100">Reward Tiers</h4>
        <Button 
          variant="secondary" 
          size="sm"
          onClick={() => setShowRewardEditModal(true)}
        >
          Edit Rewards
        </Button>
      </div>

      {rewards && rewards.length > 0 ? (
        <div className="space-y-3">
          {rewards.map((reward: any) => (
            <Card key={reward.id} className="bg-[#faf6f1] dark:bg-[#111111] dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-[#2d2a26] dark:text-slate-100 capitalize">
                    {reward.severity}
                  </p>
                  <p className="text-xs text-[#8b8177] dark:text-slate-400 mt-1">
                    {reward.description || 'Standard bounty'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100">
                    {formatCurrency(reward.min_amount)} - {formatCurrency(reward.max_amount)}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-[#faf6f1] dark:bg-[#111111] dark:border-gray-700">
          <p className="text-sm text-[#6d6760] dark:text-slate-300 text-center py-8">
            No reward tiers configured yet
          </p>
        </Card>
      )}
    </div>
  );

  const renderSettings = () => {
    // Collect unverified verifiable scopes for the publish gate
    const unverifiedScopes = verificationSummary?.scopes?.filter(
      (s: any) => s.needs_verification && s.verification_status !== 'verified'
    ) || [];
    const canPublish = unverifiedScopes.length === 0;

    return (
      <div className="space-y-6">
        <div>
          <h4 className="text-sm font-semibold text-[#2d2a26] dark:text-slate-100 mb-4">Program Actions</h4>
          <div className="space-y-3">
            {program.status === 'draft' && (
              <>
                {/* Verification gate banner */}
                {!canPublish && (
                  <div style={{
                    background: 'rgba(239,68,68,0.08)',
                    border: '1px solid rgba(239,68,68,0.25)',
                    borderRadius: 10,
                    padding: '12px 16px',
                    marginBottom: 8,
                  }}>
                    <p style={{ color: '#fca5a5', fontSize: 13, fontWeight: 600, margin: '0 0 6px' }}>
                      🔐 Cannot publish — unverified scopes:
                    </p>
                    <ul style={{ margin: 0, paddingLeft: 18, color: '#f87171', fontSize: 12 }}>
                      {unverifiedScopes.map((s: any) => (
                        <li key={s.scope_id}>
                          {s.asset_identifier}
                          {' '}
                          <button
                            onClick={() => setVerifyingScope({ id: s.scope_id, domain: s.asset_identifier })}
                            style={{ color: '#818cf8', background: 'none', border: 'none', cursor: 'pointer', fontSize: 11, fontWeight: 700, textDecoration: 'underline', padding: 0 }}
                          >
                            Verify
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <Button
                  type="button"
                  onClick={(e) => { handlePublish(e); }}
                  disabled={isPublishing || !canPublish}
                  className="w-full"
                  title={!canPublish ? 'Verify all domain scopes before publishing' : undefined}
                >
                  {isPublishing ? 'Publishing...' : 'Publish Program'}
                </Button>
              </>
            )}

          {program.status === 'public' && (
            <Button
              onClick={handlePause}
              disabled={isPausing}
              variant="secondary"
              className="w-full"
            >
              {isPausing ? 'Pausing...' : 'Pause Program'}
            </Button>
          )}

          {program.status === 'paused' && (
            <Button
              onClick={handleResume}
              disabled={isResuming}
              className="w-full"
            >
              {isResuming ? 'Resuming...' : 'Resume Program'}
            </Button>
          )}

          {(program.status === 'public' || program.status === 'paused') && (
            <Button
              onClick={handleClose}
              disabled={isClosing}
              variant="secondary"
              className="w-full"
            >
              {isClosing ? 'Closing...' : 'Close Program'}
            </Button>
          )}

          {program.status === 'closed' && !isArchived && (
            <Button
              onClick={handleArchive}
              disabled={isArchiving}
              variant="secondary"
              className="w-full"
            >
              {isArchiving ? 'Archiving...' : 'Archive Program'}
            </Button>
          )}

          {isArchived && (
            <Button
              onClick={handleRestore}
              disabled={isRestoring}
              className="w-full"
            >
              {isRestoring ? 'Restoring...' : 'Restore Program'}
            </Button>
          )}
        </div>
      </div>

      <div className="rounded-xl bg-[#faf1e1] dark:bg-yellow-900 border border-[#f0d9a8] dark:border-yellow-800 p-4">
        <p className="text-sm text-[#9a6412] dark:text-yellow-200">
          <strong>Note:</strong> Closing a program will prevent new submissions but existing reports will remain accessible.
        </p>
      </div>
    </div>
  );
};

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'scope':
        return renderScope();
      case 'rewards':
        return renderRewards();
      case 'settings':
        return renderSettings();
      default:
        return null;
    }
  };

  return (
    <>
      <Modal
        isOpen={true}
        onClose={onClose}
        title={program.name}
        size="xl"
      >
        <div className="space-y-6">
          <SimpleTabs
            tabs={tabs}
            activeTab={activeTab}
            onChange={setActiveTab}
          />

          <div className="min-h-[400px]">
            {renderContent()}
          </div>
        </div>
      </Modal>

      {/* Reward Edit Modal */}
      {showRewardEditModal && (
        <RewardEditModal
          programId={program.id}
          existingRewards={rewards || []}
          onClose={() => setShowRewardEditModal(false)}
          onSuccess={() => {
            setShowRewardEditModal(false);
            window.location.reload();
          }}
        />
      )}

      {/* Scope Add Modal */}
      {showScopeAddModal && (
        <ScopeAddModal
          programId={program.id}
          onClose={() => setShowScopeAddModal(false)}
          onSuccess={() => {
            setShowScopeAddModal(false);
            refetchScopes();
            refetchVerification();
          }}
        />
      )}

      {/* Scope Verification Wizard */}
      {verifyingScope && (
        <ScopeVerificationWizard
          scopeId={verifyingScope.id}
          domain={verifyingScope.domain}
          onClose={() => {
            setVerifyingScope(null);
            refetchVerification();
          }}
          onVerified={() => {
            setVerifyingScope(null);
            refetchVerification();
          }}
        />
      )}
    </>
  );
}
