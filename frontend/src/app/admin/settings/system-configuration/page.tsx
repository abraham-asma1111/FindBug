'use client';

import React, { useState, useEffect } from 'react';
import api from '@/lib/api';

type Settings = {
  platform_name: string;
  maintenance_mode: boolean;
  support_email: string;
  smtp_mock_mode: boolean;
};

const DEFAULTS: Settings = {
  platform_name: 'FindBug Platform',
  maintenance_mode: false,
  support_email: 'support@findbug.et',
  smtp_mock_mode: true,
};

export default function SystemConfigurationPage() {
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
        platform_name:    data.platform_name    ?? DEFAULTS.platform_name,
        maintenance_mode: data.maintenance_mode ?? DEFAULTS.maintenance_mode,
        support_email:    data.support_email    ?? DEFAULTS.support_email,
        smtp_mock_mode:   data.smtp_mock_mode   ?? DEFAULTS.smtp_mock_mode,
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
          platform_name:    { value: settings.platform_name,    type: 'string',  is_public: true },
          maintenance_mode: { value: settings.maintenance_mode, type: 'boolean', is_public: true },
          support_email:    { value: settings.support_email,    type: 'string',  is_public: true },
          smtp_mock_mode:   { value: settings.smtp_mock_mode,   type: 'boolean', is_public: false },
        },
      });
      setMsg({ type: 'success', text: 'System configuration saved successfully.' });
    } catch {
      setMsg({ type: 'error', text: 'Failed to save configuration. Please try again.' });
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
        {/* Platform Details */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Platform Details</h3>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Platform Name</label>
              <input
                type="text"
                value={settings.platform_name}
                onChange={e => setSettings(s => ({ ...s, platform_name: e.target.value }))}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Maintenance Mode</label>
                <p className="text-xs text-gray-500">Disable platform access for non-admins</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, maintenance_mode: !s.maintenance_mode }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.maintenance_mode ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${settings.maintenance_mode ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Email Infrastructure */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Email & Communication</h3>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Support Email</label>
              <input
                type="email"
                value={settings.support_email}
                onChange={e => setSettings(s => ({ ...s, support_email: e.target.value }))}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">SMTP Mock Mode</label>
                <p className="text-xs text-gray-500">Output emails to terminal instead of sending</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, smtp_mock_mode: !s.smtp_mock_mode }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.smtp_mock_mode ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${settings.smtp_mock_mode ? 'translate-x-5' : 'translate-x-0'}`} />
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
          {saving ? <><div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white" /> Saving...</> : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
}
