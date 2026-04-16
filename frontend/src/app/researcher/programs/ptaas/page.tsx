'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import EmptyState from '@/components/ui/EmptyState';
import Button from '@/components/ui/Button';
import ResearcherPTaaSEngagementList from '@/components/researcher/ptaas/ResearcherPTaaSEngagementList';


export default function ResearcherPTaaSPage() {
  const user = useAuthStore((state) => state.user);
  const [expandedFeature, setExpandedFeature] = useState<string | null>(null);
  const [showEngagements, setShowEngagements] = useState(false);

  // If user wants to see engagements, show the list
  if (showEngagements) {
    return (
      <ProtectedRoute allowedRoles={['researcher']}>
        {user ? (
          <PortalShell
            user={user}
            title="Penetration Testing as a Service"
            subtitle="Your assigned PTaaS engagements and testing workspace"
            navItems={getPortalNavItems(user.role)}
            headerAlign="left"
            eyebrowText="Researcher Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
          >
            <div className="space-y-6">
              <Button
                variant="outline"
                onClick={() => setShowEngagements(false)}
              >
                ← Back to PTaaS Information
              </Button>
              <ResearcherPTaaSEngagementList />
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  const features = [
    {
      id: 'methodologies',
      title: 'Structured Methodologies',
      summary: 'Follow industry-standard frameworks including OWASP, PTES, or NIST SP 800-115. Each methodology comes with auto-generated phase checklists, progress tracking, and milestone management to ensure comprehensive coverage.',
      details: [
        {
          name: 'OWASP Testing Guide',
          description: 'Comprehensive web application security testing methodology covering the OWASP Top 10 and beyond.',
          phases: ['Information Gathering', 'Configuration Testing', 'Identity Management', 'Authentication', 'Authorization', 'Session Management', 'Input Validation', 'Error Handling', 'Cryptography', 'Business Logic', 'Client-Side Testing']
        },
        {
          name: 'PTES (Penetration Testing Execution Standard)',
          description: 'Complete penetration testing framework from pre-engagement to reporting.',
          phases: ['Pre-engagement Interactions', 'Intelligence Gathering', 'Threat Modeling', 'Vulnerability Analysis', 'Exploitation', 'Post Exploitation', 'Reporting']
        },
        {
          name: 'NIST SP 800-115',
          description: 'Technical guide to information security testing and assessment from NIST.',
          phases: ['Planning', 'Discovery', 'Attack & Penetration', 'Reporting', 'Compliance Validation']
        },
        {
          name: 'Custom Methodology',
          description: 'Tailored testing approach combining multiple frameworks for specialized requirements.',
          phases: ['Requirement Analysis', 'Custom Phase Definition', 'Hybrid Testing Approach', 'Specialized Assessments']
        }
      ]
    },
    {
      id: 'findings',
      title: 'Real-Time Findings',
      summary: 'Submit security findings with CVSS scores as you discover them during testing. Platform triage specialists validate each finding, adjust priorities based on business impact, and ensure quality before delivery to organizations.',
      details: [
        {
          name: 'Finding Submission',
          description: 'Structured templates ensure consistent, high-quality vulnerability reports.',
          phases: ['Title & Description', 'CVSS Score Calculation', 'Affected Components', 'Reproduction Steps', 'Proof of Concept', 'Evidence Attachments']
        },
        {
          name: 'Platform Triage',
          description: 'Expert validation ensures finding accuracy and appropriate severity classification.',
          phases: ['Initial Review', 'Severity Validation', 'Priority Adjustment', 'Business Impact Analysis', 'Quality Assurance', 'Organization Notification']
        },
        {
          name: 'CVSS Scoring',
          description: 'Industry-standard vulnerability scoring for consistent risk assessment.',
          phases: ['Base Score Metrics', 'Temporal Metrics', 'Environmental Metrics', 'Severity Classification', 'Risk Rating']
        }
      ]
    },
    {
      id: 'reports',
      title: 'Compliance Reports',
      summary: 'Auto-generated executive reports designed for compliance requirements. Includes executive summary, risk ratings, evidence documentation, and detailed remediation guidance suitable for audit and regulatory purposes.',
      details: [
        {
          name: 'Executive Summary',
          description: 'High-level overview for C-level executives and board members.',
          phases: ['Engagement Overview', 'Key Findings Summary', 'Risk Assessment', 'Business Impact', 'Strategic Recommendations', 'Compliance Status']
        },
        {
          name: 'Technical Report',
          description: 'Detailed technical findings for security and development teams.',
          phases: ['Methodology Used', 'Scope Coverage', 'Detailed Findings', 'Evidence & PoC', 'Technical Remediation', 'Verification Steps']
        },
        {
          name: 'Compliance Documentation',
          description: 'Audit-ready reports for regulatory and compliance requirements.',
          phases: ['Standards Mapping', 'Control Assessment', 'Gap Analysis', 'Remediation Timeline', 'Compliance Certification', 'Audit Trail']
        }
      ]
    },
    {
      id: 'pricing',
      title: 'Flexible Pricing',
      summary: 'Choose between fixed-price engagements for one-time assessments or subscription-based models for continuous testing. All engagements include a free retesting period to verify fixes and ensure vulnerabilities are properly remediated.',
      details: [
        {
          name: 'Fixed-Price Engagements',
          description: 'One-time penetration tests with defined scope and deliverables.',
          phases: ['Scope Definition', 'Resource Allocation', 'Testing Period', 'Report Delivery', 'Free Retest Window', 'Final Verification']
        },
        {
          name: 'Subscription Model',
          description: 'Continuous security testing with recurring assessments.',
          phases: ['Monthly/Quarterly Testing', 'Ongoing Monitoring', 'Continuous Retesting', 'Regular Reporting', 'Trend Analysis', 'Security Posture Tracking']
        },
        {
          name: 'Retest Policy',
          description: 'Free retesting period to verify vulnerability remediation.',
          phases: ['Eligibility Check', 'Retest Request', 'Assignment', 'Verification Testing', 'Status Update', 'Final Confirmation']
        }
      ]
    }
  ];

  const methodologies = [
    {
      id: 'owasp',
      name: 'OWASP Testing',
      description: 'The OWASP Web Security Testing Guide (WSTG) is a premier open-source framework used by security professionals and developers to systematically test the security of web applications. It provides a comprehensive set of best practices, tools, and methodologies that can be integrated into every stage of the software development lifecycle (SDLC).\n\nCore Testing Framework (SDLC Alignment): The OWASP Testing Framework moves security testing beyond just the final production phase, advocating for activities across five key phases:\n\n1. Before Development Begins (Define security requirements and developer training)\n\n2. During Definition and Design (Perform threat modeling and review security architecture)\n\n3. During Development (Conduct code reviews and unit testing for security controls)\n\n4. During Deployment (Execute penetration tests and check for configuration errors)\n\n5. During Maintenance and Operations (Continuously monitor for new vulnerabilities and perform periodic audits)',
      image: '/images/owasp.png'
    },
    {
      id: 'ptes',
      name: 'PTES Methodology',
      description: 'The Penetration Testing Execution Standard (PTES) is a comprehensive, seven-phase framework designed to standardize penetration testing, ensuring consistent, high-quality, and thorough security assessments. It covers the entire engagement lifecycle, from initial planning and scoping to intelligence gathering, threat modeling, vulnerability analysis, exploitation, post-exploitation, and final reporting.\n\nThe Seven Phases of PTES:\n\n1. Pre-engagement Interactions: Define scope, rules of engagement, legal authorization, and communication channels.\n\n2. Intelligence Gathering: Collect target data including IP addresses, domain information, and employee details using OSINT.\n\n3. Threat Modeling: Analyze intel to identify potential attackers, their capabilities, and target assets.\n\n4. Vulnerability Analysis: Identify security flaws using automated scanners and manual methods, validating to reduce false positives.\n\n5. Exploitation: Actively exploit validated vulnerabilities to gain unauthorized access and prove impact.\n\n6. Post-Exploitation: Assess compromised systems, maintain access, and attempt lateral movement to higher-value targets.\n\n7. Reporting: Deliver comprehensive report with executive summary, detailed findings, risk ratings, and remediation recommendations.',
      image: '/images/ptes.png'
    },
    {
      id: 'nist',
      name: 'NIST Framework',
      description: 'NIST SP 800-115 is a foundational technical guide for conducting information security assessments, outlining methodologies for testing and assessing network security. It defines structured, repeatable phases—planning, discovery, attack, and reporting—to identify, validate, and remediate vulnerabilities, ensuring compliance and improving security posture.\n\nCore Components of NIST SP 800-115 Testing:\n\n1. Security Assessment Planning: Sets the scope, goals, rules of engagement, and legal/logistical requirements (e.g., timing, data protection).\n\n2. Discovery (Information Gathering): Identifies targets and their characteristics through network scanning, port scanning, and vulnerability scans.\n\n3. Attack (Vulnerability Validation): Validates identified vulnerabilities through penetration testing, password cracking, and social engineering to confirm risks.\n\n4. Reporting & Post-Testing: Delivers a detailed report on findings, recommendations, and evidence, followed by remediation actions and validation.',
      image: '/images/nist.png'
    },
    {
      id: 'custom',
      name: 'Custom Methodology',
      description: 'A custom methodology based on NIST SP 800-115 allows you to move beyond a generic checklist to a risk-based approach tailored to your specific infrastructure, compliance needs, and threat profile. By selecting and combining specific techniques, you can focus resources on the most critical assets.\n\nCore Tailoring Factors:\n\nWhen customizing your approach, NIST SP 800-115 suggests evaluating these key variables:\n\n1. Asset Criticality: Prioritize high-impact systems (e.g., those holding PII or critical financial data) for more intensive testing, such as manual penetration testing rather than just automated scans.\n\n2. Resource Constraints: Balance depth with reality by considering available staff expertise, time, and budget for hardware/software tools.\n\n3. Compliance Requirements: Align testing with specific frameworks like HIPAA, PCI DSS, or SOC 2 by focusing on the controls those standards demand.\n\n4. Operational Risk: Tailor the Rules of Engagement (ROE) to protect production systems, establishing clear boundaries for non-destructive testing if uptime is critical.',
      image: '/images/custom.png'
    }
  ];

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Penetration Testing as a Service"
          subtitle="Comprehensive security testing with structured methodologies. Simulate real-world attacks to identify vulnerabilities."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Hero Banner with Background Image */}
            <div className="relative w-full overflow-hidden rounded-2xl h-[600px]">
              {/* Background Image - Full Width */}
              <img 
                src="/images/ptaas-hero.png" 
                alt="Penetration Testing as a Service" 
                className="absolute inset-0 w-full h-full object-cover"
              />
              
              {/* Overlay for text readability */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
              
              {/* Content - Bottom Center */}
              <div className="relative z-10 h-full flex items-end justify-center pb-6">
                <div className="text-center px-8">
                  <h1 className="text-7xl font-black text-white drop-shadow-2xl mb-6">
                    PENETRATION TESTING
                  </h1>
                  <h2 className="text-4xl font-bold text-white drop-shadow-2xl">
                    Professional pentesting <span className="text-blue-400">on demand</span>
                  </h2>
                </div>
              </div>
            </div>

            {/* Quick Access Button */}
            <div className="flex justify-center">
              <Button
                onClick={() => setShowEngagements(true)}
                className="px-8 py-4 text-lg"
              >
                🚀 View My PTaaS Engagements
              </Button>
            </div>

            {/* What is PTaaS */}
            <div className="rounded-2xl bg-white dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6">
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4 text-center">What is Penetration Testing as a Service?</h3>
              <p className="text-base text-slate-600 dark:text-gray-300 mb-6 text-center">
                PTaaS is a comprehensive security testing service where you simulate real-world attacks against an organization's 
                systems, applications, and infrastructure. The platform provides structured workflows, real-time collaboration, 
                and automated triage to ensure high-quality security assessments.
              </p>
              <div className="w-full">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {features.map((feature) => (
                    <div
                      key={feature.id}
                      className={`transition-all duration-300 ${
                        expandedFeature === feature.id ? 'md:col-span-2' : ''
                      }`}
                    >
                      <button
                        onClick={() => setExpandedFeature(expandedFeature === feature.id ? null : feature.id)}
                        className={`w-full rounded-lg bg-white dark:bg-[#111111] p-6 border transition-all duration-300 text-left min-h-[180px] ${
                          expandedFeature === feature.id
                            ? 'border-blue-500 dark:border-blue-500 shadow-xl'
                            : 'border-slate-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:shadow-lg'
                        }`}
                      >
                    <div className="flex items-start justify-between mb-4">
                      <h4 className="text-2xl font-bold text-slate-900 dark:text-white">{feature.title}</h4>
                      <span className={`text-blue-500 transition-transform duration-300 ml-3 flex-shrink-0 text-xl ${expandedFeature === feature.id ? 'rotate-180' : ''}`}>
                        ▼
                      </span>
                    </div>
                    <p className="text-base text-slate-600 dark:text-gray-300 mb-0 leading-relaxed">
                      {feature.summary}
                    </p>
                    
                    {expandedFeature === feature.id && (
                      <div className="mt-3 pt-3 border-t border-slate-200 dark:border-gray-700 space-y-3">
                        {feature.details.map((detail, idx) => (
                          <div key={idx} className="space-y-2">
                            <h5 className="font-bold text-slate-900 dark:text-white text-xl">{detail.name}</h5>
                            <p className="text-base text-slate-600 dark:text-gray-300 leading-relaxed mb-2">{detail.description}</p>
                            <div className="bg-slate-50 dark:bg-black/50 rounded p-3">
                              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                                {detail.phases.map((phase, phaseIdx) => (
                                  <div key={phaseIdx} className="flex items-start gap-2">
                                    <span className="text-blue-500 text-base">•</span>
                                    <span className="text-base text-slate-600 dark:text-gray-300 leading-snug">{phase}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Testing Methodologies */}
            <div className="rounded-2xl bg-white dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6">
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4 text-center">Testing Methodologies</h3>
              <p className="text-base text-slate-600 dark:text-gray-300 mb-6 text-center">
                Industry-standard frameworks for comprehensive security testing
              </p>
              <div className="w-full">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {methodologies.map((methodology) => (
                  <div key={methodology.id} className="space-y-3 p-6 rounded-lg border border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-black/30">
                    <div>
                      <h4 className="font-bold text-slate-900 dark:text-white text-2xl mb-3" style={{ fontFamily: 'Times New Roman, serif' }}>{methodology.name}</h4>
                      <p className="text-slate-600 dark:text-gray-300 text-lg whitespace-pre-line" style={{ fontFamily: 'Times New Roman, serif', lineHeight: '1.5' }}>{methodology.description}</p>
                    </div>
                  </div>
                ))}
              </div>
              </div>
            </div>

            {/* PTaaS Engagement Workflow */}
            <div className="rounded-2xl bg-white dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">PTaaS Engagement Workflow</h3>
              <div className="relative">
                {/* Vertical line */}
                <div className="absolute left-4 top-8 bottom-8 w-0.5 bg-gradient-to-b from-blue-500 to-blue-300"></div>
                
                <div className="space-y-6">
                  {[
                    { step: 1, title: 'Engagement Creation', desc: 'Organization creates engagement with scope, methodology (OWASP/PTES/NIST), deliverables, and pricing model (fixed/subscription).' },
                    { step: 2, title: 'Researcher Assignment', desc: 'Platform matches and assigns qualified researchers based on skills, reputation, and availability. Team collaboration begins.' },
                    { step: 3, title: 'Testing Phases', desc: 'Execute testing following methodology checklist. Track progress through dashboard. Submit findings with CVSS scores in real-time.' },
                    { step: 4, title: 'Triage & Validation', desc: 'Platform triage specialists validate findings. Prioritize based on severity and business impact. Generate compliance reports.' },
                    { step: 5, title: 'Deliverable Submission', desc: 'Submit required deliverables (executive report, technical findings, remediation guide). Organization reviews and approves.' },
                    { step: 6, title: 'Retest Workflow', desc: 'Organization requests free retests within eligibility period. Verify fixes and update finding status. Complete engagement.' }
                  ].map((item) => (
                    <div key={item.step} className="flex gap-4 relative">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-lg z-10">
                        {item.step}
                      </div>
                      <div className="flex-1 pb-2">
                        <h4 className="font-bold text-slate-900 dark:text-white">{item.title}</h4>
                        <p className="text-sm text-slate-600 dark:text-gray-300 mt-1">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Empty State */}
            <EmptyState
              icon="🔒"
              title="No Active PTaaS Engagements"
              description="You're not currently assigned to any penetration testing engagements. Organizations will assign you based on your expertise and certifications."
            />
          </div>

          {/* Key Platform Features - Gradient background, no gap, full width */}
          <div className="bg-gradient-to-r from-[#1a1d2e] via-[#1e2139] to-[#3d2645] dark:bg-gradient-to-r dark:from-[#1a1d2e] dark:via-[#1e2139] dark:to-[#3d2645] py-24 px-6">
            <div className="max-w-6xl mx-auto">
              <h3 className="text-3xl font-bold text-white mb-12 tracking-tight" style={{ marginLeft: '350px' }}>Platform Features</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                <div className="group">
                  <h4 className="font-semibold text-white mb-4 text-2xl tracking-tight">Real-Time Dashboard</h4>
                  <p className="text-lg text-gray-400 leading-relaxed">
                    Track testing phases, methodology checklists, findings, and team collaboration updates in real-time.
                  </p>
                </div>

                <div className="group">
                  <h4 className="font-semibold text-white mb-4 text-2xl tracking-tight">Triage & Validation</h4>
                  <p className="text-lg text-gray-400 leading-relaxed">
                    Platform specialists validate findings, adjust priorities, and generate compliance-ready executive reports.
                  </p>
                </div>

                <div className="group">
                  <h4 className="font-semibold text-white mb-4 text-2xl tracking-tight">Free Retest Period</h4>
                  <p className="text-lg text-gray-400 leading-relaxed">
                    Organizations can request free retests within eligibility period. Verify fixes and track retest statistics.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Requirements - Light background, no gap, full width */}
          <div className="bg-[#f5f5f5] dark:bg-[#1a1a1a] py-16 px-6">
              <div className="max-w-6xl mx-auto">
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-10 text-left" style={{ marginLeft: '370px' }}>Requirements & Skills</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white text-xl mb-6">Certifications</h4>
                    <ul className="space-y-3">
                      {['OSCP, CEH, or equivalent', 'OWASP certification', 'Cloud security certs', 'Network+ or Security+', 'Specialized domain certs'].map((skill, idx) => (
                        <li key={idx} className="flex items-start gap-3 text-base text-slate-600 dark:text-gray-300">
                          <span className="text-blue-500 text-lg">•</span>
                          <span>{skill}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white text-xl mb-6">Technical Skills</h4>
                    <ul className="space-y-3">
                      {['Network protocols & services', 'Web application security', 'API security testing', 'Cloud infrastructure', 'Mobile app security'].map((skill, idx) => (
                        <li key={idx} className="flex items-start gap-3 text-base text-slate-600 dark:text-gray-300">
                          <span className="text-blue-500 text-lg">•</span>
                          <span>{skill}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white text-xl mb-6">Tools & Frameworks</h4>
                    <ul className="space-y-3">
                      {['Burp Suite, OWASP ZAP', 'Metasploit, Cobalt Strike', 'Nmap, Nessus, Qualys', 'Custom exploit development', 'Reporting tools'].map((skill, idx) => (
                        <li key={idx} className="flex items-start gap-3 text-base text-slate-600 dark:text-gray-300">
                          <span className="text-blue-500 text-lg">•</span>
                          <span>{skill}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>

          {/* Testing Types - Gradient background from dark purple to pink, no gap, full width */}
          <div className="bg-gradient-to-r from-[#3d1f3f] via-[#8b3a62] to-[#ec4899] py-24 px-6">
            <div className="max-w-6xl mx-auto">
              <h3 className="text-3xl font-bold text-white dark:text-white mb-12 tracking-tight" style={{ marginLeft: '300px' }}>Common Testing Types</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {[
                  { title: 'Web Application', desc: 'Test web apps for OWASP Top 10, business logic flaws, and authentication issues.' },
                  { title: 'API Security', desc: 'Test REST/GraphQL APIs for authorization, injection, and rate limiting issues.' },
                  { title: 'Mobile Application', desc: 'Test iOS/Android apps for insecure storage, weak crypto, and API vulnerabilities.' },
                  { title: 'Cloud Infrastructure', desc: 'Test AWS/Azure/GCP for misconfigurations, IAM issues, and data exposure.' },
                  { title: 'Network Penetration', desc: 'Test internal/external networks for vulnerabilities, weak protocols, and lateral movement.' },
                  { title: 'Wireless Security', desc: 'Test WiFi networks for weak encryption, rogue APs, and authentication bypasses.' }
                ].map((type, idx) => (
                  <div key={idx}>
                    <h4 className="font-semibold text-white dark:text-white mb-2 text-xl">{type.title}</h4>
                    <p className="text-base text-gray-200 dark:text-gray-200 leading-relaxed">{type.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
