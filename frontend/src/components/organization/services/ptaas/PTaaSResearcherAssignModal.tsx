'use client';

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useToast } from '@/components/ui/Toast';
import { UserPlus, X, Search } from 'lucide-react';

interface PTaaSResearcherAssignModalProps {
  isOpen: boolean;
  onClose: () => void;
  engagementId: string;
  engagementName: string;
  onSuccess?: () => void;
}

interface Researcher {
  id: string;
  user: {
    username: string;
    email: string;
  };
  reputation_score: number;
  total_reports: number;
  verified_reports: number;
  profile: {
    experience_years: number;
    skills: string[];
    specializations: string[];
    bio?: string;
  };
}

export default function PTaaSResearcherAssignModal({
  isOpen,
  onClose,
  engagementId,
  engagementName,
  onSuccess,
}: PTaaSResearcherAssignModalProps) {
  const { showToast } = useToast();
  const [selectedResearchers, setSelectedResearchers] = useState<string[]>([]);
  const [researcherInput, setResearcherInput] = useState('');

  // Fetch researchers from API
  const { data: researchersData, isLoading: isLoadingResearchers } = useApiQuery({
    endpoint: '/matching/organization/researchers?limit=100',
    queryKey: ['organization-researchers'],
  });

  const availableResearchers: Researcher[] = researchersData || [];

  const assignMutation = useApiMutation(
    `/ptaas/engagements/${engagementId}/assign`,
    'POST',
    {
      onSuccess: () => {
        showToast('Researchers assigned successfully', 'success');
        onClose();
        setSelectedResearchers([]);
        onSuccess?.();
      },
      onError: (error: any) => {
        showToast(error.message || 'Failed to assign researchers', 'error');
      },
    }
  );

  const handleToggleResearcher = (researcherId: string) => {
    setSelectedResearchers(prev =>
      prev.includes(researcherId)
        ? prev.filter(id => id !== researcherId)
        : [...prev, researcherId]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedResearchers.length === 0) {
      showToast('Please select at least one researcher', 'error');
      return;
    }

    assignMutation.mutate({
      researcher_ids: selectedResearchers,
    });
  };

  const filteredResearchers = availableResearchers.filter(r =>
    r.user.username.toLowerCase().includes(researcherInput.toLowerCase()) ||
    r.user.email.toLowerCase().includes(researcherInput.toLowerCase()) ||
    (r.profile.skills && r.profile.skills.some(s => s.toLowerCase().includes(researcherInput.toLowerCase()))) ||
    (r.profile.specializations && r.profile.specializations.some(s => s.toLowerCase().includes(researcherInput.toLowerCase())))
  );

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Assign Researchers">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <p className="text-sm text-[#6b6662] dark:text-[#a39e9a] mb-4">
            Assign researchers to: <span className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">{engagementName}</span>
          </p>
        </div>

        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-[#faf6f1] mb-2">
            Search Researchers
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#8b8177]" />
            <input
              type="text"
              value={researcherInput}
              onChange={(e) => setResearcherInput(e.target.value)}
              placeholder="Search by name, email, or skills..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-[#e6ddd4] dark:border-[#3d3a36] bg-white dark:bg-[#2d2a26] text-[#2d2a26] dark:text-[#faf6f1] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]"
            />
          </div>
        </div>

        {/* Researcher List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-[#faf6f1] mb-2">
            Available Researchers ({isLoadingResearchers ? '...' : filteredResearchers.length})
          </label>
          
          {isLoadingResearchers ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3b82f6] mx-auto" />
              <p className="text-sm text-[#6b6662] dark:text-[#a39e9a] mt-2">Loading researchers...</p>
            </div>
          ) : filteredResearchers.length > 0 ? (
            filteredResearchers.map((researcher) => (
              <div
                key={researcher.id}
                onClick={() => handleToggleResearcher(researcher.id)}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedResearchers.includes(researcher.id)
                    ? 'border-[#3b82f6] bg-blue-50 dark:bg-blue-900/20'
                    : 'border-[#e6ddd4] dark:border-[#3d3a36] hover:border-[#3b82f6]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">
                        {researcher.user.username}
                      </h4>
                      {selectedResearchers.includes(researcher.id) && (
                        <span className="px-2 py-0.5 rounded-full bg-[#3b82f6] text-white text-xs">
                          Selected
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[#8b8177] dark:text-[#a39e9a] mt-0.5">
                      {researcher.user.email}
                    </p>
                    <div className="flex items-center gap-3 mt-1">
                      <p className="text-sm text-[#6b6662] dark:text-[#a39e9a]">
                        Reputation: {researcher.reputation_score?.toLocaleString() || 0}
                      </p>
                      <p className="text-xs text-[#8b8177] dark:text-[#a39e9a]">
                        {researcher.verified_reports || 0} verified reports
                      </p>
                    </div>
                    {researcher.profile.bio && (
                      <p className="text-xs text-[#8b8177] dark:text-[#a39e9a] mt-1 line-clamp-2">
                        {researcher.profile.bio}
                      </p>
                    )}
                    <div className="flex flex-wrap gap-1 mt-2">
                      {researcher.profile.skills && researcher.profile.skills.slice(0, 5).map((skill) => (
                        <span
                          key={skill}
                          className="px-2 py-0.5 rounded bg-[#faf6f1] dark:bg-[#3d3a36] text-xs text-[#2d2a26] dark:text-[#e6ddd4]"
                        >
                          {skill}
                        </span>
                      ))}
                      {researcher.profile.specializations && researcher.profile.specializations.slice(0, 3).map((spec) => (
                        <span
                          key={spec}
                          className="px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-900/20 text-xs text-blue-700 dark:text-blue-300"
                        >
                          {spec}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <input
                    type="checkbox"
                    checked={selectedResearchers.includes(researcher.id)}
                    onChange={() => {}}
                    className="mt-1"
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-[#6b6662] dark:text-[#a39e9a]">
              {researcherInput ? 'No researchers match your search' : 'No researchers available'}
            </div>
          )}
        </div>

        {/* Selected Count */}
        {selectedResearchers.length > 0 && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <p className="text-sm text-blue-900 dark:text-blue-100">
              {selectedResearchers.length} researcher{selectedResearchers.length !== 1 ? 's' : ''} selected
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-[#e6ddd4] dark:border-[#3d3a36]">
          <Button
            type="button"
            onClick={onClose}
            variant="outline"
            disabled={assignMutation.isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={selectedResearchers.length === 0 || assignMutation.isLoading}
            className="bg-[#3b82f6] hover:bg-[#2563eb] text-white"
          >
            {assignMutation.isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Assigning...
              </>
            ) : (
              <>
                <UserPlus className="h-4 w-4 mr-2" />
                Assign {selectedResearchers.length > 0 && `(${selectedResearchers.length})`}
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
