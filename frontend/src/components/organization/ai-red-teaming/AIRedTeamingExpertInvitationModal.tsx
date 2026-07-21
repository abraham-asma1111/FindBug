'use client';

import { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import Checkbox from '@/components/ui/Checkbox';
import Tabs from '@/components/ui/Tabs';
import { api } from '@/lib/api';
import { useApiQuery } from '@/hooks/useApiQuery';

interface Researcher {
  id: string;
  user: {
    username: string;
    email: string;
  };
  reputation_score: number;
  total_reports: number;
  verified_reports: number;
}

interface MatchRecommendation {
  researcher: Researcher;
  match_score: number;
  skill_score: number;
  reputation_score: number;
  ai_expertise_score: number;
  reasons: string[];
}

interface AIRedTeamingExpertInvitationModalProps {
  isOpen: boolean;
  onClose: () => void;
  engagementId: string;
  onSuccess: () => void;
}

export default function AIRedTeamingExpertInvitationModal({
  isOpen,
  onClose,
  engagementId,
  onSuccess,
}: AIRedTeamingExpertInvitationModalProps) {
  const [activeTab, setActiveTab] = useState<'recommended' | 'browse'>('recommended');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedResearchers, setSelectedResearchers] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);
  const [recommendations, setRecommendations] = useState<MatchRecommendation[]>([]);

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch all researchers for browse tab with search
  const { data: researchers, isLoading } = useApiQuery<Researcher[]>(
    `/ai-red-teaming/engagements/${engagementId}/available-researchers${debouncedSearch ? `?search=${encodeURIComponent(debouncedSearch)}` : ''}`,
    { 
      enabled: isOpen && activeTab === 'browse',
      // Refetch when debounced search query changes
      queryKey: ['available-researchers', engagementId, debouncedSearch]
    }
  );

  // Fetch AI-powered recommendations
  useEffect(() => {
    if (isOpen && activeTab === 'recommended') {
      fetchRecommendations();
    }
  }, [isOpen, activeTab, engagementId]);

  const fetchRecommendations = async () => {
    try {
      setIsLoadingMatches(true);
      const response = await api.post(`/ai-red-teaming/engagements/${engagementId}/match-researchers`, {
        limit: 10,
      });
      setRecommendations(response.data);
    } catch (err: any) {
      console.error('Failed to fetch recommendations:', err);
      // Fallback to browse tab if matching fails
      setActiveTab('browse');
    } finally {
      setIsLoadingMatches(false);
    }
  };

  // Researchers are already filtered by search on the server
  const filteredResearchers = researchers || [];

  const handleToggleResearcher = (researcherId: string) => {
    setSelectedResearchers((prev) =>
      prev.includes(researcherId)
        ? prev.filter((id) => id !== researcherId)
        : [...prev, researcherId]
    );
  };

  const handleSubmit = async () => {
    if (selectedResearchers.length === 0) {
      setError('Please select at least one researcher');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');

      await api.post(`/ai-red-teaming/engagements/${engagementId}/assign-experts`, {
        researcher_ids: selectedResearchers,
      });

      onSuccess();
      onClose();
      setSelectedResearchers([]);
      setSearchQuery('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to assign experts');
    } finally {
      setIsSubmitting(false);
    }
  };

  const tabs = [
    { id: 'recommended', label: '🤖 AI Recommendations' },
    { id: 'browse', label: '🔍 Browse All' },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Invite AI Security Experts"
      size="large"
    >
      <div className="space-y-4">
        {error && <Alert variant="error">{error}</Alert>}

        <Alert variant="info">
          <strong>Hybrid Approach:</strong> When you publish this engagement (Start Engagement), the BountyMatch algorithm automatically broadcasts to ALL qualified researchers based on AI/ML expertise and reputation. You can also manually invite specific researchers from the filtered list below.
        </Alert>

        <Tabs tabs={tabs} activeTab={activeTab} onChange={(tab) => setActiveTab(tab as any)} />

        {/* Recommended Tab */}
        {activeTab === 'recommended' && (
          <div className="space-y-4">
            <div className="text-sm text-[#6d6760] dark:text-slate-400">
              {selectedResearchers.length} researcher(s) selected
            </div>

            <div className="max-h-96 overflow-y-auto space-y-2 border border-[#e6ddd4] dark:border-gray-700 rounded-lg p-4">
              {isLoadingMatches ? (
                <div className="text-center py-8">
                  <div className="inline-block h-6 w-6 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                  <p className="mt-2 text-sm text-[#6d6760] dark:text-slate-400">
                    Analyzing researchers with AI matching algorithm...
                  </p>
                </div>
              ) : recommendations.length === 0 ? (
                <div className="text-center py-8 text-sm text-[#6d6760] dark:text-slate-400">
                  No recommendations available. Try browsing all researchers.
                </div>
              ) : (
                recommendations.map((rec) => (
                  <div
                    key={rec.researcher.id}
                    className="flex items-start gap-3 p-4 rounded-lg border-2 border-[#7d39c2] bg-[#f6efff] dark:bg-purple-900/20"
                  >
                    <Checkbox
                      checked={selectedResearchers.includes(rec.researcher.id)}
                      onChange={() => handleToggleResearcher(rec.researcher.id)}
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="font-bold text-[#2d2a26] dark:text-slate-100">
                          {rec.researcher.user.username}
                        </div>
                        <span className="inline-flex items-center rounded-full bg-[#7d39c2] px-3 py-1 text-xs font-semibold text-white">
                          {rec.match_score}% Match
                        </span>
                        <span className="inline-flex items-center rounded-full bg-[#eef7ef] px-3 py-1 text-xs font-semibold text-[#24613a]">
                          {rec.researcher.reputation_score} Rep
                        </span>
                      </div>
                      <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-2">
                        {rec.researcher.user.email}
                      </div>
                      <div className="flex gap-4 text-xs text-[#8b8177] dark:text-slate-500 mb-2">
                        <span>Reports: {rec.researcher.total_reports}</span>
                        <span>Verified: {rec.researcher.verified_reports}</span>
                        <span>AI Expertise: {rec.ai_expertise_score}%</span>
                      </div>
                      <div className="space-y-1">
                        {rec.reasons.map((reason, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-[#6d6760] dark:text-slate-400">
                            <span className="text-purple-600">✓</span>
                            <span>{reason}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div className="space-y-4">
            <Input
              label="Search Researchers"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by username or email..."
            />

            <div className="text-sm text-[#6d6760] dark:text-slate-400">
              {selectedResearchers.length} researcher(s) selected
            </div>

            <div className="max-h-96 overflow-y-auto space-y-2 border border-[#e6ddd4] dark:border-gray-700 rounded-lg p-4">
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="inline-block h-6 w-6 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                </div>
              ) : filteredResearchers.length === 0 ? (
                <div className="text-center py-8 text-sm text-[#6d6760] dark:text-slate-400">
                  {searchQuery ? 'No researchers found matching your search' : 'No researchers available'}
                </div>
              ) : (
                filteredResearchers.map((researcher) => (
                  <div
                    key={researcher.id}
                    className="flex items-start gap-3 p-3 rounded-lg border border-[#e6ddd4] dark:border-gray-700 hover:bg-[#fcfaf7] dark:hover:bg-gray-800 transition-colors"
                  >
                    <Checkbox
                      checked={selectedResearchers.includes(researcher.id)}
                      onChange={() => handleToggleResearcher(researcher.id)}
                    />
                    <div className="flex-1">
                      <div className="font-medium text-[#2d2a26] dark:text-slate-100">
                        {researcher.user.username}
                      </div>
                      <div className="text-sm text-[#6d6760] dark:text-slate-400">
                        {researcher.user.email}
                      </div>
                      <div className="flex gap-4 mt-2 text-xs text-[#8b8177] dark:text-slate-500">
                        <span>Reputation: {researcher.reputation_score}</span>
                        <span>Reports: {researcher.total_reports}</span>
                        <span>Verified: {researcher.verified_reports}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} isLoading={isSubmitting}>
            Invite {selectedResearchers.length} Expert(s)
          </Button>
        </div>
      </div>
    </Modal>
  );
}
