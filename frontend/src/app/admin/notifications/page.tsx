'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Spinner from '@/components/ui/Spinner';
import EmptyState from '@/components/ui/EmptyState';
import {
  Bell,
  CheckCircle2,
  Info,
  AlertTriangle,
  ShieldAlert,
  Clock,
  ArrowRight,
  Check,
  CheckCheck,
  Trash2,
  Filter,
  MoreVertical,
  Activity
} from 'lucide-react';
import Link from 'next/link';
import { useToast } from '@/components/ui/Toast';

interface Notification {
  id: string;
  type: string;
  priority: string;
  title: string;
  message: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  action_url: string | null;
  action_text: string | null;
  related_entity_type: string | null;
  related_entity_id: string | null;
}

export default function AdminNotificationsPage() {
  const user = useAuthStore((state) => state.user);
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const { showToast } = useToast();

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = filter === 'unread' 
    ? '/notifications?unread_only=true&limit=100' 
    : '/notifications?limit=100';

  const { data, isLoading, refetch } = useApiQuery<{
    notifications: Notification[];
    total: number;
    unread_count: number;
  }>({
    endpoint,
  });

  const markAsReadMutation = useApiMutation({
    method: 'PUT',
    onSuccess: () => {
      refetch();
    }
  });

  const markAllAsReadMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      showToast('All notifications marked as read', 'success');
      refetch();
      setSelectedIds(new Set());
    }
  });

  const deleteMutation = useApiMutation({
    method: 'DELETE',
    onSuccess: () => {
      refetch();
    }
  });

  const handleMarkAsRead = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    markAsReadMutation.mutate({ endpoint: `/notifications/${id}/read` });
  };

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate({ endpoint: '/notifications/mark-all-read' });
  };

  const handleDelete = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    deleteMutation.mutate({ endpoint: `/notifications/${id}` });
  };

  const handleBatchMarkRead = () => {
    if (selectedIds.size === 0) return;
    // In a real app we might have a batch endpoint, but here we can just loop or rely on mark-all
    // Since we don't have a batch read endpoint, we will just call mark-all-read if they want to clear,
    // or call individual endpoints.
    selectedIds.forEach((id) => handleMarkAsRead(id));
    setSelectedIds(new Set());
    showToast(`Marked ${selectedIds.size} notifications as read`, 'success');
  };

  const handleBatchDelete = () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`Are you sure you want to delete ${selectedIds.size} notifications?`)) return;
    selectedIds.forEach((id) => handleDelete(id));
    setSelectedIds(new Set());
    showToast(`Deleted ${selectedIds.size} notifications`, 'success');
  };

  const toggleSelection = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  };

  const toggleAll = () => {
    if (selectedIds.size === filteredNotifications.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredNotifications.map(n => n.id)));
    }
  };

  const notifications = data?.notifications || [];
  const unreadCount = data?.unread_count || 0;

  // Client-side filtering for 'read' state since backend only has 'unread_only'
  const filteredNotifications = notifications.filter(n => {
    if (filter === 'read') return n.is_read;
    return true; // 'all' and 'unread' handled by endpoint
  });

  const getPriorityConfig = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return {
          icon: ShieldAlert,
          color: 'text-[#EF4444]',
          bg: 'bg-[#EF4444]/10',
          border: 'border-[#EF4444]/50',
          glow: 'shadow-[0_0_15px_rgba(239,68,68,0.15)]'
        };
      case 'high':
        return {
          icon: AlertTriangle,
          color: 'text-[#F97316]',
          bg: 'bg-[#F97316]/10',
          border: 'border-[#F97316]/50',
          glow: 'shadow-[0_0_15px_rgba(249,115,22,0.15)]'
        };
      case 'medium':
        return {
          icon: Info,
          color: 'text-[#38BDF8]',
          bg: 'bg-[#0EA5E9]/10',
          border: 'border-[#38BDF8]/50',
          glow: 'shadow-[0_0_15px_rgba(56,189,248,0.15)]'
        };
      case 'low':
      default:
        return {
          icon: Bell,
          color: 'text-[#10B981]',
          bg: 'bg-[#10B981]/10',
          border: 'border-[#10B981]/50',
          glow: 'shadow-[0_0_15px_rgba(16,185,129,0.15)]'
        };
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
    } else if (diffInHours < 48) {
      return 'Yesterday, ' + date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
    } else {
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }
  };

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Notification Management"
          subtitle="System alerts and updates"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Hero Section with Glassmorphism */}
          <div className="relative overflow-hidden rounded-2xl border border-[#334155] bg-[#0F172A] p-8 sm:p-10 mb-8">
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-[#3B82F6]/10 via-transparent to-[#EF4444]/5 pointer-events-none"></div>
            
            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#1E293B] border border-[#334155] text-xs font-medium text-[#94A3B8] mb-4">
                  <Activity className="w-3.5 h-3.5 text-[#3B82F6]" />
                  Operations Center
                </div>
                <h1 className="text-3xl font-bold text-[#F8FAFC] tracking-tight sm:text-4xl mb-3">
                  Inbox & Alerts
                </h1>
                <p className="text-[#94A3B8] max-w-xl text-sm sm:text-base leading-relaxed">
                  Manage platform events, security notifications, and administrative alerts across all services in real-time.
                </p>
              </div>

              <div className="flex gap-4 min-w-[240px]">
                <div className="flex-1 bg-[#1E293B]/80 backdrop-blur-md border border-[#334155] rounded-xl p-5 text-center transition-transform hover:scale-105">
                  <p className="text-xs text-[#94A3B8] font-semibold uppercase tracking-wider mb-2">Unread Alerts</p>
                  <p className="text-4xl font-black text-[#F8FAFC]">
                    {isLoading ? <Spinner size="sm" className="mx-auto" /> : unreadCount}
                  </p>
                </div>
                <div className="flex-1 bg-[#1E293B]/80 backdrop-blur-md border border-[#334155] rounded-xl p-5 text-center transition-transform hover:scale-105">
                  <p className="text-xs text-[#94A3B8] font-semibold uppercase tracking-wider mb-2">Total</p>
                  <p className="text-4xl font-black text-[#F8FAFC]">
                    {isLoading ? <Spinner size="sm" className="mx-auto" /> : data?.total || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[240px_1fr] gap-8">
            {/* Left Sidebar Layout for Filters */}
            <div className="flex flex-col gap-6">
              <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-4 sticky top-24">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-4 pl-2">Views</h3>
                <nav className="space-y-1.5">
                  <button
                    onClick={() => setFilter('all')}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      filter === 'all'
                        ? 'bg-[#3B82F6] text-white shadow-md shadow-[#3B82F6]/20'
                        : 'text-[#94A3B8] hover:bg-[#0F172A] hover:text-[#F8FAFC]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Filter className="w-4 h-4" />
                      All Inbox
                    </div>
                  </button>
                  
                  <button
                    onClick={() => setFilter('unread')}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      filter === 'unread'
                        ? 'bg-[#3B82F6] text-white shadow-md shadow-[#3B82F6]/20'
                        : 'text-[#94A3B8] hover:bg-[#0F172A] hover:text-[#F8FAFC]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Bell className="w-4 h-4" />
                      Unread
                    </div>
                    {unreadCount > 0 && (
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${filter === 'unread' ? 'bg-white text-[#3B82F6]' : 'bg-[#EF4444] text-white'}`}>
                        {unreadCount}
                      </span>
                    )}
                  </button>

                  <button
                    onClick={() => setFilter('read')}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      filter === 'read'
                        ? 'bg-[#3B82F6] text-white shadow-md shadow-[#3B82F6]/20'
                        : 'text-[#94A3B8] hover:bg-[#0F172A] hover:text-[#F8FAFC]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <CheckCircle2 className="w-4 h-4" />
                      Archive
                    </div>
                  </button>
                </nav>

                <div className="mt-8 pt-6 border-t border-[#334155]">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-4 pl-2">Actions</h3>
                  <button
                    onClick={handleMarkAllAsRead}
                    disabled={unreadCount === 0 || markAllAsReadMutation.isLoading}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-[#94A3B8] hover:bg-[#0F172A] hover:text-[#F8FAFC] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <CheckCheck className="w-4 h-4" />
                    Mark all read
                  </button>
                </div>
              </div>
            </div>

            {/* Main Notifications List */}
            <div className="flex flex-col gap-4">
              
              {/* Batch Actions Bar (Floating / Dynamic) */}
              <div className={`flex items-center justify-between bg-[#1E293B] border border-[#334155] rounded-xl p-3 transition-all duration-300 ${selectedIds.size > 0 ? 'opacity-100 transform translate-y-0 shadow-lg shadow-black/40' : 'opacity-0 transform -translate-y-4 pointer-events-none absolute'}`}>
                <div className="flex items-center gap-3 px-2">
                  <span className="text-sm font-semibold text-[#38BDF8]">{selectedIds.size} selected</span>
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={handleBatchMarkRead}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-white bg-[#3B82F6] hover:bg-[#2563EB] rounded-lg transition-colors"
                  >
                    <Check className="w-3.5 h-3.5" />
                    Mark Read
                  </button>
                  <button 
                    onClick={handleBatchDelete}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-white bg-[#EF4444] hover:bg-[#DC2626] rounded-lg transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Delete
                  </button>
                  <button 
                    onClick={() => setSelectedIds(new Set())}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-[#94A3B8] hover:text-white transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>

              {/* List Header */}
              <div className="flex items-center justify-between px-2 mb-2">
                <div className="flex items-center gap-3">
                  <button 
                    onClick={toggleAll}
                    className="flex items-center justify-center w-5 h-5 rounded border border-[#475569] bg-[#0F172A] focus:ring-2 focus:ring-[#3B82F6]"
                  >
                    {selectedIds.size > 0 && selectedIds.size === filteredNotifications.length ? (
                      <Check className="w-3.5 h-3.5 text-[#3B82F6]" />
                    ) : selectedIds.size > 0 ? (
                      <div className="w-2.5 h-0.5 bg-[#3B82F6] rounded-sm" />
                    ) : null}
                  </button>
                  <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">Select All</span>
                </div>
                <span className="text-xs font-medium text-[#64748B]">{filteredNotifications.length} items</span>
              </div>

              {/* List Content */}
              <div className="space-y-3">
                {isLoading ? (
                  <div className="flex items-center justify-center py-20 bg-[#1E293B] rounded-xl border border-[#334155]">
                    <Spinner size="lg" />
                  </div>
                ) : filteredNotifications.length === 0 ? (
                  <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-16 text-center shadow-sm">
                    <EmptyState
                      title={filter === 'unread' ? "Zero Unread Alerts" : "Inbox Zero"}
                      description={filter === 'unread' ? "You're completely caught up on your platform notifications." : "When platform events occur, they'll show up right here."}
                      icon="🌟"
                    />
                  </div>
                ) : (
                  filteredNotifications.map((notification) => {
                    const config = getPriorityConfig(notification.priority);
                    const Icon = config.icon;
                    const isSelected = selectedIds.has(notification.id);
                    
                    return (
                      <div
                        key={notification.id}
                        onClick={() => toggleSelection(notification.id)}
                        className={`relative group cursor-pointer bg-[#1E293B] rounded-xl border p-4 sm:p-5 transition-all duration-200 hover:shadow-lg ${
                          isSelected 
                            ? 'border-[#3B82F6] shadow-md shadow-[#3B82F6]/10 bg-[#0F172A]/80' 
                            : !notification.is_read
                              ? `border-[#475569] shadow-md ${config.glow}`
                              : 'border-[#334155] opacity-80 hover:opacity-100 hover:border-[#475569]'
                        }`}
                      >
                        {/* Unread indicator line */}
                        {!notification.is_read && (
                          <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-xl ${config.bg.replace('/10', '')}`} />
                        )}

                        <div className="flex gap-4 sm:gap-5 items-start">
                          {/* Checkbox */}
                          <div className="mt-1 flex-shrink-0">
                            <div className={`flex items-center justify-center w-5 h-5 rounded border ${isSelected ? 'border-[#3B82F6] bg-[#3B82F6]' : 'border-[#475569] bg-[#0F172A]'} transition-colors`}>
                              {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
                            </div>
                          </div>

                          {/* Icon */}
                          <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center border ${config.bg} ${config.border}`}>
                            <Icon className={`w-5 h-5 ${config.color}`} />
                          </div>
                          
                          {/* Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1.5">
                              <h3 className={`text-base font-bold truncate pr-4 ${!notification.is_read ? 'text-[#F8FAFC]' : 'text-[#CBD5E1]'}`}>
                                {notification.title}
                              </h3>
                              <div className="flex items-center gap-2 text-xs font-medium text-[#64748B] flex-shrink-0 bg-[#0F172A] px-2.5 py-1 rounded-full border border-[#334155]">
                                <Clock className="w-3.5 h-3.5" />
                                {formatTime(notification.created_at)}
                              </div>
                            </div>
                            
                            <p className={`text-sm leading-relaxed mb-4 ${!notification.is_read ? 'text-[#94A3B8]' : 'text-[#64748B]'}`}>
                              {notification.message}
                            </p>
                            
                            {/* Footer / Actions */}
                            <div className="flex flex-wrap items-center gap-4">
                              {notification.action_url && (
                                <Link href={notification.action_url} onClick={(e) => e.stopPropagation()}>
                                  <span className="inline-flex items-center justify-center text-xs font-semibold px-4 py-2 rounded-lg bg-[#0F172A] text-[#F8FAFC] border border-[#334155] hover:border-[#475569] hover:bg-[#1E293B] transition-all">
                                    {notification.action_text || 'View Activity'}
                                    <ArrowRight className="w-3.5 h-3.5 ml-2 text-[#38BDF8]" />
                                  </span>
                                </Link>
                              )}
                              
                              <div className="flex items-center gap-2">
                                <span className={`inline-block text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md border ${config.bg} ${config.color} border-transparent`}>
                                  {notification.priority}
                                </span>
                                <span className="inline-block text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-[#0F172A] text-[#64748B] border border-[#334155]">
                                  {notification.type.replace(/_/g, ' ')}
                                </span>
                              </div>
                              
                              <div className="ml-auto flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                {!notification.is_read && (
                                  <button
                                    onClick={(e) => handleMarkAsRead(notification.id, e)}
                                    className="p-1.5 text-[#94A3B8] hover:text-[#3B82F6] hover:bg-[#3B82F6]/10 rounded-md transition-colors"
                                    title="Mark as read"
                                  >
                                    <Check className="w-4 h-4" />
                                  </button>
                                )}
                                <button
                                  onClick={(e) => handleDelete(notification.id, e)}
                                  className="p-1.5 text-[#94A3B8] hover:text-[#EF4444] hover:bg-[#EF4444]/10 rounded-md transition-colors"
                                  title="Delete"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}

