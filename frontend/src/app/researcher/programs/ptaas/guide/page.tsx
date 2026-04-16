'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { useRouter } from 'next/navigation';

export default function PTaaSGuidePage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();

  const phases = [
    {
      phase: 'Phase 1: Discovery & Access',
      icon: '🔍',
      color: 'from-blue-500 to-blue-600',
      steps: [
        {
          step: 1,
          title: 'Engagement Discovery',
          description: 'View assigned PTaaS engagements with requirements and scope preview',
          items: ['Available PTaaS engagements', 'Requirements', 'Scope preview']
        },
        {
          step: 2,
          title: 'Access Control',
          description: 'Accept engagement assignment and review rules',
          items: ['Accept assignment', 'Review NDA', 'Acknowledge testing rules']
        },
        {
          step: 3,
          title: 'Engagement Dashboard',
          description: 'Access your testing workspace with all engagement details',
          items: ['Scope details', 'Target assets', 'Testing rules', 'Active reports']
        }
      ]
    },
    {
      phase: 'Phase 2: Testing',
      icon: '🛠️',
      color: 'from-purple-500 to-purple-600',
      steps: [
        {
          step: 4,
          title: 'Structured Testing Approach',
          description: 'Follow methodology-based testing framework',
          items: ['Reconnaissance', 'Scanning', 'Exploitation', 'Validation']
        },
        {
          step: 5,
          title: 'Collaboration',
          description: 'Work with team members on testing activities',
          items: ['Team-based testing', 'Shared notes', 'Progress updates']
        },
        {
          step: 6,
          title: 'Report Submission',
          description: 'Submit findings with comprehensive details',
          items: ['Title & Severity', 'Steps to reproduce', 'Impact analysis', 'Proof of Concept', 'Attachments']
        },
        {
          step: 7,
          title: 'Real-Time Feedback',
          description: 'Receive updates and communicate with organization',
          items: ['Triage updates', 'Chat with organization', 'Clarification requests']
        },
        {
          step: 8,
          title: 'Retesting Phase',
          description: 'Validate fixes and update report status',
          items: ['Validate fixes', 'Update report', 'Confirm resolution']
        }
      ]
    },
    {
      phase: 'Phase 3: Reputation & Earnings',
      icon: '💰',
      color: 'from-green-500 to-green-600',
      steps: [
        {
          step: 9,
          title: 'Scoring System',
          description: 'Earn reputation points based on finding quality',
          items: ['Points per valid finding', 'Accuracy rate', 'Severity weight']
        },
        {
          step: 10,
          title: 'Payment',
          description: 'Receive compensation for completed engagements',
          items: ['Fixed payout', 'Bonus rewards', 'Performance incentives']
        }
      ]
    }
  ];

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="PTaaS Researcher Guide"
          subtitle="Complete workflow for penetration testing engagements"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-8">
            {/* Back Button */}
            <Button
              variant="outline"
              onClick={() => router.push('/researcher/programs/ptaas')}
            >
              ← Back to PTaaS Engagements
            </Button>

            {/* Introduction */}
            <Card>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                Researcher PTaaS Workflow
              </h2>
              <p className="text-slate-600 dark:text-gray-300 leading-relaxed">
                This guide outlines the complete workflow for researchers participating in Penetration Testing as a Service (PTaaS) engagements. 
                Follow these phases to successfully complete engagements, submit high-quality findings, and earn reputation points.
              </p>
            </Card>

            {/* Phases */}
            {phases.map((phase, phaseIdx) => (
              <Card key={phaseIdx}>
                <div className="flex items-center gap-3 mb-6">
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${phase.color} flex items-center justify-center text-2xl`}>
                    {phase.icon}
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                    {phase.phase}
                  </h3>
                </div>

                <div className="space-y-6">
                  {phase.steps.map((step, stepIdx) => (
                    <div key={stepIdx} className="flex gap-4">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-sm">
                          {step.step}
                        </div>
                      </div>
                      <div className="flex-1">
                        <h4 className="font-bold text-slate-900 dark:text-white mb-1">
                          Step {step.step}: {step.title}
                        </h4>
                        <p className="text-sm text-slate-600 dark:text-gray-400 mb-3">
                          {step.description}
                        </p>
                        <ul className="space-y-1">
                          {step.items.map((item, itemIdx) => (
                            <li key={itemIdx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-gray-300">
                              <span className="text-blue-500 mt-1">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            ))}

            {/* Key Differences from Bug Bounty */}
            <Card>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                PTaaS vs Bug Bounty
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-bold text-slate-900 dark:text-white mb-2">PTaaS</h4>
                  <ul className="space-y-2 text-sm text-slate-600 dark:text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">✓</span>
                      <span>Structured methodology required</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">✓</span>
                      <span>Fixed timeline and scope</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">✓</span>
                      <span>Team collaboration</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">✓</span>
                      <span>Comprehensive reporting</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">✓</span>
                      <span>Fixed payout + bonuses</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 dark:text-white mb-2">Bug Bounty</h4>
                  <ul className="space-y-2 text-sm text-slate-600 dark:text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400">○</span>
                      <span>Flexible testing approach</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400">○</span>
                      <span>Ongoing programs</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400">○</span>
                      <span>Individual work</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400">○</span>
                      <span>Finding-focused reports</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400">○</span>
                      <span>Per-finding bounties</span>
                    </li>
                  </ul>
                </div>
              </div>
            </Card>

            {/* Call to Action */}
            <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-800">
              <div className="text-center py-6">
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                  Ready to Start?
                </h3>
                <p className="text-slate-600 dark:text-gray-300 mb-4">
                  Once you're assigned to an engagement, you'll see it in your PTaaS dashboard
                </p>
                <Button
                  onClick={() => router.push('/researcher/programs/ptaas')}
                >
                  View My Engagements
                </Button>
              </div>
            </Card>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
