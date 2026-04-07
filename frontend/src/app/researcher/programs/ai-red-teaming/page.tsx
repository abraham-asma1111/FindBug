'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import EmptyState from '@/components/ui/EmptyState';

export default function ResearcherAIRedTeamingPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="AI Red Teaming"
          subtitle="Specialized security testing for AI systems, LLMs, and machine learning models. Invitation-only for vetted AI security experts."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Invitation-Only Banner */}
            <div className="rounded-2xl bg-gradient-to-r from-purple-600 to-purple-800 p-8 text-center text-white">
              <div className="text-4xl mb-4">🤖</div>
              <h2 className="text-2xl font-bold mb-2">AI Red Teaming Engagements</h2>
              <p className="text-white/90 max-w-2xl mx-auto mb-4">
                Test AI systems for safety, security, and policy violations. Requires proven expertise in AI/ML security.
              </p>
              <span className="inline-block px-4 py-2 bg-white/20 rounded-full text-sm font-semibold">
                🔒 Invitation-Only Program
              </span>
            </div>

            {/* What Makes AI Red Teaming Different */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">What Makes AI Red Teaming Different?</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">🎯</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Behavioral Testing</h4>
                  <p className="text-sm text-[#6d6760]">
                    Focus on AI behavior and policy violations, not just technical bugs. Test for harmful outputs, bias, and safety failures.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">🔄</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Probabilistic Nature</h4>
                  <p className="text-sm text-[#6d6760]">
                    AI models don't always give the same output. Report success rates (e.g., "works 60% of the time") instead of binary pass/fail.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">💬</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Chat Transcripts</h4>
                  <p className="text-sm text-[#6d6760]">
                    Submit full conversation context, not just code snippets. Include prompts, model responses, and attack techniques used.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">🛡️</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Safety Policies</h4>
                  <p className="text-sm text-[#6d6760]">
                    Test against organization-defined safety policies. Each engagement has specific "in-scope harms" to validate.
                  </p>
                </div>
              </div>
            </div>

            {/* Attack Types */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Common Attack Types</h3>
              <div className="space-y-3">
                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Prompt Injection</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Inject malicious instructions into user input to override system prompts or safety guardrails.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Jailbreaking</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Use roleplay, hypotheticals, or encoding to bypass content filters and safety restrictions.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Data Leakage</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Extract training data, system prompts, or sensitive information the model shouldn't reveal.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                    4
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Model Inversion</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Reverse-engineer model behavior to infer training data or internal logic.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                    5
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Bias & Fairness</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Identify discriminatory outputs, stereotyping, or unfair treatment of protected groups.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                    6
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Excessive Agency</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Test if AI agents perform unauthorized actions or exceed their intended scope.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* How to Get Invited */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">How to Get Invited</h3>
              <div className="space-y-4">
                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Build Your Reputation</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Demonstrate expertise in regular bug bounty programs. High-quality reports and good reputation increase your chances.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Show AI/ML Knowledge</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Publish research, blog posts, or talks about AI security. Contribute to AI safety communities.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Complete Profile</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Update your profile with relevant skills, certifications, and experience in AI/ML security testing.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Wait for Invitation</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Organizations will invite you directly when they need AI security specialists. You'll receive a notification.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Empty State */}
            <EmptyState
              icon="🔒"
              title="No Active Invitations"
              description="You don't have any AI Red Teaming invitations yet. Build your reputation and showcase your AI/ML security expertise to get invited!"
            />

            {/* Required Skills */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Required Skills & Knowledge</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Technical Skills</h4>
                  <ul className="text-sm text-[#6d6760] space-y-1">
                    <li>• LLM architecture understanding</li>
                    <li>• Prompt engineering</li>
                    <li>• NLP fundamentals</li>
                    <li>• API testing</li>
                    <li>• Python/scripting</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Security Knowledge</h4>
                  <ul className="text-sm text-[#6d6760] space-y-1">
                    <li>• OWASP LLM Top 10</li>
                    <li>• Adversarial ML</li>
                    <li>• Model security</li>
                    <li>• Data privacy</li>
                    <li>• Threat modeling</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Soft Skills</h4>
                  <ul className="text-sm text-[#6d6760] space-y-1">
                    <li>• Clear communication</li>
                    <li>• Ethical testing</li>
                    <li>• Detailed documentation</li>
                    <li>• Creative thinking</li>
                    <li>• Patience & persistence</li>
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
