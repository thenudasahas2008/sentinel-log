import React from 'react';
import { Shield, Code, Terminal, Award, GitBranch, Heart } from 'lucide-react';

export const About: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl font-mono text-xs">
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-8 shadow-2xl relative overflow-hidden">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 rounded-xl bg-cyan-950 border border-cyan-500/50 flex items-center justify-center text-cyan-400">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-100 font-sans">
              SENTINEL<span className="text-cyan-400">LOG</span>
            </h2>
            <p className="text-slate-400 text-xs">
              Advanced Security Log Intelligence &amp; Behavioral Threat Detection Platform &bull; v2.4.0
            </p>
          </div>
        </div>

        <p className="text-slate-300 leading-relaxed text-sm font-sans mb-6">
          SentinelLog is an enterprise-grade security intelligence platform built to parse, normalize, and correlate
          heterogeneous security telemetry across multi-cloud and on-premise environments. Operating with zero external telemetry leakage,
          it provides deterministic sliding-window detection for 10 distinct MITRE ATT&amp;CK adversary behaviors.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-6 border-t border-slate-800">
          <div className="space-y-2">
            <h4 className="text-slate-200 font-bold uppercase tracking-wider flex items-center gap-1.5 text-cyan-400">
              <Code className="w-4 h-4" /> Core Architecture
            </h4>
            <ul className="text-slate-400 space-y-1">
              <li>&bull; Backend: Python 3.11+ / FastAPI / SQLAlchemy 2 / Pydantic</li>
              <li>&bull; Database: SQLite (zero-config) &bull; PostgreSQL enterprise ready</li>
              <li>&bull; Cryptography: Argon2id password hashing &bull; HS256 JWT tokens</li>
              <li>&bull; Frontend: React 18 / TypeScript / Vite / Tailwind CSS / Recharts</li>
              <li>&bull; Live Telemetry: Native WebSockets async pipeline</li>
            </ul>
          </div>

          <div className="space-y-2">
            <h4 className="text-slate-200 font-bold uppercase tracking-wider flex items-center gap-1.5 text-cyan-400">
              <Award className="w-4 h-4" /> Author &amp; Portfolio Credits
            </h4>
            <div className="text-slate-400 space-y-1">
              <div>Creator: <strong className="text-slate-200">Thenuda Sahas</strong></div>
              <div>GitHub: <a href="https://github.com/thenudasahas2008" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">@thenudasahas2008</a></div>
              <div>Repository: <a href="https://github.com/thenudasahas2008/sentinel-log" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">thenudasahas2008/sentinel-log</a></div>
              <div>License: <strong className="text-slate-200">MIT Open Source License</strong></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
