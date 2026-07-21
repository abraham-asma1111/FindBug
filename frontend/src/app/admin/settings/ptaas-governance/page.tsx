'use client';

import React, { useState } from 'react';
import { CommandLineIcon, DocumentCheckIcon } from '@heroicons/react/24/outline';

export default function PTaaSGovernancePage() {
  const [settings, setSettings] = useState({
    default_engagement_duration: 14,
    require_peer_review: true,
    max_testers_per_engagement: 3,
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Engagement Defaults */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-900/30 rounded-lg text-indigo-400">
              <CommandLineIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Engagement Defaults</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Default Duration (Days)</label>
              <input
                type="number"
                value={settings.default_engagement_duration}
                onChange={(e) => setSettings({ ...settings, default_engagement_duration: parseInt(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Max Testers per Engagement</label>
              <input
                type="number"
                value={settings.max_testers_per_engagement}
                onChange={(e) => setSettings({ ...settings, max_testers_per_engagement: parseInt(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Reporting Standards */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-pink-900/30 rounded-lg text-pink-400">
              <DocumentCheckIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Reporting Standards</h3>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Require Peer Review</label>
                <p className="text-xs text-gray-500">All findings must be peer-reviewed before publishing</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.require_peer_review ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, require_peer_review: !settings.require_peer_review })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.require_peer_review ? 'translate-x-5' : 'translate-x-0'}`} />
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
