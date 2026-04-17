export type UserRole =
  | 'researcher'
  | 'organization'
  | 'staff'
  | 'triage_specialist'
  | 'finance_officer'
  | 'admin'
  | 'super_admin';

export interface ResearcherProfile {
  bio?: string | null;
  website?: string | null;
  github?: string | null;
  twitter?: string | null;
  reputation_score?: number;
  rank?: number;
  total_earnings?: number;
}

export interface OrganizationProfile {
  company_name?: string | null;
  industry?: string | null;
  website?: string | null;
  subscription_type?: string | null;
}

export interface UserProfile {
  id: string;
  email: string;
  fullName?: string | null;
  role: UserRole;
  emailVerified: boolean;
  mfaEnabled: boolean;
  status?: string;
  researcher?: ResearcherProfile;
  organization?: OrganizationProfile;
}

export interface PortalNavItem {
  href: string;
  label: string;
  badge?: string | number;
  children?: PortalNavItem[];
}

export function getPortalNavItems(role: UserRole): PortalNavItem[] {
  // Admin Console
  if (isAdminRole(role)) {
    return [
      { href: '/admin/dashboard', label: 'Dashboard' },
      { href: '/admin/users', label: 'Users' },
      { href: '/admin/staff', label: 'Staff' },
      { href: '/admin/programs', label: 'Programs' },
      { href: '/admin/reports', label: 'Reports' },
      { href: '/admin/finance', label: 'Finance' },
      { href: '/admin/platform', label: 'Platform' },
      { href: '/admin/audit-logs', label: 'Audit Logs' },
    ];
  }

  // Triage Specialist Desk
  if (role === 'triage_specialist') {
    return [
      { href: '/triage/dashboard', label: 'Dashboard' },
      { 
        href: '/triage/queue', 
        label: 'Queue',
        children: [
          { href: '/triage/queue?status=validated', label: 'Validated' },
          { href: '/triage/queue?status=rejected', label: 'Rejected' },
          { href: '/triage/queue?status=in-progress', label: 'In Progress' },
        ]
      },
      { 
        href: '/triage/reports', 
        label: 'Reports',
        children: [
          { href: '/triage/duplicates', label: 'Duplicate Checker' },
          { href: '/triage/templates', label: 'Templates' },
        ]
      },
      { href: '/triage/analytics', label: 'Analytics' },
      { href: '/triage/researchers', label: 'Researchers' },
      { href: '/triage/programs', label: 'Programs' },
      { href: '/triage/messages', label: 'Messages' },
    ];
  }

  // Finance Officer Desk
  if (role === 'finance_officer') {
    return [
      { href: '/finance/dashboard', label: 'Dashboard' },
      { 
        href: '/finance/payments', 
        label: 'Payments',
        children: [
          { href: '/finance/payments?status=pending', label: 'Pending' },
          { href: '/finance/payments?status=approved', label: 'Approved' },
          { href: '/finance/payments?status=completed', label: 'Completed' },
        ]
      },
      { 
        href: '/finance/payouts', 
        label: 'Payouts',
        children: [
          { href: '/finance/payouts?status=requested', label: 'Requested' },
          { href: '/finance/payouts?status=processing', label: 'Processing' },
          { href: '/finance/payouts?status=completed', label: 'Completed' },
        ]
      },
      { 
        href: '/finance/kyc', 
        label: 'KYC',
        children: [
          { href: '/finance/kyc?status=pending', label: 'Pending Review' },
          { href: '/finance/kyc?status=approved', label: 'Approved' },
          { href: '/finance/kyc?status=rejected', label: 'Rejected' },
        ]
      },
      { href: '/finance/billing', label: 'Billing' },
      { href: '/finance/reports', label: 'Financial Reports' },
      { href: '/finance/analytics', label: 'Analytics' },
    ];
  }

  // Organization Portal
  if (role === 'organization') {
    return [
      { href: '/organization/dashboard', label: 'Dashboard' },
      { href: '/organization/programs', label: 'Programs' },
      { href: '/organization/reports', label: 'Reports' },
      { 
        href: '/organization/services', 
        label: 'Services',
        children: [
          { href: '/organization/ai-red-teaming', label: 'AI Red Teaming' },
          { href: '/organization/services/ptaas', label: 'PTaaS' },
          { href: '/organization/services/code-review', label: 'Code Review' },
          { href: '/organization/services/live-events', label: 'Live Events' },
        ]
      },
      { href: '/organization/researchers', label: 'Researchers' },
      { href: '/organization/analytics', label: 'Analytics' },
      { href: '/organization/billing', label: 'Billing' },
      { href: '/organization/integrations', label: 'Integrations' },
      { href: '/organization/messages', label: 'Messages' },
      { href: '/organization/settings', label: 'Settings' },
    ];
  }

  // Researcher Portal (default)
  return [
    { href: '/researcher/dashboard', label: 'Dashboard' },
    { 
      href: '/researcher/programs', 
      label: 'Programs',
      children: [
        { href: '/researcher/programs', label: 'Bug Bounty' },
        { href: '/researcher/programs/ai-red-teaming', label: 'AI Red Teaming' },
        { href: '/researcher/programs/ptaas', label: 'PTaaS' },
        { href: '/researcher/programs/code-review', label: 'Code Review' },
      ]
    },
    { 
      href: '/researcher/reports', 
      label: 'Reports',
      children: [
        { href: '/researcher/reports', label: 'Bug Bounty Reports' },
        { href: '/researcher/reports/ai-red-teaming', label: 'AI Red Teaming Reports' },
        { href: '/researcher/reports/ptaas', label: 'PTaaS Reports' },
        { href: '/researcher/reports/code-review', label: 'Code Review Reports' },
      ]
    },
    { href: '/researcher/earnings', label: 'Earnings' },
    { 
      href: '/researcher/reputation', 
      label: 'Reputation',
      children: [
        { href: '/researcher/reputation/leaderboard', label: 'Leaderboard' }
      ]
    },
    { href: '/researcher/analytics', label: 'Analytics' },
    { href: '/researcher/messages', label: 'Messages' },
    { href: '/researcher/events', label: 'Events' },
    { href: '/researcher/settings', label: 'Settings' },
  ];
}

