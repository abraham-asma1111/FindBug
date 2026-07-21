'use client';

import React, { useState } from 'react';
import { LinkIcon, CubeTransparentIcon } from '@heroicons/react/24/outline';

export default function IntegrationPage() {
  const [settings, setSettings] = useState({
    enable_webhooks: true,
    jira_client_id: '',
    github_client_id: '',
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Third-Party Connectors */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-900/30 rounded-lg text-blue-400">
              <CubeTransparentIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">OAuth Clients</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Jira Client ID</label>
              <input
                type="text"
                placeholder="e.g. 1a2b3c4d5e"
                value={settings.jira_client_id}
                onChange={(e) => setSettings({ ...settings, jira_client_id: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">GitHub Client ID</label>
              <input
                type="text"
                placeholder="e.g. Iv1.1a2b3c4d5e"
                value={settings.github_client_id}
                onChange={(e) => setSettings({ ...settings, github_client_id: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Webhooks */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-green-900/30 rounded-lg text-green-400">
              <LinkIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Global Webhooks</h3>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Enable Outbound Webhooks</label>
                <p className="text-xs text-gray-500">Allow organizations to set up real-time event notifications</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.enable_webhooks ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, enable_webhooks: !settings.enable_webhooks })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.enable_webhooks ? 'translate-x-5' : 'translate-x-0'}`} />
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
