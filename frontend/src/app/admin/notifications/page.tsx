'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
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
  CheckCheck
} from 'lucide-react';
import Link from 'next/link';

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
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

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
      refetch();
    }
  });

  const handleMarkAsRead = (id: string) => {
    markAsReadMutation.mutate({
      endpoint: `/notifications/${id}/read`
    });
  };

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate({
      endpoint: '/notifications/mark-all-read'
    });
  };

  const notifications = data?.notifications || [];
  const unreadCount = data?.unread_count || 0;

  const getPriorityConfig = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return {
          icon: ShieldAlert,
          color: 'text-[#EF4444]',
          bg: 'bg-[#EF4444]/10',
          border: 'border-l-[#EF4444]'
        };
      case 'high':
        return {
          icon: AlertTriangle,
          color: 'text-[#F97316]',
          bg: 'bg-[#F97316]/10',
          border: 'border-l-[#F97316]'
        };
      case 'medium':
        return {
          icon: Info,
          color: 'text-[#38BDF8]',
          bg: 'bg-[#0EA5E9]/10',
          border: 'border-l-[#38BDF8]'
        };
      case 'low':
      default:
        return {
          icon: Bell,
          color: 'text-[#10B981]',
          bg: 'bg-[#10B981]/10',
          border: 'border-l-[#10B981]'
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
      return 'Yesterday';
    } else {
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }
  };

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Notifications"
          subtitle="System alerts and updates"
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
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="text-center md:text-left">
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                  System Alerts
                </p>
                <h1 className="mt-2 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                  Notifications
                </h1>
                <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                  Stay updated on platform activity, security events, and important operational alerts.
                </p>
              </div>
              
              <div className="flex flex-col gap-3 min-w-[200px]">
                <div className="bg-[#0F172A] border border-[#334155] rounded-lg p-4 text-center">
                  <p className="text-xs text-[#94A3B8] font-semibold uppercase tracking-wider mb-1">Unread Alerts</p>
                  <p className="text-3xl font-bold text-[#F8FAFC]">
                    {isLoading ? <Spinner size="sm" className="mx-auto" /> : unreadCount}
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Controls */}
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 bg-[#1E293B] p-1 rounded-lg border border-[#334155]">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                  filter === 'all'
                    ? 'bg-[#0F172A] text-[#F8FAFC] shadow-sm'
                    : 'text-[#94A3B8] hover:text-[#F8FAFC]'
                }`}
              >
                All Notifications
              </button>
              <button
                onClick={() => setFilter('unread')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                  filter === 'unread'
                    ? 'bg-[#0F172A] text-[#F8FAFC] shadow-sm'
                    : 'text-[#94A3B8] hover:text-[#F8FAFC]'
                }`}
              >
                Unread
                {unreadCount > 0 && filter !== 'unread' && (
                  <span className="ml-2 inline-flex items-center justify-center bg-[#EF2330] text-white text-[10px] h-4 min-w-[16px] px-1 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </button>
            </div>

            {unreadCount > 0 && (
              <Button
                variant="outline"
                onClick={handleMarkAllAsRead}
                disabled={markAllAsReadMutation.isLoading}
                className="text-xs border-[#334155] hover:bg-[#334155] hover:text-white"
              >
                <CheckCheck className="w-4 h-4 mr-2" />
                Mark all as read
              </Button>
            )}
          </div>

          {/* Notifications List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="flex items-center justify-center py-20 bg-[#1E293B] rounded-lg border border-[#334155]">
                <Spinner size="lg" />
              </div>
            ) : notifications.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
                <EmptyState
                  title={filter === 'unread' ? "No unread notifications" : "No notifications yet"}
                  description={filter === 'unread' ? "You're all caught up!" : "When platform events occur, you'll see them here."}
                  icon="🔔"
                />
              </div>
            ) : (
              <div className="space-y-3">
                {notifications.map((notification) => {
                  const config = getPriorityConfig(notification.priority);
                  const Icon = config.icon;
                  
                  return (
                    <div
                      key={notification.id}
                      className={`relative overflow-hidden bg-[#1E293B] rounded-lg border transition-all duration-200 group ${
                        !notification.is_read
                          ? `border-[#475569] shadow-md shadow-black/20 border-l-4 ${config.border}`
                          : 'border-[#334155] opacity-75'
                      }`}
                    >
                      <div className="p-5 flex gap-4">
                        {/* Icon */}
                        <div className={`mt-1 flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${config.bg}`}>
                          <Icon className={`w-5 h-5 ${config.color}`} />
                        </div>
                        
                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1">
                            <h3 className={`text-base font-semibold truncate pr-4 ${!notification.is_read ? 'text-[#F8FAFC]' : 'text-[#E2E8F0]'}`}>
                              {notification.title}
                            </h3>
                            <div className="flex items-center gap-2 text-xs font-mono text-[#94A3B8] flex-shrink-0">
                              <Clock className="w-3.5 h-3.5" />
                              {formatTime(notification.created_at)}
                            </div>
                          </div>
                          
                          <p className={`text-sm leading-relaxed mb-3 ${!notification.is_read ? 'text-[#CBD5E1]' : 'text-[#94A3B8]'}`}>
                            {notification.message}
                          </p>
                          
                          {/* Footer / Actions */}
                          <div className="flex flex-wrap items-center gap-3">
                            {notification.action_url && (
                              <Link href={notification.action_url}>
                                <span className={`inline-flex items-center text-xs font-medium ${config.color} hover:underline transition-colors`}>
                                  {notification.action_text || 'View Details'}
                                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                                </span>
                              </Link>
                            )}
                            
                            <span className="inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#0F172A] text-[#94A3B8] border border-[#334155]">
                              {notification.type.replace(/_/g, ' ')}
                            </span>
                            
                            {!notification.is_read && (
                              <button
                                onClick={() => handleMarkAsRead(notification.id)}
                                disabled={markAsReadMutation.isLoading}
                                className="opacity-0 group-hover:opacity-100 transition-opacity ml-auto text-xs flex items-center text-[#94A3B8] hover:text-[#F8FAFC]"
                                title="Mark as read"
                              >
                                <Check className="w-4 h-4 mr-1" />
                                Mark as read
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
