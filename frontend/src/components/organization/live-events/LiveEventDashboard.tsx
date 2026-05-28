"use client";

import { useApiQuery } from "@/hooks/useApiQuery";
import Card from "@/components/ui/Card";
import PieChart from "@/components/ui/PieChart";
import BarChart from "@/components/ui/BarChart";

interface EventMetrics {
  total_invited: number;
  total_accepted: number;
  total_active: number;
  total_submissions: number;
  valid_submissions: number;
  invalid_submissions: number;
  duplicate_submissions: number;
  critical_bugs: number;
  high_bugs: number;
  medium_bugs: number;
  low_bugs: number;
  info_bugs: number;
  total_rewards_paid: number;
  average_reward: number;
  participation_rate: number;
}

interface LeaderboardEntry {
  rank: number;
  researcher_id: string;
  researcher_name: string;
  score: number;
  submissions_count: number;
  valid_submissions_count: number;
  prize_amount: number | null;
}

interface DashboardData {
  metrics: EventMetrics;
  leaderboard: LeaderboardEntry[];
}

interface LiveEventDashboardProps {
  eventId: string;
}

export function LiveEventDashboard({ eventId }: LiveEventDashboardProps) {
  const { data, isLoading, refetch } = useApiQuery<DashboardData>(
    `/live-events/${eventId}/dashboard`,
    ["live-event-dashboard", eventId],
    {
      refetchInterval: 10000, // Refresh every 10 seconds for real-time updates
    }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">No data available</p>
      </div>
    );
  }

  const { metrics, leaderboard } = data;

  // Prepare severity chart data
  const severityData = [
    { name: "Critical", value: metrics.critical_bugs, color: "#DC2626" },
    { name: "High", value: metrics.high_bugs, color: "#EA580C" },
    { name: "Medium", value: metrics.medium_bugs, color: "#F59E0B" },
    { name: "Low", value: metrics.low_bugs, color: "#10B981" },
    { name: "Info", value: metrics.info_bugs, color: "#3B82F6" },
  ];

  // Prepare submission status data
  const submissionStatusData = [
    { name: "Valid", value: metrics.valid_submissions, color: "#10B981" },
    { name: "Invalid", value: metrics.invalid_submissions, color: "#EF4444" },
    { name: "Duplicate", value: metrics.duplicate_submissions, color: "#F59E0B" },
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Submissions</div>
          <div className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
            {metrics.total_submissions}
          </div>
          <div className="mt-1 text-xs text-green-600 dark:text-green-400">
            {metrics.valid_submissions} valid
          </div>
        </Card>

        <Card className="p-6">
          <div className="text-sm text-gray-600 dark:text-gray-400">Active Participants</div>
          <div className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
            {metrics.total_active}
          </div>
          <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {Number(metrics.participation_rate).toFixed(1)}% participation rate
          </div>
        </Card>

        <Card className="p-6">
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Rewards</div>
          <div className="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
            {Number(metrics.total_rewards_paid).toLocaleString()} ETB
          </div>
          <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Avg: {Number(metrics.average_reward).toLocaleString()} ETB
          </div>
        </Card>

        <Card className="p-6">
          <div className="text-sm text-gray-600 dark:text-gray-400">Critical Bugs</div>
          <div className="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">
            {metrics.critical_bugs}
          </div>
          <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {metrics.high_bugs} high severity
          </div>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Severity Distribution
          </h3>
          <PieChart data={severityData} />
        </Card>

        {/* Submission Status */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Submission Status
          </h3>
          <PieChart data={submissionStatusData} />
        </Card>
      </div>

      {/* Leaderboard */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Live Leaderboard
          </h3>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Top 10 Researchers
          </span>
        </div>

        {leaderboard.length === 0 ? (
          <p className="text-center py-8 text-gray-600 dark:text-gray-400">
            No submissions yet
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Rank
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Researcher
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Score
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Submissions
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Valid
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Prize
                  </th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((entry) => (
                  <tr
                    key={entry.researcher_id}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center">
                        {entry.rank === 1 && <span className="text-2xl mr-2">🥇</span>}
                        {entry.rank === 2 && <span className="text-2xl mr-2">🥈</span>}
                        {entry.rank === 3 && <span className="text-2xl mr-2">🥉</span>}
                        <span className="font-semibold text-gray-900 dark:text-white">
                          #{entry.rank}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-900 dark:text-white">
                      {entry.researcher_name}
                    </td>
                    <td className="py-3 px-4 text-right font-semibold text-blue-600 dark:text-blue-400">
                      {entry.score}
                    </td>
                    <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                      {entry.submissions_count}
                    </td>
                    <td className="py-3 px-4 text-right text-green-600 dark:text-green-400">
                      {entry.valid_submissions_count}
                    </td>
                    <td className="py-3 px-4 text-right font-semibold text-green-600 dark:text-green-400">
                      {entry.prize_amount ? `${Number(entry.prize_amount).toLocaleString()} ETB` : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
