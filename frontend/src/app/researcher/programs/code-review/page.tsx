'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import EmptyState from '@/components/ui/EmptyState';

export default function ResearcherCodeReviewPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const vulnerabilityCategories = [
    {
      id: 'auth',
      name: 'Authentication & Authorization',
      description: 'Access control and identity management flaws',
      color: 'from-orange-500 to-orange-600',
      examples: ['Weak password policies', 'Insecure session management', 'Privilege escalation', 'Missing access controls']
    },
    {
      id: 'input',
      name: 'Input Validation',
      description: 'Injection and data validation issues',
      color: 'from-purple-600 to-purple-700',
      examples: ['SQL injection', 'XSS', 'Command injection', 'Path traversal', 'Unsafe deserialization']
    },
    {
      id: 'crypto',
      name: 'Cryptographic Weaknesses',
      description: 'Encryption and key management issues',
      color: 'from-yellow-500 to-yellow-600',
      examples: ['Weak algorithms', 'Hardcoded keys', 'Improper key storage', 'Insecure RNG']
    },
    {
      id: 'logic',
      name: 'Business Logic Flaws',
      description: 'Application workflow and state issues',
      color: 'from-orange-500 to-orange-600',
      examples: ['Race conditions', 'State manipulation', 'Workflow bypasses', 'Price manipulation']
    },
    {
      id: 'data',
      name: 'Data Exposure',
      description: 'Information disclosure vulnerabilities',
      color: 'from-purple-600 to-purple-700',
      examples: ['Sensitive data in logs', 'Debug endpoints', 'Verbose errors', 'Exposed API keys']
    },
    {
      id: 'deps',
      name: 'Dependency Vulnerabilities',
      description: 'Third-party library and supply chain risks',
      color: 'from-yellow-500 to-yellow-600',
      examples: ['Outdated libraries', 'Known CVEs', 'Supply chain risks', 'Malicious packages']
    }
  ];

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
          {/* Hero Banner with Background Image - No gap at top, minimal side gaps */}
          <div className="relative w-full overflow-hidden h-[600px] -mt-6 -mx-4">
            <img 
              src="/images/%20expert%20code%20review%20.png" 
              alt="Expert Code Review" 
              className="absolute inset-0 w-full h-full object-cover"
            />
            
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
            
            <div className="relative z-10 h-full flex items-end justify-center pb-6">
              <div className="text-center px-8">
                <h1 className="text-7xl font-black text-white drop-shadow-2xl mb-6">
                  EXPERT CODE REVIEW
                </h1>
                <h2 className="text-4xl font-bold text-white drop-shadow-2xl">
                  White-box security <span className="text-blue-400">assessment</span>
                </h2>
              </div>
            </div>
          </div>

          {/* What is Code Review - Full width section with minimal side gaps */}
          <div className="relative bg-black dark:bg-black py-16 px-6 -mx-4 overflow-hidden">
            {/* V-Shape: Dark outside, Red inside */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Left side of V - Dark from left edge to center */}
              <div className="absolute top-0 left-0 w-1/2 h-full bg-gradient-to-br from-black via-black to-transparent opacity-90"></div>
              {/* Right side of V - Dark from right edge to center */}
              <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-bl from-black via-black to-transparent opacity-90"></div>
            </div>
            
            {/* Red center glow for V interior */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Center red V shape */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[900px] bg-red-600/60 rounded-full blur-[150px]"></div>
              {/* Bottom center red glow */}
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-red-500/50 rounded-full blur-[120px]"></div>
            </div>
            
            <div className="max-w-6xl mx-auto relative z-10">
              <h3 className="text-5xl font-bold text-red-600 dark:text-red-500 mb-6 text-center">What is Expert Code Review?</h3>
              <p className="text-3xl text-lg text-gray-200 dark:text-gray-200 mb-8 text-center max-w-5xl mx-auto leading-relaxed">
                Expert Code Review is a white-box security assessment where you have direct access to the application's 
                source code. Unlike black-box testing, you can analyze the code logic, data flow, and architecture to 
                find vulnerabilities that are difficult or impossible to detect through external testing.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-6">
                  <h4 className="font-bold text-white dark:text-white text-3
                  xl mb-3" style={{textAlign:'center' }}>Full Code Access</h4>
                  <p className="text-base text-gray-300 dark:text-gray-300" style={{textAlign:'center' }}>
                    Direct access to private repositories.Review <br/> source code, configuration files, and dependencies.
                  </p>
                </div>

                <div className="p-6">
                  <h4 className="font-bold text-white dark:text-white text-3xl mb-3" style={{textAlign:'center' }}>Logic Vulnerabilities</h4>
                  <p className="text-base text-gray-300 dark:text-gray-300" style={{textAlign:'center' }}>
                    Find business logic flaws, race conditions,and <br/> architectural issues that can't be found externally.
                  </p>
                </div>

                <div className="p-6">
                  <h4 className="font-bold text-white dark:text-white text-3xl mb-3" style={{textAlign:'center' }}>Precise References</h4>
                  <p className="text-base text-gray-300 dark:text-gray-300" style={{textAlign:'center' }}>
                    Report vulnerabilities with exact file names <br/>  and line numbers (e.g., src/api/auth.js:142).
                  </p>
                </div>

                <div className="p-6">
                  <h4 className="font-bold text-white dark:text-white text-3xl mb-3" style={{textAlign:'center' }}>Secure Access</h4>
                  <p className="text-base text-gray-300 dark:text-gray-300" style={{textAlign:'center' }}>
                    VPN access, NDA requirements,and strict <br/> confidentiality.Code never leaves secure environment.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Vulnerability Categories - Blue-black without shine */}
          <div className="relative bg-gradient-to-br from-[#0a0a1a] via-[#0f0f2a] to-[#0a0a1a] dark:bg-gradient-to-br dark:from-[#0a0a1a] dark:via-[#0f0f2a] dark:to-[#0a0a1a] py-16 px-6 -mx-4 overflow-hidden">
            {/* Geometric Background Pattern - Light Mode */}
            <div className="absolute inset-0 dark:hidden pointer-events-none">
              {/* Large diagonal shapes */}
              <div className="absolute -left-1/4 top-0 w-1/2 h-full bg-gradient-to-br from-[#1a1a2a] to-transparent transform -skew-x-12 opacity-60"></div>
              <div className="absolute right-0 top-0 w-1/3 h-full bg-gradient-to-bl from-[#1a1a3a] to-transparent transform skew-x-6 opacity-40"></div>
              <div className="absolute left-1/3 bottom-0 w-1/2 h-2/3 bg-gradient-to-tr from-[#0f0f1a] to-transparent transform -skew-y-12 opacity-50"></div>
            </div>
            
            {/* Geometric Background Pattern - Dark Mode */}
            <div className="absolute inset-0 hidden dark:block pointer-events-none">
              {/* Large diagonal shapes */}
              <div className="absolute -left-1/4 top-0 w-1/2 h-full bg-gradient-to-br from-[#1a1a2a] to-transparent transform -skew-x-12 opacity-60"></div>
              <div className="absolute right-0 top-0 w-1/3 h-full bg-gradient-to-bl from-[#1a1a3a] to-transparent transform skew-x-6 opacity-40"></div>
              <div className="absolute left-1/3 bottom-0 w-1/2 h-2/3 bg-gradient-to-tr from-[#0f0f1a] to-transparent transform -skew-y-12 opacity-50"></div>
            </div>
            
            <div className="max-w-6xl mx-auto relative z-10">
              <h3 className="text-3xl font-bold text-white dark:text-gray-100 mb-4 text-center">What to Look For</h3>
              <p className="text-lg text-gray-200 dark:text-gray-200 mb-10 text-center">
                Click on a category to see specific vulnerability types
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {vulnerabilityCategories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(selectedCategory === category.id ? null : category.id)}
                    className={`
                      p-6 text-left transition-all duration-300
                      ${selectedCategory === category.id 
                        ? 'ring-2 ring-blue-400 shadow-xl' 
                        : 'hover:shadow-lg'
                      }
                      bg-gradient-to-br ${category.color} text-white
                    `}
                  >
                    <h4 className="font-bold text-xl mb-2">{category.name}</h4>
                    <p className="text-white/90 mb-3">{category.description}</p>
                    {selectedCategory === category.id && (
                      <div className="mt-4 pt-4 border-t border-white/20">
                        <p className="text-sm font-semibold mb-2 text-white/80">Common Issues:</p>
                        <div className="space-y-2">
                          {category.examples.map((example, idx) => (
                            <div key={idx} className="text-sm px-3 py-2 bg-white/20">
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

          {/* Code Review Workflow - Thick white for both modes with minimal side gaps */}
          <div className="bg-white dark:bg-white py-16 px-6 -mx-4">
            <div className="max-w-6xl mx-auto">
              <h3 className="text-3xl font-bold text-slate-900 dark:text-slate-900 mb-10 text-center">Code Review Workflow</h3>
              <div className="relative max-w-3xl mx-auto">
                <div className="absolute left-4 top-8 bottom-8 w-0.5 bg-gradient-to-b from-red-500 to-red-600"></div>
                
                <div className="space-y-8">
                  {[
                    { step: 1, title: 'Assignment & NDA', desc: 'Organization assigns you to code review. Sign NDA and confidentiality agreement. Receive secure access credentials.' },
                    { step: 2, title: 'Repository Access', desc: 'Clone private repository via VPN. Review code structure, dependencies, and configuration files.' },
                    { step: 3, title: 'Manual Code Analysis', desc: 'Review code for security issues. Focus on hotspots identified by organization. Use static analysis tools.' },
                    { step: 4, title: 'Submit Findings', desc: 'Report vulnerabilities with file:line references. Explain attack path and provide remediation advice.' },
                    { step: 5, title: 'Verification', desc: 'After fixes, review updated code. Verify vulnerability is properly remediated. Check for new issues.' },
                    { step: 6, title: 'Final Report', desc: 'Comprehensive security report with all findings, severity ratings, and recommendations.' }
                  ].map((item) => (
                    <div key={item.step} className="flex gap-4 relative">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-red-600 text-white flex items-center justify-center font-bold shadow-lg z-10">
                        {item.step}
                      </div>
                      <div className="flex-1 pb-2">
                        <h4 className="font-bold text-slate-900 dark:text-slate-900 text-xl mb-2">{item.title}</h4>
                        <p className="text-base text-slate-600 dark:text-slate-600">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Required Skills - Split background without shine and minimal side gaps */}
          <div className="relative bg-gradient-to-r from-red-300 to-pink-300 dark:from-red-300 dark:to-pink-300 py-16 px-6 -mx-4">
            <div className="max-w-6xl mx-auto relative z-10">
              <h3 className="text-3xl font-bold text-slate-900 dark:text-slate-900 mb-12 " style={{marginLeft:'350px'}}>Required Skills & Tools</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                <div>
                  <div className="mb-6">
                    <h4 className="font-bold text-slate-900 dark:text-slate-900 text-xl">Programming Languages</h4>
                  </div>
                  <ul className="space-y-3">
                    {['JavaScript/TypeScript', 'Python', 'Java/Kotlin', 'C#/.NET', 'Go, Rust, PHP'].map((skill, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-base text-slate-700 dark:text-slate-700">
                        <span className="text-red-500 text-lg">•</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="mb-6">
                    <h4 className="font-bold text-slate-900 dark:text-slate-900 text-xl">Security Knowledge</h4>
                  </div>
                  <ul className="space-y-3">
                    {['OWASP Top 10', 'Secure coding practices', 'Cryptography basics', 'Authentication patterns', 'Threat modeling'].map((skill, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-base text-slate-700 dark:text-slate-700">
                        <span className="text-red-500 text-lg">•</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="mb-6">
                    <h4 className="font-bold text-slate-900 dark:text-slate-900 text-xl">Tools & Frameworks</h4>
                  </div>
                  <ul className="space-y-3">
                    {['Git/GitHub/GitLab', 'Static analysis (SonarQube, etc.)', 'IDE security plugins', 'Dependency scanners', 'Code search tools'].map((skill, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-base text-slate-700 dark:text-slate-700">
                        <span className="text-red-500 text-lg">•</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Best Practices - Full dark background with minimal side gaps */}
          <div className="relative bg-black dark:bg-black py-16 px-6 -mx-4 overflow-hidden">
            <div className="max-w-6xl mx-auto relative z-10">
              <h3 className="text-3xl font-bold text-white dark:text-white mb-10 text-center">Code Review Best Practices</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { title: 'Start with Hotspots', desc: 'Focus on authentication, authorization, payment processing, and data handling first.' },
                  { title: 'Trace Data Flow', desc: 'Follow user input from entry point to database. Look for validation gaps.' },
                  { title: 'Check Dependencies', desc: 'Review package.json, requirements.txt, pom.xml for outdated or vulnerable libraries.' },
                  { title: 'Document Attack Paths', desc: 'Explain how an attacker would exploit the vulnerability. Include code flow diagram.' }
                ].map((practice, idx) => (
                  <div key={idx} className="bg-gray-900 dark:bg-gray-900 p-6 border border-gray-800">
                    <h4 className="font-bold text-white dark:text-white text-xl mb-2">{practice.title}</h4>
                    <p className="text-base text-gray-300 dark:text-gray-300">{practice.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Empty State with minimal side gaps */}
          <div className="bg-white dark:bg-white py-16 px-6 -mx-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center py-12">
                <h3 className="text-lg font-medium text-slate-900 dark:text-slate-900 mb-2">
                  No Active Code Review Engagements
                </h3>
                <p className="text-slate-600 dark:text-slate-600 mb-4 max-w-md mx-auto">
                  You're not currently assigned to any code review engagements. Organizations will assign you based on your expertise and availability.
                </p>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
