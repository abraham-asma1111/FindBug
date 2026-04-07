'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import EmptyState from '@/components/ui/EmptyState';

export default function ResearcherCodeReviewPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Expert Code Review"
          subtitle="White-box security assessment with direct access to source code. Manual code review for logic vulnerabilities and security flaws."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Code Review Banner */}
            <div className="rounded-2xl bg-gradient-to-r from-green-600 to-green-800 p-8 text-center text-white">
              <div className="text-4xl mb-4">📝</div>
              <h2 className="text-2xl font-bold mb-2">Expert Code Review Engagements</h2>
              <p className="text-white/90 max-w-2xl mx-auto mb-4">
                Deep dive into source code to find logic flaws, security vulnerabilities, and architectural issues.
              </p>
              <span className="inline-block px-4 py-2 bg-white/20 rounded-full text-sm font-semibold">
                🔍 White-Box Security Testing
              </span>
            </div>

            {/* What is Code Review */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">What is Expert Code Review?</h3>
              <p className="text-sm text-[#6d6760] mb-4">
                Expert Code Review is a white-box security assessment where you have direct access to the application's 
                source code. Unlike black-box testing, you can analyze the code logic, data flow, and architecture to 
                find vulnerabilities that are difficult or impossible to detect through external testing.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">👁️</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Full Code Access</h4>
                  <p className="text-sm text-[#6d6760]">
                    Direct access to private repositories. Review source code, configuration files, and dependencies.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">🔍</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Logic Vulnerabilities</h4>
                  <p className="text-sm text-[#6d6760]">
                    Find business logic flaws, race conditions, and architectural issues that can't be found externally.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">📍</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Precise References</h4>
                  <p className="text-sm text-[#6d6760]">
                    Report vulnerabilities with exact file names and line numbers (e.g., src/api/auth.js:142).
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">🛡️</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Secure Access</h4>
                  <p className="text-sm text-[#6d6760]">
                    VPN access, NDA requirements, and strict confidentiality. Code never leaves secure environment.
                  </p>
                </div>
              </div>
            </div>

            {/* What to Look For */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">What to Look For</h3>
              <div className="space-y-3">
                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-bold">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Authentication & Authorization Flaws</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Weak password policies, insecure session management, privilege escalation, missing access controls.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-bold">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Input Validation Issues</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      SQL injection, XSS, command injection, path traversal, unsafe deserialization.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-bold">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Cryptographic Weaknesses</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Weak algorithms, hardcoded keys, improper key storage, insecure random number generation.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-bold">
                    4
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Business Logic Flaws</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Race conditions, state manipulation, workflow bypasses, price manipulation, quantity limits.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-bold">
                    5
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Data Exposure</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Sensitive data in logs, debug endpoints, verbose error messages, exposed API keys.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-bold">
                    6
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Dependency Vulnerabilities</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Outdated libraries, known CVEs, supply chain risks, malicious packages.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Code Review Workflow */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Code Review Workflow</h3>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Assignment & NDA</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Organization assigns you to code review. Sign NDA and confidentiality agreement. Receive secure access credentials.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Repository Access</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Clone private repository via VPN. Review code structure, dependencies, and configuration files.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Manual Code Analysis</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Review code for security issues. Focus on hotspots identified by organization. Use static analysis tools.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    4
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Submit Findings</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Report vulnerabilities with file:line references. Explain attack path and provide remediation advice.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    5
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Verification</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      After fixes, review updated code. Verify vulnerability is properly remediated. Check for new issues.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    6
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Final Report</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Comprehensive security report with all findings, severity ratings, and recommendations.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Empty State */}
            <EmptyState
              icon="📝"
              title="No Active Code Review Engagements"
              description="You're not currently assigned to any code review engagements. Organizations will assign you based on your expertise and availability."
            />

            {/* Required Skills */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Required Skills & Tools</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Programming Languages</h4>
                  <ul className="text-sm text-[#6d6760] space-y-1">
                    <li>• JavaScript/TypeScript</li>
                    <li>• Python</li>
                    <li>• Java/Kotlin</li>
                    <li>• C#/.NET</li>
                    <li>• Go, Rust, PHP</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Security Knowledge</h4>
                  <ul className="text-sm text-[#6d6760] space-y-1">
                    <li>• OWASP Top 10</li>
                    <li>• Secure coding practices</li>
                    <li>• Cryptography basics</li>
                    <li>• Authentication patterns</li>
                    <li>• Threat modeling</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Tools & Frameworks</h4>
                  <ul className="text-sm text-[#6d6760] space-y-1">
                    <li>• Git/GitHub/GitLab</li>
                    <li>• Static analysis (SonarQube, etc.)</li>
                    <li>• IDE security plugins</li>
                    <li>• Dependency scanners</li>
                    <li>• Code search tools</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Best Practices */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Code Review Best Practices</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Start with Hotspots</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Focus on authentication, authorization, payment processing, and data handling first.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Trace Data Flow</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Follow user input from entry point to database. Look for validation gaps.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Check Dependencies</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Review package.json, requirements.txt, pom.xml for outdated or vulnerable libraries.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 items-start">
                  <div className="text-xl">✅</div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Document Attack Paths</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Explain how an attacker would exploit the vulnerability. Include code flow diagram.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
