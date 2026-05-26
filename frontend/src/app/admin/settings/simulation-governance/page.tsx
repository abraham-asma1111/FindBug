'use client';

import React, { useState } from 'react';
import { AcademicCapIcon, TrophyIcon } from '@heroicons/react/24/outline';

export default function SimulationGovernancePage() {
  const [settings, setSettings] = useState({
    default_team_size: 4,
    show_leaderboard_during_event: true,
    require_registration_approval: false,
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Event Configuration */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-purple-900/30 rounded-lg text-purple-400">
              <AcademicCapIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Event Configuration</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Default Max Team Size</label>
              <input
                type="number"
                value={settings.default_team_size}
                onChange={(e) => setSettings({ ...settings, default_team_size: parseInt(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <div>
                <label className="block text-sm font-medium text-gray-300">Require Registration Approval</label>
                <p className="text-xs text-gray-500">Admins must approve all CTF/LHE participants</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.require_registration_approval ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, require_registration_approval: !settings.require_registration_approval })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.require_registration_approval ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Visibility */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-yellow-900/30 rounded-lg text-yellow-400">
              <TrophyIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Leaderboard Visibility</h3>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Show Real-Time Leaderboard</label>
                <p className="text-xs text-gray-500">Display leaderboard updates during the event</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.show_leaderboard_during_event ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, show_leaderboard_during_event: !settings.show_leaderboard_during_event })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.show_leaderboard_during_event ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4 border-t border-gray-800">
        <button className="px-6 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary-500/20">
          Save Changes
        </button>
      </div>
    </div>
  );
}
