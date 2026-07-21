'use client';

import React, { useState } from 'react';
import { CreditCardIcon, DocumentChartBarIcon } from '@heroicons/react/24/outline';

export default function FinancialControlPage() {
  const [settings, setSettings] = useState({
    platform_commission: 20,
    withhold_tax: true,
    payout_schedule: 'Bi-Weekly',
    primary_gateway: 'Stripe',
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Gateway & Schedules */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-emerald-900/30 rounded-lg text-emerald-400">
              <CreditCardIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Gateway & Schedules</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Primary Payment Gateway</label>
              <div className="grid grid-cols-3 gap-2">
                {['Stripe', 'PayPal', 'Crypto'].map((gateway) => (
                  <button
                    key={gateway}
                    onClick={() => setSettings({ ...settings, primary_gateway: gateway })}
                    className={`py-2 text-sm rounded-lg border font-medium transition-colors ${
                      settings.primary_gateway === gateway
                        ? 'bg-primary-900/50 border-primary-500 text-primary-400'
                        : 'bg-gray-900/50 border-gray-700 text-gray-400 hover:border-gray-500'
                    }`}
                  >
                    {gateway}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Automated Payout Schedule</label>
              <select
                value={settings.payout_schedule}
                onChange={(e) => setSettings({ ...settings, payout_schedule: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500 appearance-none"
              >
                <option>Weekly</option>
                <option>Bi-Weekly</option>
                <option>Monthly</option>
                <option>Manual Only</option>
              </select>
            </div>
          </div>
        </div>

        {/* Fees & Taxes */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-orange-900/30 rounded-lg text-orange-400">
              <DocumentChartBarIcon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white">Fees & Taxes</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Platform Commission Fee (%)</label>
              <div className="relative">
                <input
                  type="number"
                  value={settings.platform_commission}
                  onChange={(e) => setSettings({ ...settings, platform_commission: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 pr-8 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <span className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500">%</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Automatic Tax Withholding</label>
                <p className="text-xs text-gray-500">Calculate and withhold applicable taxes from payouts</p>
              </div>
              <button
                type="button"
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${settings.withhold_tax ? 'bg-primary-500' : 'bg-gray-700'}`}
                onClick={() => setSettings({ ...settings, withhold_tax: !settings.withhold_tax })}
              >
                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${settings.withhold_tax ? 'translate-x-5' : 'translate-x-0'}`} />
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
