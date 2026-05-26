export interface ProgramGuideSection {
  id: string;
  title: string;
  summary: string;
  bullets?: string[];
}

export interface ProgramGuideConfig {
  intro: string;
  sections: ProgramGuideSection[];
}

export const ptaasProgramGuide: ProgramGuideConfig = {
  intro:
    'Penetration Testing as a Service (PTaaS) is structured security testing where researchers simulate real-world attacks against in-scope systems. Organizations assign you to engagements with a defined methodology, timeline, and deliverables.',
  sections: [
    {
      id: 'methodologies',
      title: 'Testing methodologies',
      summary: 'Industry frameworks that shape your phase checklists and reporting.',
      bullets: [
        'OWASP WSTG — web application security across the SDLC',
        'PTES — seven-phase penetration testing lifecycle',
        'NIST SP 800-115 — planning, discovery, attack, and reporting',
        'Custom — hybrid approaches for specialized compliance needs',
      ],
    },
    {
      id: 'workflow',
      title: 'Engagement workflow',
      summary: 'Typical flow from assignment through retest.',
      bullets: [
        'Organization creates engagement with scope, methodology, and pricing',
        'Researchers are assigned and confirm access / rules of engagement',
        'Testing phases run with real-time finding submission and CVSS scoring',
        'Triage validates findings; executive and technical reports are produced',
        'Deliverables submitted; free retest window verifies remediation',
      ],
    },
    {
      id: 'testing-types',
      title: 'Common testing types',
      summary: 'What organizations usually scope for PTaaS.',
      bullets: [
        'Web application and API security',
        'Mobile application assessments',
        'Cloud infrastructure (AWS, Azure, GCP)',
        'Network penetration (internal / external)',
        'Wireless and configuration reviews',
      ],
    },
    {
      id: 'skills',
      title: 'Skills and tools',
      summary: 'What strong PTaaS researchers bring to engagements.',
      bullets: [
        'Certifications: OSCP, CEH, cloud security, domain-specific certs',
        'Technical: OWASP Top 10, API security, secure architecture',
        'Tools: Burp Suite, ZAP, Nmap, Metasploit, dependency scanners',
      ],
    },
  ],
};

export const aiRedTeamingProgramGuide: ProgramGuideConfig = {
  intro:
    'AI Red Teaming evaluates model behavior and safety policies—not only traditional code bugs. You probe assigned sandboxes for harmful outputs, policy violations, and adversarial failures using full conversation transcripts as evidence.',
  sections: [
    {
      id: 'concepts',
      title: 'Core concepts',
      summary: 'How AI security testing differs from classic bug bounty.',
      bullets: [
        'Behavioral testing — policy violations, bias, and unsafe outputs',
        'Probabilistic results — report success rates, not only pass/fail',
        'Transcript evidence — prompts, responses, and attack framing',
        'Safety policies — test only in-scope harms defined per engagement',
      ],
    },
    {
      id: 'attacks',
      title: 'Attack surfaces',
      summary: 'Common categories you may be asked to probe.',
      bullets: [
        'Prompt injection and instruction hijacking',
        'Jailbreaks and filter bypass techniques',
        'Data leakage and training-data extraction',
        'Model inversion and excessive agency',
        'Bias, fairness, and hallucination triggers',
      ],
    },
    {
      id: 'workflow',
      title: 'Researcher workflow',
      summary: 'End-to-end flow on the AI Red Teaming desk.',
      bullets: [
        'Review briefing, ethics, and allowed attack types',
        'Execute probes in the isolated sandbox / API',
        'Submit reports with prompt, response, impact, and mitigation',
        'Hand off for organization remediation and policy updates',
      ],
    },
  ],
};

export const codeReviewProgramGuide: ProgramGuideConfig = {
  intro:
    'Expert Code Review is white-box assessment: you analyze source code directly to find logic flaws, insecure dependencies, and architectural issues that external testing often misses.',
  sections: [
    {
      id: 'value',
      title: 'Why code review',
      summary: 'What organizations get from reviewer access.',
      bullets: [
        'Private repository access under NDA and scoped credentials',
        'Logic and business-flow vulnerabilities',
        'Findings with file path and line number references',
        'Remediation guidance engineering teams can act on immediately',
      ],
    },
    {
      id: 'categories',
      title: 'What to look for',
      summary: 'Common reviewer focus areas.',
      bullets: [
        'Authentication, authorization, and session handling',
        'Input validation, injection, and unsafe deserialization',
        'Cryptography, secrets, and key management',
        'Business logic, race conditions, and state issues',
        'Data exposure, logging, and dependency/CVE risk',
      ],
    },
    {
      id: 'workflow',
      title: 'Review workflow',
      summary: 'Steps from assignment to final report.',
      bullets: [
        'Assignment, NDA, and secure repository access',
        'Manual analysis of hotspots and data flows',
        'Log findings with severity, issue type, and location',
        'Submit final review package for remediation follow-up',
        'Optional verification pass after fixes land',
      ],
    },
  ],
};

export const liveEventsProgramGuide: ProgramGuideConfig = {
  intro:
    'Live Hacking Events are time-bound competitions where researchers hunt in real time. Leaderboards, triage, and scoring update during the event window so top performers earn recognition and prizes.',
  sections: [
    {
      id: 'benefits',
      title: 'Why live events',
      summary: 'What makes events different from ongoing programs.',
      bullets: [
        'Real-time leaderboard and competitive pressure',
        'Faster triage and validation during the window',
        'Direct coordination with org staff in the “war room”',
        'Prize pools and bonus recognition for top ranks',
      ],
    },
    {
      id: 'how-it-works',
      title: 'How events work',
      summary: 'Typical participant journey.',
      bullets: [
        'Register or accept an invitation (some events require minimum reputation)',
        'Join the briefing when the event starts',
        'Find vulnerabilities and submit or link reports',
        'Get near-real-time validation and score updates',
        'Climb the leaderboard; prizes allocated at close',
      ],
    },
    {
      id: 'event-types',
      title: 'Event types',
      summary: 'Formats you may see on the platform.',
      bullets: [
        'Target-specific — single app, usually 2–4 hours',
        'Sprint — fast 1-hour windows with speed multipliers',
        'Global — multi-day, larger prize pools',
        'Training — lower stakes, more guidance for newer researchers',
      ],
    },
  ],
};
