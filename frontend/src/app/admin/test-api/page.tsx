'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

export default function TestApiPage() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const user = useAuthStore((state) => state.user);

  const testEndpoint = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      console.log('Testing /admin/users endpoint...');
      console.log('Current user:', user);
      console.log('Token:', localStorage.getItem('access_token')?.substring(0, 50));
      
      const response = await api.get('/admin/users');
      console.log('Response:', response.data);
      setResult(response.data);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F172A] p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-4">API Test Page</h1>
        
        <div className="bg-[#1E293B] p-6 rounded-lg border border-[#334155] mb-4">
          <h2 className="text-lg font-semibold text-white mb-2">Current User</h2>
          <pre className="text-sm text-[#94A3B8] bg-[#0F172A] p-4 rounded overflow-auto">
            {JSON.stringify(user, null, 2)}
          </pre>
        </div>

        <button
          onClick={testEndpoint}
          disabled={loading}
          className="bg-[#EF2330] hover:bg-[#DC2026] text-white px-6 py-3 rounded-lg font-semibold disabled:opacity-50 mb-4"
        >
          {loading ? 'Testing...' : 'Test /admin/users Endpoint'}
        </button>

        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-200 p-4 rounded-lg mb-4">
            <h3 className="font-semibold mb-2">Error:</h3>
            <pre className="text-sm overflow-auto">{error}</pre>
          </div>
        )}

        {result && (
          <div className="bg-[#1E293B] p-6 rounded-lg border border-[#334155]">
            <h2 className="text-lg font-semibold text-white mb-2">Result:</h2>
            <pre className="text-sm text-[#94A3B8] bg-[#0F172A] p-4 rounded overflow-auto max-h-96">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
