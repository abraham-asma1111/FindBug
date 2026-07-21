'use client';

import React, { useState, useEffect } from 'react';
import api from '@/lib/api';

type Settings = {
  require_mfa: boolean;
  session_timeout: number;
};

const DEFAULTS: Settings = { require_mfa: true, session_timeout: 30 };

export default function AccessControlPage() {
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
        require_mfa:     data.require_mfa     ?? DEFAULTS.require_mfa,
        session_timeout: data.session_timeout  ?? DEFAULTS.session_timeout,
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
          require_mfa:     { value: settings.require_mfa,    type: 'boolean' },
          session_timeout:  { value: settings.session_timeout, type: 'integer' },
        },
      });
      setMsg({ type: 'success', text: 'Access control settings saved successfully.' });
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
        {/* Authentication Policies */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Authentication Policies</h3>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Require MFA for All Users</label>
                <p className="text-xs text-gray-500">Enforce Multi-Factor Authentication</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, require_mfa: !s.require_mfa }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.require_mfa ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ${settings.require_mfa ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Session Timeout (Minutes)</label>
              <input
                type="number"
                min={5}
                max={1440}
                value={settings.session_timeout}
                onChange={e => setSettings(s => ({ ...s, session_timeout: parseInt(e.target.value) || 30 }))}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Role Management (read-only overview) */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Role Overview</h3>
          </div>
          <div className="space-y-3">
            {[
              { label: 'Researcher',        badge: 'Standard',   color: 'green'  },
              { label: 'Organization',      badge: 'Standard',   color: 'blue'   },
              { label: 'Triage Specialist', badge: 'Privileged', color: 'purple' },
              { label: 'Finance Officer',   badge: 'Privileged', color: 'orange' },
              { label: 'Admin',             badge: 'Super',      color: 'red'    },
            ].map(role => (
              <div key={role.label} className="flex justify-between items-center p-3 bg-gray-900/50 border border-gray-700 rounded-lg">
                <span className="text-white text-sm font-medium">{role.label}</span>
                <span className={`text-xs px-2 py-1 rounded-full bg-${role.color}-900/30 text-${role.color}-400 border border-${role.color}-800/50`}>
                  {role.badge}
                </span>
              </div>
            ))}
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
