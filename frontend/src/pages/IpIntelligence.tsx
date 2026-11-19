import React, { useState } from 'react';
import { api } from '../services/api';
import { IpIntelligence } from '../types';
import { Globe, Search, Shield, AlertTriangle, CheckCircle, Crosshair, MapPin } from 'lucide-react';

export const IpIntelligencePage: React.FC = () => {
  const [ipInput, setIpInput] = useState('194.26.29.112');
  const [data, setData] = useState<IpIntelligence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!ipInput.trim()) return;

    setIsLoading(true);
    setError(null);
    try {
      const res = await api.lookupIp(ipInput.trim());
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to inspect IP address');
      setData(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          IP INTELLIGENCE &amp; REPUTATION ENGINE
        </h2>
        <p className="text-xs font-mono text-slate-400 mt-1">
          Empirical IP profiling, RFC 1918 classification, local threat score derivation, and targeted attack history
        </p>
      </div>

      {/* Search Input */}
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5 shadow-xl">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Globe className="w-5 h-5 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              value={ipInput}
              onChange={(e) => setIpInput(e.target.value)}
              placeholder="Enter IPv4 or IPv6 address (e.g., 194.26.29.112, 185.220.101.5, 10.0.0.1)..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-700/80 rounded-lg text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-black font-semibold text-xs font-mono rounded-lg transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)] disabled:opacity-50"
          >
            {isLoading ? 'ANALYZING...' : 'INSPECT IP'}
          </button>
        </form>

        {/* Quick Search Chips */}
        <div className="mt-3 flex items-center gap-2 text-xs font-mono text-slate-500">
          <span>Quick Lookup:</span>
          {['194.26.29.112', '185.220.101.5', '45.142.195.88', '192.168.1.1'].map((sampleIp) => (
            <button
              key={sampleIp}
              type="button"
              onClick={() => {
                setIpInput(sampleIp);
                api.lookupIp(sampleIp).then(setData).catch(console.error);
              }}
              className="px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-cyan-400"
            >
              {sampleIp}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono">
          {error}
        </div>
      )}

      {/* IP Intelligence Report Card */}
      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-mono">
          {/* Main Profile & Threat Score */}
          <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs text-slate-500 uppercase tracking-wider">Classification</span>
                <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                  data.classification === 'HIGH_RISK' ? 'bg-red-500/20 text-red-400 border border-red-500/50' :
                  data.classification === 'SUSPICIOUS' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50' :
                  'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50'
                }`}>
                  {data.classification}
                </span>
              </div>

              <div className="my-6 text-center">
                <div className="text-5xl font-bold tracking-tight mb-2 text-slate-100">
                  {data.threat_score}<span className="text-xl text-slate-500">/100</span>
                </div>
                <span className="text-xs text-slate-400 uppercase tracking-widest">
                  Derived Local Threat Score
                </span>
              </div>

              <div className="space-y-2 pt-4 border-t border-slate-800 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">IP Version:</span>
                  <span className="text-slate-300">IPv{data.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Network Type:</span>
                  <span className="text-slate-300">{data.is_private ? 'Private (RFC 1918)' : 'Public External'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Loopback / Local:</span>
                  <span className="text-slate-300">{data.is_loopback ? 'Yes' : 'No'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Activity Telemetry */}
          <div className="lg:col-span-2 bg-[#0d1322] border border-slate-800 rounded-xl p-5 space-y-6">
            <h3 className="text-sm font-semibold tracking-wide text-slate-200">
              LOCAL TELEMETRY &amp; REPUTATION HISTORY
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">Total Events</span>
                <span className="text-xl font-bold text-slate-200">{data.reputation_history.total_events}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">Failed Attempts</span>
                <span className="text-xl font-bold text-red-400">{data.reputation_history.failed_attempts}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">Total Alerts</span>
                <span className="text-xl font-bold text-orange-400">{data.reputation_history.total_alerts}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">Critical Alerts</span>
                <span className="text-xl font-bold text-red-500">{data.reputation_history.critical_alerts}</span>
              </div>
            </div>

            <div className="space-y-4 pt-2">
              <div>
                <span className="text-xs text-slate-400 uppercase tracking-wider block mb-2">Targeted Accounts</span>
                <div className="flex flex-wrap gap-2">
                  {data.targeted_accounts.length === 0 ? (
                    <span className="text-xs text-slate-500">None observed</span>
                  ) : (
                    data.targeted_accounts.map((user) => (
                      <span key={user} className="px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-xs text-cyan-300">
                        {user}
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div>
                <span className="text-xs text-slate-400 uppercase tracking-wider block mb-2">Triggered Detection Rules</span>
                <div className="flex flex-wrap gap-2">
                  {data.detected_rules.length === 0 ? (
                    <span className="text-xs text-slate-500">No detection rules triggered</span>
                  ) : (
                    data.detected_rules.map((rule) => (
                      <span key={rule} className="px-2.5 py-1 rounded bg-red-950/30 border border-red-500/40 text-xs text-red-400">
                        {rule}
                      </span>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
