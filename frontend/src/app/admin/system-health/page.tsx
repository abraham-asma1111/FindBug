'use client';

import React, { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import api from '@/lib/api';

type SystemHealth = {
  status: string;
  timestamp: string;
  database: { status: string; connection: string; };
  api: { status: string; uptime_seconds: number; uptime_formatted: string; version: string; };
  server: {
    cpu: { usage_percent: number; cores: number; };
    memory: { usage_percent: number; used_gb: number; total_gb: number; };
    disk: { usage_percent: number; used_gb: number; total_gb: number; };
  };
  external_integrations: Array<{ service: string; status: string; latency_ms: number; }>;
};

export default function SystemHealthPage() {
  const user = useAuthStore((state) => state.user);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    try {
      const { data } = await api.get('/admin/system-health');
      setHealth(data);
    } catch (err) {
      console.error('Failed to fetch system health', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    document.documentElement.classList.add('dark');
    fetchHealth();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    return status === 'operational' || status === 'healthy' 
      ? 'bg-emerald-900/30 text-emerald-400 border-emerald-700/50'
      : 'bg-red-900/30 text-red-400 border-red-700/50';
  };

  const ProgressBar = ({ percent, colorClass }: { percent: number; colorClass: string }) => (
    <div className="w-full bg-gray-800 rounded-full h-2 mt-2">
      <div className={`h-2 rounded-full ${colorClass}`} style={{ width: `${percent}%` }}></div>
    </div>
  );

  const getUsageColor = (percent: number) => {
    if (percent > 90) return 'bg-red-500';
    if (percent > 75) return 'bg-amber-500';
    return 'bg-primary-500';
  };

  const getUsageTextColor = (percent: number) => {
    if (percent > 90) return 'text-red-400';
    if (percent > 75) return 'text-amber-400';
    return 'text-primary-400';
  };

  if (loading && !health) {
    return (
      <ProtectedRoute requireRole="admin">
        <PortalShell navItems={getPortalNavItems('admin')} user={user} pageTitle="System Health">
          <div className="flex justify-center items-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          </div>
        </PortalShell>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute requireRole="admin">
      <PortalShell navItems={getPortalNavItems('admin')} user={user} pageTitle="System Health">
        <div className="max-w-7xl mx-auto space-y-8 pb-12 animate-in fade-in duration-500">
          
          {/* Header Banner */}
          <div className={`p-6 rounded-xl border ${health?.status === 'operational' ? 'bg-emerald-900/20 border-emerald-800/50' : 'bg-red-900/20 border-red-800/50'}`}>
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-semibold text-white tracking-tight">
                  {health?.status === 'operational' ? 'All Systems Operational' : 'Degraded Performance'}
                </h2>
                <p className="text-sm text-gray-400 mt-1">
                  Last updated: {new Date(health?.timestamp || '').toLocaleTimeString()}
                </p>
              </div>
              <div className={`px-4 py-1.5 rounded-full text-sm font-medium border ${getStatusColor(health?.status || 'degraded')}`}>
                {health?.status?.toUpperCase()}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Server Resources (Takes up 2 columns on large screens) */}
            <div className="lg:col-span-2 bg-gray-900/50 border border-gray-800/50 rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-medium text-white mb-6">Hardware Utilization</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                
                {/* CPU */}
                <div>
                  <div className="flex justify-between items-end mb-1">
                    <span className="text-sm font-medium text-gray-400">CPU Usage</span>
                    <span className={`text-xl font-semibold ${getUsageTextColor(health?.server.cpu.usage_percent || 0)}`}>
                      {health?.server.cpu.usage_percent.toFixed(1)}%
                    </span>
                  </div>
                  <ProgressBar percent={health?.server.cpu.usage_percent || 0} colorClass={getUsageColor(health?.server.cpu.usage_percent || 0)} />
                  <p className="text-xs text-gray-500 mt-2">{health?.server.cpu.cores} Physical Cores</p>
                </div>

                {/* Memory */}
                <div>
                  <div className="flex justify-between items-end mb-1">
                    <span className="text-sm font-medium text-gray-400">Memory</span>
                    <span className={`text-xl font-semibold ${getUsageTextColor(health?.server.memory.usage_percent || 0)}`}>
                      {health?.server.memory.usage_percent.toFixed(1)}%
                    </span>
                  </div>
                  <ProgressBar percent={health?.server.memory.usage_percent || 0} colorClass={getUsageColor(health?.server.memory.usage_percent || 0)} />
                  <p className="text-xs text-gray-500 mt-2">{health?.server.memory.used_gb} GB / {health?.server.memory.total_gb} GB</p>
                </div>

                {/* Disk */}
                <div>
                  <div className="flex justify-between items-end mb-1">
                    <span className="text-sm font-medium text-gray-400">Storage Volume</span>
                    <span className={`text-xl font-semibold ${getUsageTextColor(health?.server.disk.usage_percent || 0)}`}>
                      {health?.server.disk.usage_percent.toFixed(1)}%
                    </span>
                  </div>
                  <ProgressBar percent={health?.server.disk.usage_percent || 0} colorClass={getUsageColor(health?.server.disk.usage_percent || 0)} />
                  <p className="text-xs text-gray-500 mt-2">{health?.server.disk.used_gb} GB / {health?.server.disk.total_gb} GB</p>
                </div>
                
              </div>
            </div>

            {/* Core Infrastructure */}
            <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-medium text-white mb-6">Core Infrastructure</h3>
              <div className="space-y-6">
                
                <div className="flex justify-between items-center pb-4 border-b border-gray-800">
                  <div>
                    <p className="text-sm font-medium text-gray-300">FastAPI Backend</p>
                    <p className="text-xs text-gray-500 mt-1">Uptime: {health?.api.uptime_formatted}</p>
                  </div>
                  <div className={`text-xs px-2.5 py-1 rounded-full border ${getStatusColor(health?.api.status || 'degraded')}`}>
                    {health?.api.status.toUpperCase()}
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm font-medium text-gray-300">PostgreSQL Primary</p>
                    <p className="text-xs text-gray-500 mt-1">Connection: Established</p>
                  </div>
                  <div className={`text-xs px-2.5 py-1 rounded-full border ${getStatusColor(health?.database.status || 'degraded')}`}>
                    {health?.database.status.toUpperCase()}
                  </div>
                </div>

              </div>
            </div>

          </div>

          {/* External Integrations */}
          <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-medium text-white mb-6">Third-Party Integrations</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {health?.external_integrations.map((integration, idx) => (
                <div key={idx} className="bg-gray-800/30 border border-gray-700/50 rounded-lg p-5">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="text-sm font-medium text-gray-300">{integration.service}</h4>
                    <div className={`w-2 h-2 rounded-full ${integration.status === 'operational' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]'}`}></div>
                  </div>
                  <div className="flex justify-between items-end">
                    <p className="text-xs text-gray-500 uppercase tracking-wider">{integration.status}</p>
                    <p className="text-sm font-medium text-gray-400">{integration.latency_ms}ms ping</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </PortalShell>
    </ProtectedRoute>
  );
}
