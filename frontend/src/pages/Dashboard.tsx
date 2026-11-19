import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardStats, Alert } from '../types';
import { MetricCard } from '../components/MetricCard';
import { SeverityBadge } from '../components/SeverityBadge';
import {
  ShieldAlert,
  Flame,
  AlertTriangle,
  Globe,
  KeyRound,
  CheckCircle2,
  FolderGit2,
  RefreshCw
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';

interface Props {
  refreshTrigger: number;
  onNavigateToTab: (tab: string) => void;
}

export const Dashboard: React.FC<Props> = ({ refreshTrigger, onNavigateToTab }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [statsData, alertsData] = await Promise.all([
        api.getDashboardStats(),
        api.getAlerts({ limit: 6 })
      ]);
      setStats(statsData);
      setRecentAlerts(alertsData);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  if (isLoading && !stats) {
    return (
      <div className="flex items-center justify-center h-64 text-cyan-400 font-mono">
        <RefreshCw className="w-6 h-6 animate-spin mr-2" />
        LOADING SOC TELEMETRY...
      </div>
    );
  }

  const categoryColors = ['#ef4444', '#f97316', '#eab308', '#06b6d4', '#8b5cf6', '#ec4899'];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            SOC INTELLIGENCE OVERVIEW
            <span className="text-xs font-mono font-normal px-2 py-0.5 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-400">
              REAL-TIME ANALYTICS
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Continuous correlation of Linux SSH, Windows AD, Syslog, and Web Proxy ingress
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          REFRESH
        </button>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Ingested Events"
          value={stats?.total_events.toLocaleString() || '0'}
          subtitle="Processed through multi-layer parsers"
          icon={ShieldAlert}
          variant="cyan"
        />
        <MetricCard
          title="Critical Alerts"
          value={stats?.critical_alerts || '0'}
          subtitle="High-confidence compromise indicators"
          icon={Flame}
          variant="red"
        />
        <MetricCard
          title="Suspicious Remote IPs"
          value={stats?.suspicious_ips_count || '0'}
          subtitle="Distinct external adversaries identified"
          icon={Globe}
          variant="amber"
        />
        <MetricCard
          title="Active Investigations"
          value={stats?.active_investigations || '0'}
          subtitle="Open triage cases"
          icon={FolderGit2}
          variant="emerald"
        />
      </div>

      {/* Threat Timeline & Attack Category Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Timeline (2 cols) */}
        <div className="lg:col-span-2 bg-[#0d1322] border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold font-mono tracking-wide text-slate-200">
              THREAT VELOCITY &amp; AUTH FAILURES (LAST 24H)
            </h3>
            <span className="text-[11px] font-mono text-slate-400">UTC TIMELINE</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.timeline || []}>
                <defs>
                  <linearGradient id="eventGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="failureGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#38bdf8', fontFamily: 'monospace' }}
                />
                <Area type="monotone" dataKey="total_events" name="Total Events" stroke="#06b6d4" fillOpacity={1} fill="url(#eventGradient)" />
                <Area type="monotone" dataKey="failed_logins" name="Failed Logins" stroke="#ef4444" fillOpacity={1} fill="url(#failureGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Attack Category Breakdown (1 col) */}
        <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <h3 className="text-sm font-semibold font-mono tracking-wide text-slate-200 mb-4">
            ATTACK CATEGORY BREAKDOWN
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.attack_distribution || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" fontSize={10} />
                <YAxis dataKey="category" type="category" stroke="#64748b" fontSize={10} width={100} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {(stats?.attack_distribution || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={categoryColors[index % categoryColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Targeted Accounts & Top Suspicious IPs Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Targeted Accounts */}
        <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold font-mono tracking-wide text-slate-200">
              TOP TARGETED USER ACCOUNTS
            </h3>
            <button
              onClick={() => onNavigateToTab('log-explorer')}
              className="text-xs font-mono text-cyan-400 hover:underline"
            >
              EXPLORE LOGS &rarr;
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 uppercase">
                  <th className="pb-2">Account</th>
                  <th className="pb-2">Total Hits</th>
                  <th className="pb-2">Failures</th>
                  <th className="pb-2 text-right">Risk Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(stats?.top_targeted_accounts || []).map((target, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-semibold text-slate-200">{target.username}</td>
                    <td className="py-2.5 text-slate-400">{target.attempt_count}</td>
                    <td className="py-2.5 text-red-400 font-bold">{target.failure_count}</td>
                    <td className="py-2.5 text-right">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        target.status === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/40' :
                        target.status === 'WARN' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {target.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Suspicious IPs */}
        <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold font-mono tracking-wide text-slate-200">
              PERSISTENT ADVERSARY IPS
            </h3>
            <button
              onClick={() => onNavigateToTab('ip-intel')}
              className="text-xs font-mono text-cyan-400 hover:underline"
            >
              IP INTEL &rarr;
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 uppercase">
                  <th className="pb-2">Source IP</th>
                  <th className="pb-2">Failures</th>
                  <th className="pb-2">Alerts</th>
                  <th className="pb-2 text-right">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(stats?.top_suspicious_ips || []).map((ipItem, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-semibold text-cyan-400">
                      <code>{ipItem.ip}</code>
                      {ipItem.is_private && <span className="ml-1 text-[9px] text-slate-500">[LAN]</span>}
                    </td>
                    <td className="py-2.5 text-slate-400">{ipItem.failure_count}</td>
                    <td className="py-2.5 text-orange-400 font-bold">{ipItem.alert_count}</td>
                    <td className="py-2.5 text-right">
                      <SeverityBadge severity={ipItem.highest_severity} size="sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Recent Alerts Feed */}
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold font-mono tracking-wide text-slate-200">
            RECENT HIGH-SEVERITY ALERTS
          </h3>
          <button
            onClick={() => onNavigateToTab('threat-detection')}
            className="text-xs font-mono text-cyan-400 hover:underline"
          >
            ALL ALERTS ({stats?.critical_alerts ? stats.critical_alerts + stats.high_alerts : 0}) &rarr;
          </button>
        </div>
        <div className="space-y-3">
          {recentAlerts.length === 0 ? (
            <div className="text-center py-6 text-xs font-mono text-slate-500">
              No recent alerts recorded. System operating nominal.
            </div>
          ) : (
            recentAlerts.map((alert) => (
              <div
                key={alert.alert_uuid}
                className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 flex items-center justify-between transition-all"
              >
                <div className="flex items-center gap-3">
                  <SeverityBadge severity={alert.severity} size="sm" />
                  <div>
                    <h4 className="text-xs font-semibold text-slate-200">{alert.title}</h4>
                    <p className="text-[11px] font-mono text-slate-500 mt-0.5">
                      Target: <span className="text-slate-300">{alert.target_username || 'N/A'}</span> &bull; 
                      Source: <span className="text-cyan-400">{alert.source_ip || 'N/A'}</span> &bull; 
                      Confidence: <span className="text-emerald-400 font-bold">{Math.round(alert.confidence_score * 100)}%</span>
                    </p>
                  </div>
                </div>
                <div className="text-right font-mono text-[11px] text-slate-500">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
