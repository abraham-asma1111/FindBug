'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui/Toast';
import { Search, Star, UserPlus, CheckCircle } from 'lucide-react';
import { withReputationRank } from '@/lib/researcherRanking';

interface CodeReviewAssignReviewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  engagementId: string;
  engagementTitle: string;
  onSuccess: () => void;
}

interface Researcher {
  id: string;
  reputation_rank?: number;
  user: {
    email: string;
    full_name: string;
    username: string;
  };
  reputation_score: number;
  profile?: {
    experience_years?: number;
    skills?: string[];
  };
}

export default function CodeReviewAssignReviewerModal({
  isOpen,
  onClose,
  engagementId,
  engagementTitle,
  onSuccess,
}: CodeReviewAssignReviewerModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResearchers, setSelectedResearchers] = useState<string[]>([]);
  const [isAssigning, setIsAssigning] = useState(false);
  const { showToast } = useToast();

  const { data: researchers, isLoading, error } = useApiQuery<Researcher[]>(
    '/matching/organization/researchers?limit=100'
  );

  const filteredResearchers = withReputationRank(
    (researchers ?? []).filter((researcher) => {
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return (
        researcher.user.full_name?.toLowerCase().includes(q) ||
        researcher.user.email?.toLowerCase().includes(q) ||
        researcher.user.username?.toLowerCase().includes(q)
      );
    })
  );

  const handleToggleResearcher = (researcherId: string) => {
    setSelectedResearchers((prev) =>
      prev.includes(researcherId) ? prev.filter((id) => id !== researcherId) : [...prev, researcherId]
    );
  };

  const handleAssign = async () => {
    if (selectedResearchers.length === 0) {
      showToast('Select at least one reviewer.', 'error');
      return;
    }
    setIsAssigning(true);
    try {
      await api.post(`/code-review/engagements/${engagementId}/assign`, {
        reviewer_ids: selectedResearchers,
      });
      showToast(
        `${selectedResearchers.length} reviewer${selectedResearchers.length > 1 ? 's' : ''} assigned successfully.`,
        'success'
      );
      setSelectedResearchers([]);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      showToast(axiosErr.response?.data?.detail || 'Failed to assign reviewers.', 'error');
    } finally {
      setIsAssigning(false);
    }
  };

  const handleClose = () => {
    if (!isAssigning) {
      setSelectedResearchers([]);
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Assign code reviewers" size="lg">
      <div className="space-y-4">
        <p className="text-sm text-[#6d6760]">
          Select one or more researchers for{' '}
          <span className="font-semibold text-[#2d2a26]">{engagementTitle}</span>. Ranked by reputation
          (#1 = highest). All selected reviewers will see this assignment in their Code Review desk.
        </p>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#8b8177]" />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-[#e6ddd4] bg-white py-2.5 pl-10 pr-4 text-sm focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
          />
        </div>

        {selectedResearchers.length > 0 ? (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800">
            <span className="font-semibold">{selectedResearchers.length}</span> reviewer
            {selectedResearchers.length > 1 ? 's' : ''} selected
          </div>
        ) : null}

        {isLoading ? (
          <p className="py-8 text-center text-sm text-[#6d6760]">Loading researchers...</p>
        ) : error ? (
          <p className="text-sm text-red-600">Failed to load researchers.</p>
        ) : filteredResearchers.length === 0 ? (
          <p className="py-8 text-center text-sm text-[#6d6760]">No researchers match your search.</p>
        ) : (
          <div className="max-h-72 space-y-2 overflow-y-auto">
            {filteredResearchers.map((researcher) => {
              const selected = selectedResearchers.includes(researcher.id);
              return (
                <button
                  key={researcher.id}
                  type="button"
                  onClick={() => handleToggleResearcher(researcher.id)}
                  className={`flex w-full items-center justify-between rounded-xl border p-4 text-left transition ${
                    selected
                      ? 'border-[#10b981] bg-emerald-50'
                      : 'border-[#e6ddd4] bg-white hover:border-[#10b981]/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-100 text-sm font-bold text-amber-900">
                      #{researcher.reputation_rank}
                    </span>
                    <div>
                      <p className="font-semibold text-[#2d2a26]">{researcher.user.full_name}</p>
                      <p className="text-xs text-[#6d6760]">{researcher.user.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1 text-sm text-[#6d6760]">
                      <Star className="h-4 w-4 text-amber-500" />
                      {researcher.reputation_score}
                    </div>
                    <div
                      className={`flex h-6 w-6 items-center justify-center rounded-full border-2 ${
                        selected ? 'border-[#10b981] bg-[#10b981]' : 'border-[#e6ddd4] bg-white'
                      }`}
                    >
                      {selected ? <CheckCircle className="h-4 w-4 text-white" /> : null}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        <div className="flex justify-end gap-3 border-t border-[#e6ddd4] pt-4">
          <Button variant="outline" onClick={handleClose} disabled={isAssigning}>
            Cancel
          </Button>
          <Button icon={UserPlus} isLoading={isAssigning} onClick={handleAssign}>
            Assign {selectedResearchers.length > 0 ? `(${selectedResearchers.length})` : ''}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
