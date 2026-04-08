'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import EmptyState from '@/components/ui/EmptyState';


export default function ResearcherAIRedTeamingPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedAttack, setSelectedAttack] = useState<string | null>(null);
  const [expandedConcept, setExpandedConcept] = useState<string | null>(null);

  const concepts = [
    {
      id: 'behavioral',
      title: 'Behavioral Testing',
      summary: 'Focus on AI behavior and policy violations, not just technical bugs. Test for harmful outputs, bias, and safety failures.',
      details: [
        'Unlike traditional security testing that focuses on code vulnerabilities, AI red teaming evaluates how the model behaves in real-world scenarios.',
        'Test for policy violations like generating harmful content, discriminatory outputs, or privacy breaches.',
        'Assess whether the AI follows organizational safety guidelines and ethical standards.',
        'Document behavioral patterns that could lead to reputational or legal risks.'
      ]
    },
    {
      id: 'probabilistic',
      title: 'Probabilistic Nature',
      summary: 'AI models don\'t always give the same output. Report success rates (e.g., "works 60% of the time") instead of binary pass/fail.',
      details: [
        'AI models are non-deterministic - the same input can produce different outputs across multiple attempts.',
        'Report findings with success rates: "This jailbreak works 7 out of 10 times" rather than just "vulnerability found".',
        'Test multiple times with slight variations to understand consistency and reliability of exploits.',
        'Include temperature settings, model versions, and other parameters that affect reproducibility.'
      ]
    },
    {
      id: 'transcripts',
      title: 'Chat Transcripts',
      summary: 'Submit full conversation context, not just code snippets. Include prompts, model responses, and attack techniques used.',
      details: [
        'Provide complete conversation history showing the full attack chain, not just the final exploit.',
        'Include all prompts, model responses, and intermediate steps that led to the vulnerability.',
        'Document the exact phrasing and techniques used - small changes in wording can significantly affect results.',
        'Screenshots or recordings of the interaction help demonstrate the issue clearly.'
      ]
    },
    {
      id: 'policies',
      title: 'Safety Policies',
      summary: 'Test against organization-defined safety policies. Each engagement has specific "in-scope harms" to validate.',
      details: [
        'Each AI red teaming engagement defines specific "in-scope harms" - categories of unsafe behavior to test for.',
        'Common policy areas include: hate speech, violence, illegal activities, privacy violations, and misinformation.',
        'Organizations may have custom policies based on their use case (e.g., medical AI has different safety requirements than chatbots).',
        'Your testing should focus on the defined scope - findings outside scope may not be accepted.'
      ]
    }
  ];

  const attackTypes = [
    {
      id: 'prompt-injection',
      name: 'Prompt Injection',
      description: 'Inject malicious instructions to override system prompts',
      color: 'bg-orange-500',
      borderColor: 'ring-orange-500',
      examples: ['System prompt override', 'Instruction hijacking', 'Context manipulation']
    },
    {
      id: 'jailbreak',
      name: 'Jailbreaking',
      description: 'Bypass content filters and safety restrictions',
      color: 'bg-purple-600',
      borderColor: 'ring-purple-600',
      examples: ['Roleplay scenarios', 'Hypothetical questions', 'Encoding tricks']
    },
    {
      id: 'data-leakage',
      name: 'Data Leakage',
      description: 'Extract training data or sensitive information',
      color: 'bg-yellow-500',
      borderColor: 'ring-yellow-500',
      examples: ['System prompt extraction', 'Training data recovery', 'PII disclosure']
    },
    {
      id: 'model-inversion',
      name: 'Model Inversion',
      description: 'Reverse-engineer model behavior and logic',
      color: 'bg-orange-500',
      borderColor: 'ring-orange-500',
      examples: ['Behavior analysis', 'Logic inference', 'Pattern detection']
    },
    {
      id: 'bias',
      name: 'Bias & Fairness',
      description: 'Identify discriminatory outputs and stereotyping',
      color: 'bg-purple-600',
      borderColor: 'ring-purple-600',
      examples: ['Protected group testing', 'Stereotype detection', 'Fairness validation']
    },
    {
      id: 'excessive-agency',
      name: 'Excessive Agency',
      description: 'Test if AI agents exceed intended scope',
      color: 'bg-yellow-500',
      borderColor: 'ring-yellow-500',
      examples: ['Unauthorized actions', 'Scope violations', 'Permission bypasses']
    }
  ];

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="AI Red Teaming"
          subtitle=""
          navItems={getPortalNavItems(user.role)}
          hideTitle={true}
          hideSubtitle={true}
        >
          <div className="space-y-6">
            {/* Hero Banner with Background Image */}
            <div className="relative w-full overflow-hidden rounded-2xl h-[600px]">
              {/* Background Image - Full Width */}
              <img 
                src="/images/ai-red-teaming-hero.png" 
                alt="AI Red Teaming" 
                className="absolute inset-0 w-full h-full object-cover"
              />
              
              {/* Very light overlay for text readability */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent"></div>
              
              {/* Content - Bottom Center */}
              <div className="relative z-10 h-full flex items-end justify-center pb-12">
                <div className="text-center px-8">
                  <h1 className="text-7xl font-black text-white drop-shadow-2xl mb-4">
                    AI RED TEAMING
                  </h1>
                  <h2 className="text-4xl font-bold text-white drop-shadow-2xl">
                    AI security testing <span className="text-orange-400">for the future</span>
                  </h2>
                </div>
              </div>
            </div>

            {/* What Makes AI Red Teaming Different */}
            <div className="rounded-2xl bg-white dark:bg-[#111111] dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6">
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-6">What Makes AI Red Teaming Different?</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {concepts.map((concept) => (
                  <button
                    key={concept.id}
                    onClick={() => setExpandedConcept(expandedConcept === concept.id ? null : concept.id)}
                    className={`group rounded-xl bg-white dark:bg-[#111111] p-6 border-2 transition-all duration-300 hover:shadow-lg text-left ${
                      expandedConcept === concept.id
                        ? 'border-orange-500 dark:border-orange-500 ring-2 ring-orange-200 dark:ring-orange-900'
                        : 'border-slate-200 dark:border-gray-700 hover:border-orange-500 dark:hover:border-orange-500'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="text-lg font-bold text-slate-900 dark:text-slate-100">{concept.title}</h4>
                      <span className={`text-orange-500 transition-transform duration-300 ${expandedConcept === concept.id ? 'rotate-180' : ''}`}>
                        ▼
                      </span>
                    </div>
                    <p className="text-base text-slate-600 dark:text-slate-400 leading-relaxed mb-3">
                      {concept.summary}
                    </p>
                    {expandedConcept === concept.id && (
                      <div className="mt-4 pt-4 border-t border-slate-200 dark:border-gray-700 space-y-3">
                        {concept.details.map((detail, idx) => (
                          <div key={idx} className="flex items-start gap-2">
                            <span className="text-orange-500 mt-1">•</span>
                            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                              {detail}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Interactive Attack Types */}
            <div className="rounded-2xl bg-white dark:bg-[#111111] dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4 text-center">Common Attack Types</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 text-center">
                Click on an attack type to see example techniques
              </p>
              <div className="flex flex-col items-center gap-8">
                {/* First Row - 3 cards */}
                <div className="flex justify-center gap-8">
                  {attackTypes.slice(0, 3).map((attack) => (
                    <button
                      key={attack.id}
                      onClick={() => setSelectedAttack(selectedAttack === attack.id ? null : attack.id)}
                      className={`
                        rounded-xl p-6 text-left transition-all duration-300 transform hover:scale-105 w-80 min-h-[160px]
                        ${selectedAttack === attack.id 
                          ? `ring-2 ${attack.borderColor} shadow-lg` 
                          : 'hover:shadow-md'
                        }
                        ${attack.color} text-white
                      `}
                    >
                      <h4 className="font-bold mb-3 text-lg">{attack.name}</h4>
                      <p className="text-white text-base leading-relaxed">{attack.description}</p>
                      {selectedAttack === attack.id && (
                        <div className="mt-4 pt-4 border-t border-white/40">
                          <p className="text-sm font-bold mb-3 text-white">Example Techniques:</p>
                          <div className="space-y-2">
                            {attack.examples.map((example, idx) => (
                              <div key={idx} className="text-sm px-3 py-2 bg-white/30 rounded-lg text-white font-semibold shadow-sm">
                                • {example}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
                
                {/* Second Row - 3 cards */}
                <div className="flex justify-center gap-8">
                  {attackTypes.slice(3, 6).map((attack) => (
                    <button
                      key={attack.id}
                      onClick={() => setSelectedAttack(selectedAttack === attack.id ? null : attack.id)}
                      className={`
                        rounded-xl p-6 text-left transition-all duration-300 transform hover:scale-105 w-80 min-h-[160px]
                        ${selectedAttack === attack.id 
                          ? `ring-2 ${attack.borderColor} shadow-lg` 
                          : 'hover:shadow-md'
                        }
                        ${attack.color} text-white
                      `}
                    >
                      <h4 className="font-bold mb-3 text-lg">{attack.name}</h4>
                      <p className="text-white text-base leading-relaxed">{attack.description}</p>
                      {selectedAttack === attack.id && (
                        <div className="mt-4 pt-4 border-t border-white/40">
                          <p className="text-sm font-bold mb-3 text-white">Example Techniques:</p>
                          <div className="space-y-2">
                            {attack.examples.map((example, idx) => (
                              <div key={idx} className="text-sm px-3 py-2 bg-white/30 rounded-lg text-white font-semibold shadow-sm">
                                • {example}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* How to Get Invited */}
            <div className="rounded-2xl bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border border-orange-200 dark:border-orange-800 p-6">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-6">How to Get Invited</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { title: 'Build Your Reputation', desc: 'Demonstrate expertise in regular bug bounty programs. High-quality reports and good reputation increase your chances.' },
                  { title: 'Show AI/ML Knowledge', desc: 'Publish research, blog posts, or talks about AI security. Contribute to AI safety communities.' },
                  { title: 'Complete Profile', desc: 'Update your profile with relevant skills, certifications, and experience in AI/ML security testing.' },
                  { title: 'Wait for Invitation', desc: 'Organizations will invite you directly when they need AI security specialists. You\'ll receive a notification.' }
                ].map((step, idx) => (
                  <div key={idx} className="bg-white dark:bg-[#111111] dark:bg-[#111111] rounded-xl p-5 border border-slate-200 dark:border-gray-700 hover:border-orange-300 dark:hover:border-orange-700 transition-all duration-200 hover:shadow-md">
                    <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-2 text-base">{step.title}</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{step.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Empty State */}
            <EmptyState
              icon="🔒"
              title="No Active Invitations"
              description="You don't have any AI Red Teaming invitations yet. Build your reputation and showcase your AI/ML security expertise to get invited!"
            />

            {/* Required Skills */}
            <div className="rounded-2xl bg-white dark:bg-[#111111] dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-6">Required Skills & Knowledge</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-orange-500 text-white flex items-center justify-center text-xl">
                      💻
                    </div>
                    <h4 className="font-bold text-slate-900 dark:text-slate-100">Technical Skills</h4>
                  </div>
                  <ul className="space-y-2">
                    {['LLM architecture understanding', 'Prompt engineering', 'NLP fundamentals', 'API testing', 'Python/scripting'].map((skill, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <span className="text-orange-500">•</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-orange-500 text-white flex items-center justify-center text-xl">
                      🛡️
                    </div>
                    <h4 className="font-bold text-slate-900 dark:text-slate-100">Security Knowledge</h4>
                  </div>
                  <ul className="space-y-2">
                    {['OWASP LLM Top 10', 'Adversarial ML', 'Model security', 'Data privacy', 'Threat modeling'].map((skill, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <span className="text-orange-500">•</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-orange-500 text-white flex items-center justify-center text-xl">
                      🎯
                    </div>
                    <h4 className="font-bold text-slate-900 dark:text-slate-100">Soft Skills</h4>
                  </div>
                  <ul className="space-y-2">
                    {['Clear communication', 'Ethical testing', 'Detailed documentation', 'Creative thinking', 'Patience & persistence'].map((skill, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <span className="text-orange-500">•</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
