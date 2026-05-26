'use client';

import React, { useState } from 'react';
import { BriefcaseIcon, CurrencyDollarIcon, ClipboardDocumentCheckIcon } from '@heroicons/react/24/outline';

export default function ProgramGovernancePage() {
  const [settings, setSettings] = useState({
    min_bounty: 50,
    max_bounty: 50000,
    default_visibility: 'Private',
    require_asset_verification: true,
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Financial Boundaries */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-emerald-900/30 rounded-lg text-emerald-400">
              <CurrencyDollarIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Financial Boundaries</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Platform Minimum Bounty (USD)</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">$</span>
                <input
                  type="number"
                  value={settings.min_bounty}
                  onChange={(e) => setSettings({ ...settings, min_bounty: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-8 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Default Max Bounty Suggestion (USD)</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">$</span>
                <input
                  type="number"
                  value={settings.max_bounty}
                  onChange={(e) => setSettings({ ...settings, max_bounty: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-8 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Default Program Settings */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-900/30 rounded-lg text-indigo-400">
              <ClipboardDocumentCheckIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Default Program Settings</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Default New Program Visibility</label>
              <div className="flex bg-gray-900 border border-gray-700 rounded-lg p-1">
                {['Private', 'Public'].map((type) => (
                  <button
                    key={type}
                    onClick={() => setSettings({ ...settings, default_visibility: type })}
                    className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-colors ${
                      settings.default_visibility === type
                        ? 'bg-gray-700 text-white shadow'
                        : 'text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Require Asset Verification</label>
                <p className="text-xs text-gray-500">Organizations must verify domain ownership</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.require_asset_verification ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, require_asset_verification: !settings.require_asset_verification })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.require_asset_verification ? 'translate-x-5' : 'translate-x-0'}`} />
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
