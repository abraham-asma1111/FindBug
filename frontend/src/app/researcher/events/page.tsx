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
          <div className="-mx-[11px] sm:-mx-[19px] lg:-mx-[19px] -my-6 lg:-my-8 space-y-0">
            {/* Hero Banner with Background Image */}
            <div className="relative w-full overflow-hidden h-[800px]">
              {/* Background Image - Full Width */}
              <img 
                src="/images/ live-hacking-events.png" 
                alt="Live Hacking Events" 
                className="absolute inset-0 w-full h-full object-cover object-[center_20%] brightness-125 contrast-110"
              />
              
              {/* Very light overlay only in middle for text readability */}
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/20 to-transparent"></div>
              
              {/* Content - Bottom Left */}
              <div className="relative z-10 h-full flex items-end justify-start pb-12 pl-12">
                <div className="text-left max-w-4xl">
                  <h1 className="text-8xl font-black text-white drop-shadow-[0_6px_16px_rgba(0,0,0,0.95)] mb-6 leading-tight">
                    LIVE HACKING EVENTS
                  </h1>
                  <h2 className="text-5xl font-bold text-white drop-shadow-[0_4px_12px_rgba(0,0,0,0.9)] leading-snug">
                    Compete in real-time <span className="text-[#ef2330] drop-shadow-[0_3px_10px_rgba(239,35,48,0.8)]">win instantly</span>
                  </h2>
                </div>
              </div>
            </div>

            {/* What is Live Hacking Events */}
            <div className="bg-white dark:bg-white py-12 px-6">
              <h3 className="text-3xl font-bold text-slate-900 dark:text-slate-900 mb-6 text-center" style={{color:'red'}}>What are Live Hacking Events?</h3>
              <p className="text-2xl text-lg text-slate-600 dark:text-slate-600 mb-6 text-center max-w-4xl mx-auto leading-relaxed" style={{textAlign:'center', color:'black'}}>
                Live Hacking Events are time-bound competitive security testing sessions where researchers<br/> compete in real-time 
                to find vulnerabilities. With instant triage, live leaderboards, and immediate <br/>payouts, these events create an 
                exciting and rewarding environment for top security researchers.
              </p>
            </div>

            {/* Feature Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
              <div className="bg-white dark:bg-white border-r border-slate-200 dark:border-slate-200 p-6 text-center">
                <h3 className="font-semibold text-slate-900 dark:text-slate-900 mb-2" style={{fontWeight:'bold', fontSize:'23px'}}>Real-Time Competition</h3>
                <p className="text-sm text-slate-600 dark:text-slate-600">
                  Compete live with other researchers. See the <br/>leaderboard update in real-time as bugs are found.
                </p>
              </div>

              <div className="bg-white dark:bg-white border-r border-slate-200 dark:border-slate-200 p-6 text-center">
                <h3 className="font-semibold text-slate-900 dark:text-slate-900 mb-2" style={{fontWeight:'bold', fontSize:'23px'}}>Instant Rewards</h3>
                <p className="text-sm text-slate-600 dark:text-slate-600">
                  Get paid immediately when your bug is <br/>validated.No waiting for weeks or months.
                </p>
              </div>

              <div className="bg-white dark:bg-white p-6 text-center">
                <h3 className="font-semibold text-slate-900 dark:text-slate-900 mb-2" style={{fontWeight:'bold', fontSize:'23px'}}>War Room Access</h3>
                <p className="text-sm text-slate-600 dark:text-slate-600" style={{ fontSize:'15px'}}>
                  Direct access to organization admins and <br/>triage specialists for instant feedback.
                </p>
              </div>
            </div>

            {/* Empty State */}
            <div className="py-20 px-6 bg-[#0a1628] dark:bg-[#0a1628]">
              <div className="text-center py-12">
                <div className="flex justify-center mb-4 text-gray-300">
                  📅
                </div>
                <h3 className="text-lg font-medium text-white mb-2">
                  No Events Available
                </h3>
                <p className="text-gray-300 mb-4 max-w-md mx-auto">
                  Live Hacking Events will be announced here. Check back soon for upcoming competitions!
                </p>
              </div>
            </div>

            {/* How It Works */}
            <div className="relative w-full overflow-hidden min-h-[600px] py-16 px-8 bg-gradient-to-r from-[#050711] from-10% via-[#0f1535] via-50% to-[#1e40af] to-90%">
              {/* Content */}
              <div className="relative z-10 max-w-4xl mx-auto">
                <h3 className="text-4xl font-bold text-white mb-10 text-center drop-shadow-lg">How Live Events Work</h3>
                <div className="space-y-6">
                  <div className="flex gap-6">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-lg shadow-lg">
                      1
                    </div>
                    <div>
                      <h4 className="font-bold text-xl text-white drop-shadow-md">Register for Event</h4>
                      <p className="text-base text-gray-100 mt-2 drop-shadow-sm">
                        Browse upcoming events and register. Some events may require invitation or minimum reputation.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-6">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-lg shadow-lg">
                      2
                    </div>
                    <div>
                      <h4 className="font-bold text-xl text-white drop-shadow-md">Join War Room</h4>
                      <p className="text-base text-gray-100 mt-2 drop-shadow-sm">
                        When the event starts, join the virtual War Room where you can see live updates and communicate with staff.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-6">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-lg shadow-lg">
                      3
                    </div>
                    <div>
                      <h4 className="font-bold text-xl text-white drop-shadow-md">Find & Submit Bugs</h4>
                      <p className="text-base text-gray-100 mt-2 drop-shadow-sm">
                        Test the target application and submit bugs. You can submit drafts and refine them during the event.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-6">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-lg shadow-lg">
                      4
                    </div>
                    <div>
                      <h4 className="font-bold text-xl text-white drop-shadow-md">Get Instant Validation</h4>
                      <p className="text-base text-gray-100 mt-2 drop-shadow-sm">
                        Triage specialists validate bugs in real-time. Approved bugs are added to your score immediately.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-6">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-lg shadow-lg">
                      5
                    </div>
                    <div>
                      <h4 className="font-bold text-xl text-white drop-shadow-md">Climb the Leaderboard</h4>
                      <p className="text-base text-gray-100 mt-2 drop-shadow-sm">
                        Watch your position on the live leaderboard. Top performers win bonus prizes and recognition.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Event Types */}
            <div className="relative w-full overflow-hidden py-16 px-8 bg-white dark:bg-white">
              <div className="relative z-10 max-w-6xl mx-auto">
                <h3 className="text-3xl font-bold text-slate-900 dark:text-slate-900 mb-10 text-center">Event Types</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  <div className="text-center">
                    <h4 className="font-bold text-xl text-slate-900 dark:text-slate-900 mb-3 text-center" style={{}}>Target-Specific Events</h4>
                    <p className="text-base text-slate-700 dark:text-slate-700 leading-relaxed">
                      Focus on a single application or system. <br/>Usually 2-4 hours long with specific scope.
                    </p>
                  </div>

                  <div className="text-center">
                    <h4 className="font-bold text-xl text-slate-900 dark:text-slate-900 mb-3 text-left" style={{marginLeft:'200px'}}>Sprint Events</h4>
                    <p className="text-base text-slate-700 dark:text-slate-700 leading-relaxed">
                     Fast-paced 1-hour events with bonus multipliers <br />for speed. First to find wins big.
                    </p>
                  </div>

                  <div className="text-center">
                    <h4 className="font-bold text-xl text-slate-900 dark:text-slate-900 mb-3 text-center">Global Events</h4>
                    <p className="text-base text-slate-700 dark:text-slate-700 leading-relaxed">
                      Multi-day events with researchers from around the world. <br/>Larger prize pools and recognition.
                    </p>
                  </div>

                  <div className="text-center">
                    <h4 className="font-bold text-xl text-slate-900 dark:text-slate-900 mb-3 text-left" style={{marginLeft:'200px'}}>Training Events</h4>
                    <p className="text-base text-slate-700 dark:text-slate-700 leading-relaxed">
                      Practice events for new researchers. <br />Lower stakes, more guidance, great for learning.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
