'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

export default function AdminUsersPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const searchParams = useSearchParams();
  const roleFilter = searchParams.get('role') || 'all';
  const [search, setSearch] = useState('');
  const [actionPending, setActionPending] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [selectedRole, setSelectedRole] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
    
    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      // Only close if clicking outside dropdown and button
      if (!target.closest('.dropdown-container')) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const params = new URLSearchParams();
  if (roleFilter !== 'all') params.set('role', roleFilter);
  if (search) params.set('search', search);
  const endpoint = `/admin/users${params.toString() ? '?' + params.toString() : ''}`;

  const { data, isLoading, isError, error, refetch } = useApiQuery<any>({ endpoint });
  const users = data?.users || [];
  
  // Debug: Log API errors
  useEffect(() => {
    if (isError && error) {
      console.error('[Admin Users] API Error:', error.message);
    }
  }, [isError, error]);

  const handleStatusToggle = async (userId: string, currentStatus: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click navigation
    setActionPending(userId);
    setMessage(null);
    try {
      const isActive = currentStatus !== 'active';
      await api.post(`/admin/users/${userId}/status?is_active=${isActive}`);
      setMessage({ type: 'success', text: `User ${isActive ? 'activated' : 'deactivated'} successfully.` });
      refetch?.();
    } catch {
      setMessage({ type: 'error', text: 'Action failed. Please try again.' });
    } finally {
      setActionPending(null);
    }
  };

  const handleDeleteUser = async (userId: string, userEmail: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click navigation
    
    if (!confirm(`Are you sure you want to delete user "${userEmail}"? This action cannot be undone.`)) {
      return;
    }
    
    setActionPending(userId);
    setMessage(null);
    try {
      await api.post(`/admin/users/${userId}/delete`);
      setMessage({ type: 'success', text: 'User deleted successfully.' });
      refetch?.();
    } catch {
      setMessage({ type: 'error', text: 'Delete failed. Please try again.' });
    } finally {
      setActionPending(null);
    }
  };

  const handleRoleChange = async () => {
    if (!selectedUser || !selectedRole) return;
    
    setActionPending(selectedUser.id);
    setMessage(null);
    try {
      await api.post(`/admin/users/${selectedUser.id}/role?new_role=${selectedRole}`);
      setMessage({ type: 'success', text: 'User role updated successfully.' });
      setShowRoleModal(false);
      refetch?.();
    } catch {
      setMessage({ type: 'error', text: 'Role change failed. Please try again.' });
    } finally {
      setActionPending(null);
    }
  };

  const handleResetPassword = async (userId: string, userEmail: string) => {
    if (!confirm(`Send password reset email to "${userEmail}"?`)) {
      return;
    }
    
    setActionPending(userId);
    setMessage(null);
    try {
      // Call password reset endpoint
      await api.post(`/auth/forgot-password`, { email: userEmail });
      setMessage({ type: 'success', text: 'Password reset email sent successfully.' });
    } catch {
      setMessage({ type: 'error', text: 'Failed to send reset email. Please try again.' });
    } finally {
      setActionPending(null);
    }
  };

  const handleRowClick = (userId: string) => {
    router.push(`/admin/users/${userId}`);
  };

  const getRoleBadge = (role: string) => {
    const roleMap: Record<string, { bg: string; label: string }> = {
      researcher:       { bg: 'bg-[#3B71CA]', label: 'RESEARCHER' },      // Blue - Security/Technical
      organization:     { bg: 'bg-[#10B981]', label: 'ORGANIZATION' },    // Green - Business/Growth
      triage_specialist:{ bg: 'bg-[#F59E0B]', label: 'TRIAGE' },          // Amber - Review/Analysis
      finance_officer:  { bg: 'bg-[#EF2330]', label: 'FINANCE' },         // Red - Financial/Critical
      admin:            { bg: 'bg-[#8B5CF6]', label: 'ADMIN' },           // Purple - Administrative Power
      super_admin:      { bg: 'bg-[#EC4899]', label: 'SUPER ADMIN' },     // Pink - Highest Authority
    };
    const config = roleMap[role] || { bg: 'bg-[#64748B]', label: role?.toUpperCase() || 'UNKNOWN' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const ROLE_FILTERS = [
    { value: 'all', label: 'All' },
    { value: 'researcher', label: 'Researchers' },
    { value: 'organization', label: 'Organizations' },
    { value: 'triage_specialist', label: 'Triage' },
    { value: 'finance_officer', label: 'Finance' },
    { value: 'admin', label: 'Admin' },
  ];

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Users"
          subtitle="Manage platform users"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero Section */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                User Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Platform Users
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                View and manage all platform users, roles, and account status.
              </p>
            </div>
          </section>

          {/* Search + Filter Row */}
          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-2 flex-wrap">
              {ROLE_FILTERS.map(({ value, label }) => (
                <Link key={value} href={value === 'all' ? '/admin/users' : `/admin/users?role=${value}`}>
                  <Button
                    variant={roleFilter === value ? 'primary' : 'outline'}
                    size="sm"
                    className={roleFilter === value ? 'bg-[#EF2330] hover:bg-[#DC2026]' : ''}
                  >
                    {label}
                  </Button>
                </Link>
              ))}
            </div>
            <input
              type="text"
              placeholder="Search by name or email…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="rounded-md border border-[#334155] bg-[#0F172A] px-3 py-2 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#EF2330] focus:outline-none sm:w-64"
            />
          </div>

          {/* Status message */}
          {message && (
            <div className={`mt-4 rounded-md px-4 py-3 text-sm font-medium ${
              message.type === 'success' ? 'bg-[#10B981]/20 text-[#10B981]' : 'bg-[#EF4444]/20 text-[#EF4444]'
            }`}>
              {message.text}
            </div>
          )}

          {/* Users Table */}
          <div className="mt-4 bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
            {isLoading ? (
              <div className="p-6 text-center">
                <p className="text-[#94A3B8]">Loading users…</p>
              </div>
            ) : isError ? (
              <div className="p-6">
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4">
                  <h3 className="text-red-400 font-semibold mb-2">Error Loading Users</h3>
                  <p className="text-red-300 text-sm mb-3">{error?.message || 'Failed to load users'}</p>
                  <button
                    onClick={() => refetch?.()}
                    className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    Retry
                  </button>
                </div>
              </div>
            ) : users.length === 0 ? (
              <div className="p-6 text-center">
                <p className="text-[#94A3B8]">No users found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-[#0F172A] border-b border-[#334155]">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Role
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Joined
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#334155]">
                    {users.map((u: any) => (
                      <tr 
                        key={u.id} 
                        onClick={() => handleRowClick(u.id)}
                        className="hover:bg-[#0F172A] transition-colors cursor-pointer"
                      >
                        <td className="px-4 py-3">
                          <span className="font-semibold text-[#F8FAFC]">
                            {u.full_name || 'N/A'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-[#94A3B8]">
                          {u.email}
                        </td>
                        <td className="px-4 py-3">
                          {getRoleBadge(u.role)}
                        </td>
                        <td className="px-4 py-3">
                          {(() => {
                            // For researchers: must be email verified AND persona verified to be truly active
                            const isResearcher = u.role === 'researcher';
                            const isFullyVerified = isResearcher 
                              ? (u.email_verified === true && u.persona_verified === true)
                              : true; // Non-researchers don't need persona verification
                            
                            const isActive = u.is_active && isFullyVerified;
                            
                            return (
                              <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                                isActive ? 'bg-[#10B981]' : 'bg-[#64748B]'
                              } text-white`}>
                                {isActive ? 'ACTIVE' : 'INACTIVE'}
                              </span>
                            );
                          })()}
                        </td>
                        <td className="px-4 py-3 text-sm text-[#94A3B8]">
                          {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-center" onClick={(e) => e.stopPropagation()}>
                            <div className="relative dropdown-container">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setOpenDropdown(openDropdown === u.id ? null : u.id);
                                }}
                                className="p-2 hover:bg-[#334155] rounded transition-colors"
                                disabled={actionPending === u.id}
                              >
                                <svg className="w-5 h-5 text-[#94A3B8]" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                                </svg>
                              </button>
                              
                              {openDropdown === u.id && (
                                <div className="absolute right-0 mt-2 w-48 bg-[#1E293B] border border-[#334155] rounded-lg shadow-lg z-50 dropdown-container">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setOpenDropdown(null);
                                      router.push(`/admin/users/${u.id}`);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm text-[#F8FAFC] hover:bg-[#334155] transition-colors flex items-center gap-2"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                    </svg>
                                    View Details
                                  </button>
                                  
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setSelectedUser(u);
                                      setSelectedRole(u.role);
                                      setShowRoleModal(true);
                                      setOpenDropdown(null);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm text-[#F8FAFC] hover:bg-[#334155] transition-colors flex items-center gap-2"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                    Change Role
                                  </button>
                                  
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setOpenDropdown(null);
                                      handleResetPassword(u.id, u.email);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm text-[#F8FAFC] hover:bg-[#334155] transition-colors flex items-center gap-2"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                                    </svg>
                                    Reset Password
                                  </button>
                                  
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setOpenDropdown(null);
                                      handleStatusToggle(u.id, u.status, e);
                                    }}
                                    className={`w-full text-left px-4 py-2 text-sm hover:bg-[#334155] transition-colors flex items-center gap-2 ${
                                      u.status === 'active' ? 'text-[#EF4444]' : 'text-[#10B981]'
                                    }`}
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={u.status === 'active' ? "M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" : "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"} />
                                    </svg>
                                    {u.status === 'active' ? 'Deactivate' : 'Activate'}
                                  </button>
                                  
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setOpenDropdown(null);
                                      handleDeleteUser(u.id, u.email, e);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm text-[#EF4444] hover:bg-[#334155] transition-colors flex items-center gap-2 border-t border-[#334155]"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                    Delete User
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <p className="mt-4 text-xs text-[#64748B]">
            Showing {users.length} user{users.length !== 1 ? 's' : ''}
            {roleFilter !== 'all' ? ` with role "${roleFilter}"` : ''}
            {search ? ` matching "${search}"` : ''}
          </p>

          {/* Role Change Modal */}
          {showRoleModal && selectedUser && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowRoleModal(false)}>
              <div className="bg-[#1E293B] border border-[#334155] rounded-lg p-6 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Change User Role</h3>
                <p className="text-sm text-[#94A3B8] mb-4">
                  Change role for <span className="font-semibold text-[#F8FAFC]">{selectedUser.email}</span>
                </p>
                
                <div className="mb-6">
                  <label className="block text-sm font-medium text-[#94A3B8] mb-2">Select New Role</label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-md text-[#F8FAFC] focus:outline-none focus:border-[#EF2330]"
                  >
                    <option value="researcher">Researcher</option>
                    <option value="organization">Organization</option>
                    <option value="triage_specialist">Triage Specialist</option>
                    <option value="finance_officer">Finance Officer</option>
                    <option value="admin">Admin</option>
                    <option value="super_admin">Super Admin</option>
                  </select>
                </div>
                
                <div className="flex gap-3 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => setShowRoleModal(false)}
                    disabled={actionPending === selectedUser.id}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleRoleChange}
                    disabled={actionPending === selectedUser.id || selectedRole === selectedUser.role}
                    className="bg-[#EF2330] hover:bg-[#DC2026]"
                  >
                    {actionPending === selectedUser.id ? 'Updating…' : 'Update Role'}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
