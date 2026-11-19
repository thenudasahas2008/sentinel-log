import React from 'react';
import { Settings, Shield, Sliders, Database, Server } from 'lucide-react';

export const SystemSettings: React.FC = () => {
  return (
    <div className="space-y-6 font-mono text-xs">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          SYSTEM SETTINGS &amp; DETECTION THRESHOLDS
        </h2>
        <p className="text-slate-400 mt-1">
          Tune behavioral sliding windows, velocity parameters, and local database operational policies
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Detection Engine Parameters */}
        <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-cyan-400 border-b border-slate-800 pb-2">
            <Sliders className="w-4 h-4" />
            DETECTION ENGINE TUNING
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-slate-400 mb-1">SSH Brute-Force Failure Threshold</label>
              <input
                type="number"
                defaultValue={5}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200"
              />
              <span className="text-[10px] text-slate-500">Number of failed authentications required to trigger RULE-001</span>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Brute-Force Sliding Window (Minutes)</label>
              <input
                type="number"
                defaultValue={10}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Password Spray Target User Threshold</label>
              <input
                type="number"
                defaultValue={3}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200"
              />
              <span className="text-[10px] text-slate-500">Distinct accounts attacked by single IP to trigger RULE-002</span>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Impossible Travel Speed Cutoff (km/h)</label>
              <input
                type="number"
                defaultValue={900}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200"
              />
              <span className="text-[10px] text-slate-500">Velocity exceeding standard commercial aircraft travel</span>
            </div>
          </div>
        </div>

        {/* Database & Security Architecture */}
        <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-cyan-400 border-b border-slate-800 pb-2">
            <Database className="w-4 h-4" />
            STORAGE &amp; ARCHITECTURE TELEMETRY
          </div>

          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Database Engine:</span>
              <span className="text-emerald-400 font-bold">SQLite 3 / PostgreSQL Ready</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Password Cryptography:</span>
              <span className="text-cyan-400 font-bold">Argon2id (m=65536, t=3, p=4)</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">JWT Token Expiry:</span>
              <span className="text-slate-200">12 Hours (HS256)</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Rate Limiter:</span>
              <span className="text-slate-200">120 Requests / Minute</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">External Threat Intel Feeds:</span>
              <span className="text-amber-400 font-bold">Disabled by Default (Zero Leaks)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
