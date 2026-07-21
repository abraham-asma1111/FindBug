'use client';

import React, { useState } from 'react';
import { CpuChipIcon, SparklesIcon } from '@heroicons/react/24/outline';

export default function AIRedTeamingPage() {
  const [settings, setSettings] = useState({
    enable_ai_analysis: true,
    llm_strictness: 75,
    openai_api_key: 'sk-********************************',
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Model Integrations */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-teal-900/30 rounded-lg text-teal-400">
              <CpuChipIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Model Integrations</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">OpenAI API Key</label>
              <input
                type="password"
                value={settings.openai_api_key}
                onChange={(e) => setSettings({ ...settings, openai_api_key: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <div>
                <label className="block text-sm font-medium text-gray-300">Enable Automated AI Analysis</label>
                <p className="text-xs text-gray-500">Use AI to preliminary triage incoming vulnerability reports</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.enable_ai_analysis ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, enable_ai_analysis: !settings.enable_ai_analysis })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.enable_ai_analysis ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Logic & Scopes */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-900/30 rounded-lg text-indigo-400">
              <SparklesIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Analysis Logic</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <div className="flex justify-between mb-1">
                <label className="block text-sm font-medium text-gray-300">LLM Evaluation Strictness</label>
                <span className="text-sm font-bold text-primary-400">{settings.llm_strictness}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={settings.llm_strictness}
                onChange={(e) => setSettings({ ...settings, llm_strictness: parseInt(e.target.value) })}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Forgiving</span>
                <span>Strict</span>
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
