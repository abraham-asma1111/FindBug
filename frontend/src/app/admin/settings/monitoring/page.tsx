'use client';

import React, { useState, useEffect } from 'react';
import api from '@/lib/api';

type Settings = {
  log_level: string;
  alert_email: string;
  enable_slack_alerts: boolean;
};

const DEFAULTS: Settings = {
  log_level: 'INFO',
  alert_email: 'alerts@findbug.et',
  enable_slack_alerts: false,
};

const LOG_LEVEL_OPTIONS = [
  { value: 'DEBUG', label: 'DEBUG - Verbose logging' },
  { value: 'INFO',  label: 'INFO - Standard logging' },
  { value: 'WARN',  label: 'WARN - Warnings and Errors only' },
  { value: 'ERROR', label: 'ERROR - Critical errors only' },
];

export default function MonitoringAuditPage() {
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
        log_level:           data.log_level           ?? DEFAULTS.log_level,
        alert_email:         data.alert_email         ?? DEFAULTS.alert_email,
        enable_slack_alerts: data.enable_slack_alerts ?? DEFAULTS.enable_slack_alerts,
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
          log_level:           { value: settings.log_level,           type: 'string',  is_public: false },
          alert_email:         { value: settings.alert_email,         type: 'string',  is_public: false },
          enable_slack_alerts: { value: settings.enable_slack_alerts, type: 'boolean', is_public: false },
        },
      });
      setMsg({ type: 'success', text: 'Monitoring & Audit settings saved.' });
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
        {/* Logging Configuration */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Logging Configuration</h3>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Application Log Level</label>
              <select
                value={settings.log_level}
                onChange={e => setSettings(s => ({ ...s, log_level: e.target.value }))}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {LOG_LEVEL_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Alert & Incident Responses */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Alert & Incident Responses</h3>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Critical Alerts Email</label>
              <input
                type="email"
                value={settings.alert_email}
                onChange={e => setSettings(s => ({ ...s, alert_email: e.target.value }))}
                placeholder="alerts@yourdomain.com"
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Enable Slack Alerts</label>
                <p className="text-xs text-gray-500">Route critical alerts to the #incidents Slack channel</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, enable_slack_alerts: !s.enable_slack_alerts }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.enable_slack_alerts ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${settings.enable_slack_alerts ? 'translate-x-5' : 'translate-x-0'}`} />
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
