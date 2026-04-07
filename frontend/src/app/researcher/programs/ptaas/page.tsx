'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import EmptyState from '@/components/ui/EmptyState';

export default function ResearcherPTaaSPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="PTaaS Engagements"
          subtitle="Penetration Testing as a Service - Structured, methodology-driven security assessments for compliance and comprehensive coverage."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* PTaaS Banner */}
            <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-blue-800 p-8 text-center text-white">
              <div className="text-4xl mb-4">🔒</div>
              <h2 className="text-2xl font-bold mb-2">Penetration Testing as a Service</h2>
              <p className="text-white/90 max-w-2xl mx-auto mb-4">
                Structured security assessments following industry-standard methodologies. Perfect for compliance requirements.
              </p>
              <span className="inline-block px-4 py-2 bg-white/20 rounded-full text-sm font-semibold">
                📋 Methodology-Driven Testing
              </span>
            </div>

            {/* What is PTaaS */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">What is PTaaS?</h3>
              <p className="text-sm text-[#6d6760] mb-4">
                PTaaS (Penetration Testing as a Service) is a structured security assessment where you follow a specific methodology 
                to test an organization's systems. Unlike bug bounty where you find any vulnerability, PTaaS requires you to:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">✅</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Follow a Checklist</h4>
                  <p className="text-sm text-[#6d6760]">
                    Complete all items in the methodology (OWASP, PCI-DSS, SOC2). Mark each as Pass or Fail.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">📝</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Report Negative Findings</h4>
                  <p className="text-sm text-[#6d6760]">
                    Document what you tested and found secure. Proof of thorough testing is required.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">⏱️</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Fixed Timeline</h4>
                  <p className="text-sm text-[#6d6760]">
                    Complete testing within agreed timeframe (usually 1-4 weeks). Track progress in real-time.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="text-2xl mb-2">💰</div>
                  <h4 className="font-semibold text-[#2d2a26] mb-2">Fixed Fee</h4>
                  <p className="text-sm text-[#6d6760]">
                    Get paid a project fee, not per bug. Additional bonuses for critical findings.
                  </p>
                </div>
              </div>
            </div>

            {/* Methodology Types */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Common Methodologies</h3>
              <div className="space-y-4">
                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                      1
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-[#2d2a26]">OWASP Top 10</h4>
                      <p className="text-sm text-[#6d6760] mt-1">
                        Test for the most critical web application security risks: Injection, Broken Authentication, 
                        Sensitive Data Exposure, XXE, Broken Access Control, Security Misconfiguration, XSS, 
                        Insecure Deserialization, Using Components with Known Vulnerabilities, Insufficient Logging.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                      2
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-[#2d2a26]">PCI-DSS</h4>
                      <p className="text-sm text-[#6d6760] mt-1">
                        Payment Card Industry Data Security Standard testing. Required for organizations handling 
                        credit card data. Covers network security, access control, encryption, and monitoring.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                      3
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-[#2d2a26]">SOC 2</h4>
                      <p className="text-sm text-[#6d6760] mt-1">
                        Service Organization Control 2 assessment. Tests security, availability, processing integrity, 
                        confidentiality, and privacy controls. Required for SaaS companies.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                      4
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-[#2d2a26]">NIST Cybersecurity Framework</h4>
                      <p className="text-sm text-[#6d6760] mt-1">
                        Comprehensive framework covering Identify, Protect, Detect, Respond, and Recover functions. 
                        Used by government and enterprise organizations.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* PTaaS Workflow */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">PTaaS Engagement Workflow</h3>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Assignment</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Organization assigns you to a PTaaS engagement. You receive scope, methodology, and timeline.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Reconnaissance</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Gather information about the target. Map attack surface, identify technologies, enumerate assets.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Systematic Testing</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Follow the methodology checklist. Test each item thoroughly. Mark as Pass (secure) or Fail (vulnerable).
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    4
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Document Findings</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Submit detailed reports for vulnerabilities. Include negative findings (what you tested and found secure).
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    5
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Retest & Verify</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      After organization fixes vulnerabilities, retest to confirm remediation. Update findings status.
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
                      Platform generates executive PDF report with all findings, methodology coverage, and attestation letter.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Empty State */}
            <EmptyState
              icon="🔒"
              title="No Active PTaaS Engagements"
              description="You're not currently assigned to any PTaaS engagements. Organizations will assign you based on your skills and availability."
            />

            {/* Requirements */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Requirements for PTaaS</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-3">Technical Skills</h4>
                  <ul className="text-sm text-[#6d6760] space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Web application security testing</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Network penetration testing</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>API security assessment</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Mobile app security</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Cloud security (AWS, Azure, GCP)</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-[#2d2a26] mb-3">Professional Skills</h4>
                  <ul className="text-sm text-[#6d6760] space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Methodology knowledge (OWASP, NIST)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Professional report writing</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Time management & deadlines</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Clear communication</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>Compliance understanding</span>
                    </li>
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
