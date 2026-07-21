'use client';

import React, { useState, useEffect } from 'react';
import api from '@/lib/api';

type Settings = {
  enforce_strict_tos: boolean;
  require_nda_for_all: boolean;
  global_announcement: string;
};

const DEFAULTS: Settings = {
  enforce_strict_tos: true,
  require_nda_for_all: false,
  global_announcement: '',
};

export default function PlatformGovernancePage() {
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
        enforce_strict_tos:  data.enforce_strict_tos  ?? DEFAULTS.enforce_strict_tos,
        require_nda_for_all: data.require_nda_for_all ?? DEFAULTS.require_nda_for_all,
        global_announcement: data.global_announcement ?? DEFAULTS.global_announcement,
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
          enforce_strict_tos:  { value: settings.enforce_strict_tos,  type: 'boolean', is_public: false },
          require_nda_for_all: { value: settings.require_nda_for_all, type: 'boolean', is_public: false },
          global_announcement: { value: settings.global_announcement, type: 'string',  is_public: true  },
        },
      });
      setMsg({ type: 'success', text: 'Platform settings saved successfully.' });
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
        {/* Global Policies */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Global Policies</h3>
          </div>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Enforce Strict Terms of Service</label>
                <p className="text-xs text-gray-500">Require re-acceptance of TOS on updates</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, enforce_strict_tos: !s.enforce_strict_tos }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.enforce_strict_tos ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${settings.enforce_strict_tos ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-300">Require NDA Platform-Wide</label>
                <p className="text-xs text-gray-500">Default NDA requirement for all new programs</p>
              </div>
              <button
                type="button"
                onClick={() => setSettings(s => ({ ...s, require_nda_for_all: !s.require_nda_for_all }))}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ${settings.require_nda_for_all ? 'bg-primary-500' : 'bg-gray-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${settings.require_nda_for_all ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Platform Communication */}
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-6">
            <h3 className="text-lg font-medium text-white">Platform Communication</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Global Announcement Banner</label>
              <textarea
                value={settings.global_announcement}
                onChange={e => setSettings(s => ({ ...s, global_announcement: e.target.value }))}
                placeholder="Enter a message to display to all users..."
                rows={4}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              />
              <p className="text-xs text-gray-500 mt-1">Leave empty to disable the banner.</p>
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
