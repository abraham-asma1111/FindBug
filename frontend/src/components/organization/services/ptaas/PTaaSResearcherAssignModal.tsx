'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useToast } from '@/components/ui/Toast';
import { Search, Users, Star, Award, CheckCircle, UserPlus, Filter } from 'lucide-react';

interface PTaaSResearcherAssignModalProps {
  isOpen: boolean;
  onClose: () => void;
  engagementId: string;
  engagementName: string;
  onSuccess: () => void;
}

interface Researcher {
  id: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    username: string;
  };
  reputation_score: number;
  total_reports: number;
  verified_reports: number;
  profile: {
    experience_years: number;
    skills: string[];
    specializations: string[];
    bio: string;
  };
}

export default function PTaaSResearcherAssignModal({
  isOpen,
  onClose,
  engagementId,
  engagementName,
  onSuccess,
}: PTaaSResearcherAssignModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResearchers, setSelectedResearchers] = useState<string[]>([]);
  const [minReputation, setMinReputation] = useState(0);
  const [skillFilter, setSkillFilter] = useState('');
  const { showToast } = useToast();

  // Fetch researchers
  const { data: researchers, isLoading, error } = useApiQuery<Researcher[]>({
    endpoint: '/matching/organization/researchers?limit=100',
    queryKey: ['researchers-list'],
  });

  // Send invitations mutation
  const { mutate: sendInvitations, isLoading: isSending } = useApiMutation(
    `/ptaas/engagements/${engagementId}/assign`,
    'POST',
    {
      onSuccess: () => {
        showToast('Researchers assigned successfully!', 'success');
        onSuccess();
        onClose();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to assign researchers', 'error');
      },
    }
  );

  const handleToggleResearcher = (researcherId: string) => {
    setSelectedResearchers((prev) =>
      prev.includes(researcherId)
        ? prev.filter((id) => id !== researcherId)
        : [...prev, researcherId]
    );
  };

  const handleAssign = () => {
    if (selectedResearchers.length === 0) {
      showToast('Please select at least one researcher', 'error');
      return;
    }

    sendInvitations({
      researcher_ids: selectedResearchers,
    });
  };

  // Filter researchers
  const filteredResearchers = researchers?.filter((researcher) => {
    // Search filter
    const matchesSearch =
      !searchQuery ||
      researcher.user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      researcher.user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      researcher.user.username.toLowerCase().includes(searchQuery.toLowerCase());

    // Reputation filter
    const matchesReputation = researcher.reputation_score >= minReputation;

    // Skill filter
    const matchesSkill =
      !skillFilter ||
      researcher.profile.skills.some((skill) =>
        skill.toLowerCase().includes(skillFilter.toLowerCase())
      ) ||
      researcher.profile.specializations.some((spec) =>
        spec.toLowerCase().includes(skillFilter.toLowerCase())
      );

    return matchesSearch && matchesReputation && matchesSkill;
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Assign Researchers" size="xl">
      <div className="space-y-6">
        {/* Engagement Info */}
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
          <div className="flex items-start gap-3">
            <Users className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900">Assigning to: {engagementName}</h4>
              <p className="mt-1 text-sm text-blue-700">
                Select researchers to invite to this engagement. They will receive notifications and can accept or decline.
              </p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm font-medium text-[#2d2a26]">
            <Filter className="h-4 w-4" />
            <span>Filter Researchers</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-2">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#8b8177]" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Name, email, username..."
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#e6ddd4] bg-white text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                />
              </div>
            </div>

            {/* Min Reputation */}
            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-2">
                Min Reputation
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={minReputation}
                onChange={(e) => setMinReputation(parseInt(e.target.value) || 0)}
                className="w-full px-4 py-2.5 rounded-xl border border-[#e6ddd4] bg-white text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
              />
            </div>

            {/* Skill Filter */}
            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-2">
                Skill/Specialization
              </label>
              <input
                type="text"
                value={skillFilter}
                onChange={(e) => setSkillFilter(e.target.value)}
                placeholder="e.g., Web Security, API..."
                className="w-full px-4 py-2.5 rounded-xl border border-[#e6ddd4] bg-white text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
              />
            </div>
          </div>
        </div>

        {/* Selected Count */}
        {selectedResearchers.length > 0 && (
          <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-2">
            <p className="text-sm text-green-700">
              <span className="font-semibold">{selectedResearchers.length}</span> researcher(s) selected
            </p>
          </div>
        )}

        {/* Researchers List */}
        <div className="space-y-3 max-h-[400px] overflow-y-auto">
          {isLoading && (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#ef2330] border-r-transparent"></div>
              <p className="mt-4 text-sm text-[#6d6760]">Loading researchers...</p>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4">
              <p className="text-sm text-red-700">Failed to load researchers. Please try again.</p>
            </div>
          )}

          {!isLoading && !error && filteredResearchers && filteredResearchers.length === 0 && (
            <div className="text-center py-8">
              <Users className="mx-auto h-12 w-12 text-[#8b8177]" />
              <p className="mt-4 text-sm text-[#6d6760]">
                No researchers found matching your filters
              </p>
            </div>
          )}

          {!isLoading &&
            !error &&
            filteredResearchers &&
            filteredResearchers.map((researcher) => (
              <div
                key={researcher.id}
                onClick={() => handleToggleResearcher(researcher.id)}
                className={`rounded-xl border-2 p-4 cursor-pointer transition-all ${
                  selectedResearchers.includes(researcher.id)
                    ? 'border-[#3b82f6] bg-blue-50'
                    : 'border-[#e6ddd4] bg-white hover:border-[#3b82f6]/50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                        {researcher.user.full_name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h4 className="font-semibold text-[#2d2a26]">
                          {researcher.user.full_name}
                        </h4>
                        <p className="text-sm text-[#6d6760]">@{researcher.user.username}</p>
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="mt-3 flex items-center gap-4">
                      <div className="flex items-center gap-1.5">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm font-medium text-[#2d2a26]">
                          {researcher.reputation_score}
                        </span>
                        <span className="text-xs text-[#8b8177]">reputation</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Award className="h-4 w-4 text-green-500" />
                        <span className="text-sm font-medium text-[#2d2a26]">
                          {researcher.verified_reports}
                        </span>
                        <span className="text-xs text-[#8b8177]">verified</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Users className="h-4 w-4 text-blue-500" />
                        <span className="text-sm font-medium text-[#2d2a26]">
                          {researcher.profile.experience_years}
                        </span>
                        <span className="text-xs text-[#8b8177]">years exp</span>
                      </div>
                    </div>

                    {/* Skills */}
                    {researcher.profile.skills.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {researcher.profile.skills.slice(0, 3).map((skill, idx) => (
                          <span
                            key={idx}
                            className="inline-block rounded-lg bg-purple-50 px-2.5 py-1 text-xs font-medium text-purple-700"
                          >
                            {skill}
                          </span>
                        ))}
                        {researcher.profile.skills.length > 3 && (
                          <span className="inline-block rounded-lg bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                            +{researcher.profile.skills.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Selection Indicator */}
                  <div
                    className={`flex items-center justify-center w-6 h-6 rounded-full border-2 transition-all ${
                      selectedResearchers.includes(researcher.id)
                        ? 'border-[#3b82f6] bg-[#3b82f6]'
                        : 'border-[#e6ddd4] bg-white'
                    }`}
                  >
                    {selectedResearchers.includes(researcher.id) && (
                      <CheckCircle className="h-4 w-4 text-white" />
                    )}
                  </div>
                </div>
              </div>
            ))}
        </div>

        {/* Actions */}
        <div className="flex gap-3 border-t border-[#e6ddd4] pt-6">
          <Button variant="outline" onClick={onClose} className="flex-1" disabled={isSending}>
            Cancel
          </Button>
          <Button
            onClick={handleAssign}
            isLoading={isSending}
            disabled={selectedResearchers.length === 0 || isSending}
            className="flex-1"
            icon={UserPlus}
          >
            Assign {selectedResearchers.length > 0 && `(${selectedResearchers.length})`}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
