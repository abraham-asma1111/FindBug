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
}

export function getPortalNavItems(role: UserRole): PortalNavItem[] {
  if (isAdminRole(role)) {
    return [
      { href: '/admin/dashboard', label: 'Overview' },
      { href: '/admin/staff/create', label: 'Staff Provisioning' },
    ];
  }

  if (isStaffRole(role)) {
    return [{ href: '/staff/dashboard', label: 'Operations' }];
  }

  if (role === 'organization') {
    return [
      { href: '/organization/dashboard', label: 'Overview' },
      { href: '/organization/programs', label: 'Programs' },
    ];
  }

  return [
    { href: '/researcher/dashboard', label: 'Dashboard' },
    { href: '/researcher/engagements', label: 'Engagements' },
    { href: '/researcher/reports', label: 'Reports' },
    { href: '/researcher/earnings', label: 'Earnings' },
    { href: '/researcher/reputation', label: 'Reputation' },
    { href: '/researcher/analytics', label: 'Analytics' },
    { href: '/researcher/messages', label: 'Messages' },
    { href: '/researcher/settings', label: 'Settings' },
    { href: '/researcher/simulation', label: 'Simulation' },
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

  if (isStaffRole(role)) {
    return '/staff/dashboard';
  }

  if (role === 'organization') {
    return '/organization/dashboard';
  }

  return '/researcher/dashboard';
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
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
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
