import React from 'react';
import {
  ShieldAlert,
  Activity,
  FileSearch,
  Crosshair,
  Globe,
  FolderGit2,
  FileText,
  Users,
  ScrollText,
  Settings,
  Info,
  ChevronLeft,
  ChevronRight,
  Radio
} from 'lucide-react';

interface Props {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isCollapsed: boolean;
  setIsCollapsed: (val: boolean) => void;
}

export const Sidebar: React.FC<Props> = ({
  activeTab,
  setActiveTab,
  isCollapsed,
  setIsCollapsed
}) => {
  const navItems = [
    { id: 'dashboard', label: 'SOC Dashboard', icon: Activity },
    { id: 'live-monitor', label: 'Live Event Monitor', icon: Radio, badge: 'LIVE' },
    { id: 'log-explorer', label: 'Log Explorer', icon: FileSearch },
    { id: 'threat-detection', label: 'Threat Detection', icon: Crosshair },
    { id: 'ip-intel', label: 'IP Intelligence', icon: Globe },
    { id: 'investigation', label: 'Incident Triage', icon: FolderGit2 },
    { id: 'reports', label: 'Reports & Export', icon: FileText },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'audit', label: 'Audit Trail', icon: ScrollText },
    { id: 'settings', label: 'System Settings', icon: Settings },
    { id: 'about', label: 'About SentinelLog', icon: Info }
  ];

  return (
    <aside
      className={`bg-[#0a0e1a] border-r border-slate-800/80 flex flex-col transition-all duration-300 z-30 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-9 h-9 rounded-lg bg-cyan-950 border border-cyan-500/50 flex items-center justify-center text-cyan-400 shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-wide bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                SENTINEL<span className="text-slate-100">LOG</span>
              </span>
              <span className="text-[10px] font-mono tracking-widest text-slate-500 uppercase">SecOps v2.4</span>
            </div>
          )}
        </div>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-slate-800/50 rounded-md transition-colors"
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav List */}
      <div className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
              {!isCollapsed && (
                <div className="flex-1 flex items-center justify-between">
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {item.badge}
                    </span>
                  )}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Info */}
      {!isCollapsed && (
        <div className="p-4 border-t border-slate-800/80 text-[11px] font-mono text-slate-500">
          <div>ENGINE: <span className="text-emerald-400">ONLINE</span></div>
          <div>RULES: <span className="text-cyan-400">10 ACTIVE</span></div>
        </div>
      )}
    </aside>
  );
};
