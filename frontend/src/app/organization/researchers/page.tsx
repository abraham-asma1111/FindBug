'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Tabs from '@/components/ui/Tabs';

interface Researcher {
  id: string;
  user: {
    username: string;
    email: string;
  };
  reputation_score: number;
  total_reports: number;
  verified_reports: number;
  profile?: {
    experience_years: number;
    skills: string[];
    specializations: string[];
    bio?: string;
  };
}

interface MatchRecommendation {
  researcher: Researcher;
  match_score: number;
  skill_score: number;
  reputation_score: number;
  ai_expertise_score: number;
  reasons: string[];
}

export default function ResearcherManagementPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState<'browse' | 'recommendations'>('browse');
  const [searchQuery, setSearchQuery] = useState('');
  const [minReputation, setMinReputation] = useState('0');
  const [specialization, setSpecialization] = useState('all');

  // Fetch all researchers
  const { data: researchers, isLoading } = useApiQuery<Researcher[]>(
    '/researchers',
    { enabled: !!user }
  );

  // Filter researchers
  const filteredResearchers = researchers?.filter((researcher) => {
    const query = searchQuery.toLowerCase();
    const matchesSearch =
      researcher.user.username.toLowerCase().includes(query) ||
      researcher.user.email.toLowerCase().includes(query);
    
    const matchesReputation = researcher.reputation_score >= parseInt(minReputation);
    
    const matchesSpecialization =
      specialization === 'all' ||
      researcher.profile?.specializations?.includes(specialization);

    return matchesSearch && matchesReputation && matchesSpecialization;
  }) || [];

  const tabs = [
    { id: 'browse', label: 'Browse Researchers' },
    { id: 'recommendations', label: 'AI Red Teaming Matches' },
  ];

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Researcher Management"
          subtitle="Discover and invite security researchers for your engagements"
          navItems={getPortalNavItems(user.role)}
        >
          <div className="space-y-6">
            {/* Info Banner */}
            <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border-purple-200 dark:border-purple-800">
              <div className="flex items-start gap-4">
                <div className="text-4xl">🔍</div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-2">
                    Smart Researcher Matching
                  </h3>
                  <p className="text-sm text-[#6d6760] dark:text-slate-400">
                    Our AI-powered matching algorithm analyzes researcher skills, reputation, past performance, and AI/ML expertise to recommend the best candidates for your AI Red Teaming engagements.
                  </p>
                </div>
              </div>
            </Card>

            {/* Tabs */}
            <Tabs tabs={tabs} activeTab={activeTab} onChange={(tab) => setActiveTab(tab as any)} />

            {/* Browse Tab */}
            {activeTab === 'browse' && (
              <div className="space-y-6">
                {/* Filters */}
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                    Filter Researchers
                  </h3>
                  <div className="grid gap-4 md:grid-cols-3">
                    <Input
                      label="Search"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Username or email..."
                    />
                    <Input
                      label="Min Reputation"
                      type="number"
                      value={minReputation}
                      onChange={(e) => setMinReputation(e.target.value)}
                      placeholder="0"
                    />
                    <Select
                      label="Specialization"
                      value={specialization}
                      onChange={(e) => setSpecialization(e.target.value)}
                    >
                      <option value="all">All Specializations</option>
                      <option value="ai_security">AI Security</option>
                      <option value="ml_security">ML Security</option>
                      <option value="web_security">Web Security</option>
                      <option value="api_security">API Security</option>
                      <option value="mobile_security">Mobile Security</option>
                    </Select>
                  </div>
                </Card>

                {/* Researcher List */}
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                    Available Researchers ({filteredResearchers.length})
                  </h3>
                  {isLoading ? (
                    <div className="flex items-center justify-center py-12">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                    </div>
                  ) : filteredResearchers.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-4xl mb-4">🔍</div>
                      <p className="text-sm text-[#6d6760] dark:text-slate-400">
                        No researchers found matching your criteria
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredResearchers.map((researcher) => (
                        <div
                          key={researcher.id}
                          className="p-4 rounded-lg border border-[#e6ddd4] dark:border-gray-700 hover:border-[#7d39c2] dark:hover:border-purple-600 transition-colors"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-bold text-[#2d2a26] dark:text-slate-100">
                                  {researcher.user.username}
                                </h4>
                                <span className="inline-flex items-center rounded-full bg-[#eef7ef] px-3 py-1 text-xs font-semibold text-[#24613a]">
                                  {researcher.reputation_score} Rep
                                </span>
                              </div>
                              <p className="text-sm text-[#6d6760] dark:text-slate-400 mb-3">
                                {researcher.user.email}
                              </p>
                              {researcher.profile?.bio && (
                                <p className="text-sm text-[#6d6760] dark:text-slate-400 mb-3">
                                  {researcher.profile.bio}
                                </p>
                              )}
                              <div className="flex flex-wrap gap-2">
                                {researcher.profile?.specializations?.map((spec) => (
                                  <span
                                    key={spec}
                                    className="inline-flex items-center rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-medium text-[#2d2a26]"
                                  >
                                    {spec.replace(/_/g, ' ')}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-1">
                                {researcher.total_reports} reports
                              </div>
                              <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-3">
                                {researcher.verified_reports} verified
                              </div>
                              <Button size="small">View Profile</Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            )}

            {/* Recommendations Tab */}
            {activeTab === 'recommendations' && (
              <Card className="p-6">
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">🤖</div>
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-2">
                    AI-Powered Matching Coming Soon
                  </h3>
                  <p className="text-sm text-[#6d6760] dark:text-slate-400 mb-6">
                    When you create an AI Red Teaming engagement, our algorithm will automatically recommend the best researchers based on:
                  </p>
                  <div className="max-w-2xl mx-auto text-left space-y-3">
                    {[
                      'AI/ML security expertise and certifications',
                      'Past AI Red Teaming performance and success rate',
                      'Reputation score and verified findings',
                      'Specialization in your model type (LLM, AI Agent, etc.)',
                      'Availability and current workload',
                      'Communication skills and responsiveness',
                    ].map((item, idx) => (
                      <div key={idx} className="flex items-start gap-3">
                        <span className="text-purple-600">✓</span>
                        <span className="text-sm text-[#6d6760] dark:text-slate-400">{item}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-8">
                    <Button onClick={() => window.location.href = '/organization/ai-red-teaming'}>
                      Create AI Red Teaming Engagement
                    </Button>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
