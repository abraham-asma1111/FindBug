'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import EmptyState from '@/components/ui/EmptyState';

export default function ResearcherEventsPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Live Hacking Events"
          subtitle="Participate in time-bound competitive security testing events with real-time leaderboards and instant rewards."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Coming Soon Banner */}
            <div className="rounded-2xl bg-gradient-to-r from-[#ef2330] to-[#d81c29] p-8 text-center text-white">
              <div className="text-4xl mb-4">🎯</div>
              <h2 className="text-2xl font-bold mb-2">Live Hacking Events</h2>
              <p className="text-white/90 max-w-2xl mx-auto">
                Compete with top researchers in time-bound events. Real-time leaderboards, instant triage, and immediate payouts.
              </p>
            </div>

            {/* Feature Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="rounded-2xl bg-[#faf6f1] p-6 text-center">
                <div className="text-3xl mb-3">⚡</div>
                <h3 className="font-semibold text-[#2d2a26] mb-2">Real-Time Competition</h3>
                <p className="text-sm text-[#6d6760]">
                  Compete live with other researchers. See the leaderboard update in real-time as bugs are found.
                </p>
              </div>

              <div className="rounded-2xl bg-[#faf6f1] p-6 text-center">
                <div className="text-3xl mb-3">🏆</div>
                <h3 className="font-semibold text-[#2d2a26] mb-2">Instant Rewards</h3>
                <p className="text-sm text-[#6d6760]">
                  Get paid immediately when your bug is validated. No waiting for weeks or months.
                </p>
              </div>

              <div className="rounded-2xl bg-[#faf6f1] p-6 text-center">
                <div className="text-3xl mb-3">👥</div>
                <h3 className="font-semibold text-[#2d2a26] mb-2">War Room Access</h3>
                <p className="text-sm text-[#6d6760]">
                  Direct access to organization admins and triage specialists for instant feedback.
                </p>
              </div>
            </div>

            {/* Empty State */}
            <EmptyState
              icon="📅"
              title="No Events Available"
              description="Live Hacking Events will be announced here. Check back soon for upcoming competitions!"
            />

            {/* How It Works */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">How Live Events Work</h3>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Register for Event</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Browse upcoming events and register. Some events may require invitation or minimum reputation.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Join War Room</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      When the event starts, join the virtual War Room where you can see live updates and communicate with staff.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Find & Submit Bugs</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Test the target application and submit bugs. You can submit drafts and refine them during the event.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    4
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Get Instant Validation</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Triage specialists validate bugs in real-time. Approved bugs are added to your score immediately.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm">
                    5
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#2d2a26]">Climb the Leaderboard</h4>
                    <p className="text-sm text-[#6d6760] mt-1">
                      Watch your position on the live leaderboard. Top performers win bonus prizes and recognition.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Event Types */}
            <div className="rounded-2xl bg-[#faf6f1] p-6">
              <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Event Types</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <h4 className="font-semibold text-[#2d2a26] mb-2">🎯 Target-Specific Events</h4>
                  <p className="text-sm text-[#6d6760]">
                    Focus on a single application or system. Usually 2-4 hours long with specific scope.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <h4 className="font-semibold text-[#2d2a26] mb-2">🏃 Sprint Events</h4>
                  <p className="text-sm text-[#6d6760]">
                    Fast-paced 1-hour events with bonus multipliers for speed. First to find wins big.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <h4 className="font-semibold text-[#2d2a26] mb-2">🌍 Global Events</h4>
                  <p className="text-sm text-[#6d6760]">
                    Multi-day events with researchers from around the world. Larger prize pools and recognition.
                  </p>
                </div>

                <div className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                  <h4 className="font-semibold text-[#2d2a26] mb-2">🎓 Training Events</h4>
                  <p className="text-sm text-[#6d6760]">
                    Practice events for new researchers. Lower stakes, more guidance, great for learning.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
