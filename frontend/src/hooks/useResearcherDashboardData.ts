'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export interface ResearcherSubmission {
  id?: string;
  report_number?: string;
  title: string;
  status?: string;
  assigned_severity?: string | null;
  submitted_at?: string | null;
  bounty_amount?: number | null;
  program_name?: string | null;
  cvss_score?: number | null;
}

export interface ResearcherDashboardData {
  overview: {
    total_submissions: number;
    submissions_by_status: Record<string, number>;
    active_programs: number;
  };
  earnings: {
    total_earnings: number;
    pending_earnings: number;
    paid_earnings: number;
  };
  reputation: {
    score: number;
    rank: number;
    total_researchers: number;
    percentile: number;
  };
  recent_submissions: ResearcherSubmission[];
  monthly_trend: Array<{
    month: string;
    label?: string;
    submissions: number;
    earnings: number;
  }>;
}

export interface NotificationItem {
  id: string;
  type?: string | null;
  priority?: string | null;
  title: string;
  message: string;
  is_read: boolean;
  created_at?: string | null;
  action_url?: string | null;
  action_text?: string | null;
}

export interface WalletBalanceData {
  wallet_id: string;
  balance: number;
  reserved_balance: number;
  available_balance: number;
  currency: string;
}

export interface ResearcherPerformanceData {
  period: string;
  metrics: {
    total_reports: number;
    valid_reports: number;
    invalid_reports: number;
    success_rate: number;
    earnings: number;
    reputation_score: number;
    rank?: number | null;
  };
  severity_distribution: Record<string, number>;
  top_vulnerability_types: Array<{
    type?: string | null;
    count: number;
  }>;
}

export interface MyReputationData {
  profile?: {
    researcher_id: string;
    username?: string | null;
    reputation_score: number;
    rank?: number | null;
    total_earnings: number;
    stats?: {
      total_reports: number;
      valid_reports: number;
      invalid_reports: number;
      duplicate_reports: number;
      success_rate: number;
      by_severity: Record<string, number>;
    };
  };
  rank_info?: {
    rank?: number | null;
    total_researchers: number;
    percentile: number;
    reputation_score: number;
  };
}

export interface SimulationStatsData {
  stats?: Record<string, unknown>;
  privacy_note?: string | null;
}

interface SecondaryDashboardState {
  notifications: NotificationItem[];
  unreadNotifications: number;
  unreadMessages: number;
  wallet: WalletBalanceData | null;
  performance: ResearcherPerformanceData | null;
  myReputation: MyReputationData | null;
  simulation: SimulationStatsData | null;
  secondaryWarnings: string[];
}

interface UseResearcherDashboardDataResult extends SecondaryDashboardState {
  data: ResearcherDashboardData | null;
  error: string;
  isLoading: boolean;
}

function createEmptySecondaryDashboardState(): SecondaryDashboardState {
  return {
    notifications: [],
    unreadNotifications: 0,
    unreadMessages: 0,
    wallet: null,
    performance: null,
    myReputation: null,
    simulation: null,
    secondaryWarnings: [],
  };
}

async function loadSecondaryResearcherDashboardState(): Promise<SecondaryDashboardState> {
  const secondaryState = createEmptySecondaryDashboardState();

  const widgetLoaders = [
    {
      label: 'notifications',
      load: () => api.get('/notifications', { params: { unread_only: true, limit: 4, offset: 0 } }),
      assign: (responseData: any) => {
        secondaryState.notifications = responseData?.notifications || [];
        secondaryState.unreadNotifications = responseData?.unread_count || 0;
      },
    },
    {
      label: 'messages',
      load: () => api.get('/messages/unread-count'),
      assign: (responseData: any) => {
        secondaryState.unreadMessages = responseData?.unread_count || 0;
      },
    },
    {
      label: 'wallet',
      load: () => api.get('/wallet/balance'),
      assign: (responseData: any) => {
        secondaryState.wallet = responseData || null;
      },
    },
    {
      label: 'performance',
      load: () => api.get('/analytics/my-performance', { params: { time_period: '6months' } }),
      assign: (responseData: any) => {
        secondaryState.performance = responseData || null;
      },
    },
    {
      label: 'reputation',
      load: () => api.get('/my-reputation'),
      assign: (responseData: any) => {
        secondaryState.myReputation = responseData || null;
      },
    },
    {
      label: 'simulation',
      load: () => api.get('/simulation/my-stats'),
      assign: (responseData: any) => {
        secondaryState.simulation = responseData || null;
      },
    },
  ];

  const settledResults = await Promise.allSettled(widgetLoaders.map((entry) => entry.load()));

  settledResults.forEach((result, index) => {
    const widget = widgetLoaders[index];

    if (result.status === 'fulfilled') {
      widget.assign(result.value.data);
      return;
    }

    secondaryState.secondaryWarnings.push(widget.label);
  });

  return secondaryState;
}

export function useResearcherDashboardData(): UseResearcherDashboardDataResult {
  const [data, setData] = useState<ResearcherDashboardData | null>(null);
  const [secondaryState, setSecondaryState] = useState<SecondaryDashboardState>(
    createEmptySecondaryDashboardState()
  );
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      try {
        setIsLoading(true);

        const [dashboardResponse, nextSecondaryState] = await Promise.all([
          api.get('/dashboard/researcher'),
          loadSecondaryResearcherDashboardState(),
        ]);

        if (cancelled) {
          return;
        }

        setData(dashboardResponse.data);
        setSecondaryState(nextSecondaryState);
        setError('');
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load researcher dashboard.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  return {
    data,
    error,
    isLoading,
    ...secondaryState,
  };
}
