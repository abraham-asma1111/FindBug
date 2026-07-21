'use client';

import React, { useState, useEffect } from 'react';
import api from '@/lib/api';

type Settings = {
  enforce_gdpr: boolean;
  data_retention_days: number;
  encrypt_audit_logs: boolean;
};

const DEFAULTS: Settings = {
  enforce_gdpr: true,
  data_retention_days: 365,
  encrypt_audit_logs: true,
};

const RETENTION_OPTIONS = [
  { value: 30,    label: '30 Days' },
  { value: 90,    label: '90 Days' },
  { value: 365,   label: '1 Year'  },
  { value: 1825,  label: '5 Years' },
  { value: -1,    label: 'Indefinitely' },
];

export default function SecurityCompliancePage() {
  const [settings, setSettings] = useState<Settings>(DEFAULTS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState({ type: '', text: '' });

  useEffect(() => { fetchSettings(); }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const { data } = await api.get('/admin/settings');
      setSettings({
        enforce_gdpr:        data.enforce_gdpr        ?? DEFAULTS.enforce_gdpr,
        data_retention_days: data.data_retention_days  ?? DEFAULTS.data_retention_days,
        encrypt_audit_logs:  data.encrypt_audit_logs   ?? DEFAULTS.encrypt_audit_logs,
      });
    } catch { /* use defaults */ }
    finally { setLoading(false); }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMsg({ type: '', text: '' });
      await api.put('/admin/settings/bulk', {
        settings: {
          enforce_gdpr:        { value: settings.enforce_gdpr,        type: 'boolean' },
          data_retention_days: { value: settings.data_retention_days, type: 'integer' },
          encrypt_audit_logs:  { value: settings.encrypt_audit_logs,  type: 'boolean' },
        },
      });
      setMsg({ type: 'success', text: 'Security & Compliance settings saved.' });
    } catch {
      setMsg({ type: 'error', text: 'Failed to save settings. Please try again.' });
    } finally {
      setSaving(false);
      setTimeout(() => setMsg({ type: '', text: '' }), 3000);
    }
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500" />
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {msg.text && (
        <div className={`p-4 rounded-lg border text-sm ${msg.type === 'success' ? 'bg-green-900/30 border-green-700 text-green-400' : 'bg-red-900/30 border-red-700 text-red-400'}`}>
          {msg.text}
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Compliance Standards */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Compliance Standards</h3>
          </div>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Enforce Strict GDPR Mode</label>
                <p className="text-xs text-gray-500">Enable features for easy data deletion and consent tracking</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, enforce_gdpr: !s.enforce_gdpr }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.enforce_gdpr ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${settings.enforce_gdpr ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Data Protection */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Data Protection</h3>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Data Retention Period</label>
              <select
                value={settings.data_retention_days}
                onChange={e => setSettings(s => ({ ...s, data_retention_days: parseInt(e.target.value) }))}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {RETENTION_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Encrypt Audit Logs</label>
                <p className="text-xs text-gray-500">Encrypt all platform activity logs at rest</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, encrypt_audit_logs: !s.encrypt_audit_logs }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.encrypt_audit_logs ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${settings.encrypt_audit_logs ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4 border-t border-gray-800">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-6 py-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium transition-colors disabled:opacity-50 shadow-lg shadow-primary-500/20"
        >
          {saving ? <><div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white" /> Saving...</> : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}
