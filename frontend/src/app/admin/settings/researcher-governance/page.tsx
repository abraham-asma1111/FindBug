'use client';

import React, { useState } from 'react';
import { IdentificationIcon, StarIcon } from '@heroicons/react/24/outline';

export default function ResearcherGovernancePage() {
  const [settings, setSettings] = useState({
    require_kyc: true,
    reputation_multiplier_critical: 10,
    reputation_multiplier_high: 5,
    auto_ban_threshold: -50,
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Verification & KYC */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-900/30 rounded-lg text-blue-400">
              <IdentificationIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Verification Policies</h3>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Require KYC for Payouts</label>
                <p className="text-xs text-gray-500">Enforce identity verification before any bounty payment</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.require_kyc ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, require_kyc: !settings.require_kyc })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.require_kyc ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Auto-Ban Threshold (Reputation)</label>
              <input
                type="number"
                value={settings.auto_ban_threshold}
                onChange={(e) => setSettings({ ...settings, auto_ban_threshold: parseInt(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <p className="text-xs text-gray-500 mt-1">Ban accounts dropping below this score due to spam/invalid reports.</p>
            </div>
          </div>
        </div>

        {/* Reputation System */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-yellow-900/30 rounded-lg text-yellow-400">
              <StarIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Reputation Scoring</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Critical Severity Multiplier</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">x</span>
                <input
                  type="number"
                  value={settings.reputation_multiplier_critical}
                  onChange={(e) => setSettings({ ...settings, reputation_multiplier_critical: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-8 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">High Severity Multiplier</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">x</span>
                <input
                  type="number"
                  value={settings.reputation_multiplier_high}
                  onChange={(e) => setSettings({ ...settings, reputation_multiplier_high: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-8 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
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