export function isStaffRole(role: UserRole): boolean {
  return role === 'staff' || role === 'triage_specialist' || role === 'finance_officer';
}

export function isAdminRole(role: UserRole): boolean {
  return role === 'admin' || role === 'super_admin';
}

export function getDashboardRouteForRole(role: UserRole): string {
  if (isAdminRole(role)) {
    return '/admin/dashboard';
  }

  if (role === 'triage_specialist') {
    return '/triage/dashboard';
  }

  if (role === 'finance_officer') {
    return '/finance/dashboard';
  }

  if (role === 'organization') {
    return '/organization/dashboard';
  }

  return '/researcher/dashboard';
}

export function getPortalName(role: UserRole): string {
  switch (role) {
    case 'researcher':
      return 'Researcher Portal';
    case 'organization':
      return 'Organization Portal';
    case 'triage_specialist':
      return 'Triage Desk';
    case 'finance_officer':
      return 'Finance Desk';
    case 'admin':
      return 'Admin Console';
    case 'super_admin':
      return 'Super Admin Console';
    default:
      return 'Operations Desk';
  }
}

export function getRoleLabel(role: UserRole): string {
  switch (role) {
    case 'researcher':
      return 'Researcher';
    case 'organization':
      return 'Organization';
    case 'triage_specialist':
      return 'Triage Specialist';
    case 'finance_officer':
      return 'Finance Officer';
    case 'admin':
      return 'Administrator';
    case 'super_admin':
      return 'Super Admin';
    default:
      return 'Platform Staff';
  }
}

export function normalizeUser(raw: Record<string, any>): UserProfile {
  const role = String(raw.role ?? 'researcher').toLowerCase() as UserRole;
  const fullName =
    raw.full_name ??
    raw.fullName ??
    ([raw.first_name, raw.last_name].filter(Boolean).join(' ') || null);

  return {
    id: String(raw.id ?? raw.user_id ?? ''),
    email: String(raw.email ?? ''),
    fullName,
    role,
    // The backend currently exposes mixed verification field names across endpoints.
    emailVerified: Boolean(
      raw.email_verified ??
        raw.is_verified ??
        raw.emailVerified ??
        raw.isVerified ??
        raw.email_verified_at ??
        true
    ),
    mfaEnabled: Boolean(raw.mfa_enabled ?? raw.mfaEnabled ?? false),
    status: raw.status ?? 'active',
    researcher: raw.researcher,
    organization: raw.organization,
  };
}

export function formatCurrency(value: number | null | undefined): string {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    maximumFractionDigits: 2,
  }).format(value ?? 0);
}

export function formatCompactNumber(value: number | null | undefined): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value ?? 0);
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'Not available';
  }

  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}
