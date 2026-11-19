import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useWebSocket } from '../context/WebSocketContext';
import { LogOut, User as UserIcon, Play, RotateCcw, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

interface Props {
  onRefresh: () => void;
}

export const Header: React.FC<Props> = ({ onRefresh }) => {
  const { user, logout } = useAuth();
  const { isConnected } = useWebSocket();
  const [isDemoLoading, setIsDemoLoading] = React.useState(false);

  const handleGenerateDemo = async () => {
    setIsDemoLoading(true);
    try {
      await api.generateDemoData();
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to generate demo scenario');
    } finally {
      setIsDemoLoading(false);
    }
  };

  const handleResetDemo = async () => {
    if (!confirm('Are you sure you want to purge synthetic demo events and alerts? Production logs will remain safe.')) return;
    setIsDemoLoading(true);
    try {
      await api.resetDemoData();
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to reset demo data');
    } finally {
      setIsDemoLoading(false);
    }
  };

  return (
    <header className="h-16 bg-[#0a0e1a]/95 backdrop-blur border-b border-slate-800/80 px-6 flex items-center justify-between z-20">
      {/* Left: Stream Status & Demo controls */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
          <span className="text-slate-400">STREAM:</span>
          <span className={isConnected ? 'text-emerald-400 font-semibold' : 'text-red-400'}>
            {isConnected ? 'LIVE' : 'DISCONNECTED'}
          </span>
        </div>

        {/* Demo Mode Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleGenerateDemo}
            disabled={isDemoLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-500/40 text-cyan-400 text-xs font-mono font-medium transition-all"
            title="Load synthetic attack scenarios (SSH brute force, spray, takeover)"
          >
            <Play className="w-3.5 h-3.5" />
            {isDemoLoading ? 'GENERATING...' : 'LOAD DEMO ATTACKS'}
          </button>

          <button
            onClick={handleResetDemo}
            disabled={isDemoLoading}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 text-xs font-mono transition-all"
            title="Purge all synthetic demo data"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            RESET DEMO
          </button>
        </div>
      </div>

      {/* Right: User Profile & Logout */}
      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="flex flex-col text-right">
              <span className="text-sm font-medium text-slate-200">{user.full_name || user.username}</span>
              <span className="text-[10px] font-mono font-semibold uppercase text-cyan-400">{user.role}</span>
            </div>
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <UserIcon className="w-4 h-4" />
            </div>
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <span className="text-xs font-mono text-slate-500">ANALYST GUEST MODE</span>
        )}
      </div>
    </header>
  );
};
