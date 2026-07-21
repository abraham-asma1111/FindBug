"use client";

import { useApiQuery } from "@/hooks/useApiQuery";
import Card from "@/components/ui/Card";

interface LeaderboardEntry {
  rank: number;
  researcher_id: string;
  researcher_name: string;
  score: number;
  submissions_count: number;
  valid_submissions_count: number;
  prize_amount: number | null;
}

interface LeaderboardData {
  event_id: string;
  event_name: string;
  entries: LeaderboardEntry[];
}

interface LiveLeaderboardProps {
  eventId: string;
}

export function LiveLeaderboard({ eventId }: LiveLeaderboardProps) {
  const { data, isLoading } = useApiQuery<LeaderboardData>(
    `/live-events/${eventId}/leaderboard`,
    ["event-leaderboard", eventId],
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      </Card>
    );
  }

  if (!data || data.entries.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Live Leaderboard
        </h3>
        <p className="text-center py-8 text-gray-600 dark:text-gray-400">
          No submissions yet. Be the first to submit a finding!
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Live Leaderboard
        </h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Updates every 30 seconds
        </span>
      </div>

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
            {data.entries.map((entry) => (
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
                  {entry.prize_amount ? `${entry.prize_amount.toLocaleString()} ETB` : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
