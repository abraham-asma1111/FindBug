export type UserRole =
  | 'researcher'
  | 'organization'
  | 'staff'
  | 'triage_specialist'
  | 'finance_officer'
  | 'admin';

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
  category?: string;
  icon?: string;
}

export function getPortalNavItems(role: UserRole): PortalNavItem[] {
  // Admin Console
  if (isAdminRole(role)) {
    return [
      { href: '/admin/dashboard', label: 'Dashboard' },
      { href: '/admin/programs', label: 'Programs' },
      { href: '/admin/pentests', label: 'Pentests' },
      { href: '/admin/reports', label: 'Reports' },
      { href: '/finance/payments?tab=bounty-payments&status=approved', label: 'Bounties' },
      { href: '/admin/activity-logs', label: 'Activity Logs' },
      { href: '/admin/analytics', label: 'Analytics' },
      { href: '/admin/platform-wallet', label: 'Platform Wallet' },
      { href: '/admin/notifications', label: 'Notifications' },
      { href: '/admin/messages', label: 'Messages' },
      { 
        href: '/admin/users', 
        label: 'Users & Roles',
        children: [
          { href: '/admin/users', label: 'All Users' },
          { href: '/admin/staff', label: 'Staff' },
        ]
      },
      { href: '/admin/settings', label: 'Settings' },
      { href: '/admin/system-health', label: 'System Health' },
      {
        href: '/admin/simulation',
        label: 'Simulation Panel',
        children: [
          { href: '/admin/simulation', label: 'Challenges' },
          { href: '/admin/simulation/reports', label: 'Review Reports' },
          { href: '/admin/simulation/writeups', label: 'Writeups' },
        ]
      },
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
      // OVERVIEW
      { href: '/finance/dashboard', label: 'Dashboard', category: 'OVERVIEW' },
      { href: '/finance/analytics', label: 'Analytics', category: 'OVERVIEW' },
      
      // PAYMENTS
      { 
        href: '/finance/payments', 
        label: 'Payments',
        category: 'PAYMENTS',
        children: [
          { href: '/finance/payments?tab=bounty-payments&status=approved', label: 'Bounty Payments' },
          { href: '/finance/payments?tab=payouts&status=pending', label: 'Payouts' },
        ]
      },
      { 
        href: '/finance/payment-methods', 
        label: 'Payment Methods',
        category: 'PAYMENTS',
        children: [
          { href: '/finance/payment-methods?status=pending', label: 'Pending' },
          { href: '/finance/payment-methods?status=approved', label: 'Approved' },
          { href: '/finance/payment-methods?status=rejected', label: 'Rejected' },
        ]
      },
      { 
        href: '/finance/kyc', 
        label: 'KYC Verification',
        category: 'PAYMENTS',
        children: [
          { href: '/finance/kyc?status=pending', label: 'Pending Review' },
          { href: '/finance/kyc?status=approved', label: 'Approved' },
          { href: '/finance/kyc?status=rejected', label: 'Rejected' },
        ]
      },
      
      // FINANCIAL OPERATIONS
      { href: '/finance/organizations', label: 'Organizations', category: 'FINANCIAL OPERATIONS' },
      { href: '/finance/transactions', label: 'Transactions', category: 'FINANCIAL OPERATIONS' },
      { href: '/finance/billing', label: 'Invoices & Billing', category: 'FINANCIAL OPERATIONS' },
      
      // REPORTS
      { href: '/finance/reports', label: 'Reports', category: 'REPORTS' },
      
      // SETTINGS
      { href: '/finance/settings/payment-methods', label: 'Payment Methods', category: 'SETTINGS' },
      { href: '/finance/settings/fees', label: 'Fee & Commission', category: 'SETTINGS' },
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
      { href: '/organization/wallet', label: 'Wallet' },
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
    { 
      href: '/researcher/earnings', 
      label: 'Earnings',
      children: [
        { href: '/researcher/payment-methods', label: 'Payment Methods' },
      ]
    },
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
    { href: '/researcher/simulation', label: 'Academy' },
    { href: '/researcher/settings', label: 'Settings' },
  ];
}

export function isStaffRole(role: UserRole): boolean {
  return role === 'staff' || role === 'triage_specialist' || role === 'finance_officer';
}

export function isAdminRole(role: UserRole): boolean {
  return role === 'admin';
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
