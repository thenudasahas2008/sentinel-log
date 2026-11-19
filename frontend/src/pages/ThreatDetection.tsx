import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Alert, AlertStatus, AlertSeverity } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { Crosshair, ShieldAlert, CheckCircle2, Clock, Eye, XCircle, Search, RefreshCw } from 'lucide-react';
import { Modal } from '../components/Modal';

export const ThreatDetection: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const params: Record<string, any> = { limit: 100 };
      if (severityFilter) params.severity = severityFilter;
      if (statusFilter) params.status = statusFilter;
      const data = await api.getAlerts(params);
      setAlerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter, statusFilter]);

  const handleStatusUpdate = async (status: AlertStatus) => {
    if (!selectedAlert) return;
    try {
      const updated = await api.updateAlertStatus(selectedAlert.alert_uuid, status, resolutionNotes);
      setAlerts(prev => prev.map(a => a.alert_uuid === updated.alert_uuid ? updated : a));
      setSelectedAlert(updated);
      setResolutionNotes('');
    } catch (err: any) {
      alert(err.message || 'Status update failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            THREAT DETECTION &amp; ALERTS
            <span className="text-xs font-mono text-cyan-400">({alerts.length} ALERTS)</span>
          </h2>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Real-time rule engine matches with documented confidence calculations and defensive playbooks
          </p>
        </div>

        <button
          onClick={fetchAlerts}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          REFRESH
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-4 flex items-center gap-4">
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
        >
          <option value="">Severity: All</option>
          <option value="CRITICAL">Severity: CRITICAL</option>
          <option value="HIGH">Severity: HIGH</option>
          <option value="MEDIUM">Severity: MEDIUM</option>
          <option value="LOW">Severity: LOW</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
        >
          <option value="">Status: All</option>
          <option value="NEW">Status: NEW</option>
          <option value="INVESTIGATING">Status: INVESTIGATING</option>
          <option value="RESOLVED">Status: RESOLVED</option>
          <option value="FALSE_POSITIVE">Status: FALSE POSITIVE</option>
        </select>
      </div>

      {/* Alerts Table */}
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase">
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Threat Title</th>
                <th className="py-3 px-4">Source IP</th>
                <th className="py-3 px-4">Target User</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    No threat alerts matching the selected filters.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.alert_uuid} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-4">
                      <SeverityBadge severity={alert.severity} size="sm" />
                    </td>
                    <td className="py-2.5 px-4 font-semibold text-slate-200">
                      {alert.title}
                      {alert.is_synthetic && (
                        <span className="ml-2 text-[9px] px-1 py-0.2 rounded bg-violet-950 border border-violet-500/40 text-violet-300">
                          DEMO
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-cyan-400">
                      {alert.source_ip || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-300">
                      {alert.target_username || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-4 font-bold text-emerald-400">
                      {Math.round(alert.confidence_score * 100)}%
                    </td>
                    <td className="py-2.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        alert.status === 'NEW' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                        alert.status === 'INVESTIGATING' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        alert.status === 'RESOLVED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {alert.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Inspection Modal */}
      {selectedAlert && (
        <Modal
          isOpen={!!selectedAlert}
          onClose={() => setSelectedAlert(null)}
          title={`ALERT DOSSIER: ${selectedAlert.alert_uuid}`}
        >
          <div className="space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="flex items-center gap-3">
                <SeverityBadge severity={selectedAlert.severity} />
                <span className="text-sm font-bold text-slate-100">{selectedAlert.title}</span>
              </div>
              <span className="text-emerald-400 font-bold">
                CONFIDENCE: {Math.round(selectedAlert.confidence_score * 100)}%
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 uppercase block text-[10px]">Detection Rule</span>
                <span className="text-slate-200 font-semibold">{selectedAlert.detection_rule_name}</span>
                <span className="text-slate-400 block text-[11px] mt-0.5">ID: {selectedAlert.rule_id}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 uppercase block text-[10px]">Target &amp; Origin</span>
                <span className="text-slate-200 font-semibold">User: {selectedAlert.target_username || 'N/A'}</span>
                <span className="text-cyan-400 block text-[11px] mt-0.5">IP: {selectedAlert.source_ip || 'N/A'}</span>
              </div>
            </div>

            <div>
              <span className="text-slate-400 uppercase tracking-wider block mb-1">Recommended Defensive Action</span>
              <div className="p-3 rounded-lg bg-red-950/20 border border-red-500/30 text-red-300">
                {selectedAlert.recommended_action}
              </div>
            </div>

            <div>
              <span className="text-slate-400 uppercase tracking-wider block mb-1">Empirical Evidence Data</span>
              <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 overflow-x-auto max-h-48 text-[11px]">
                {JSON.stringify(selectedAlert.evidence, null, 2)}
              </pre>
            </div>

            {/* Triage Status Update */}
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <span className="text-slate-400 uppercase tracking-wider block">SOC Analyst Triage</span>
              <input
                type="text"
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
                placeholder="Resolution / triage investigation notes..."
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => handleStatusUpdate('INVESTIGATING')}
                  className="px-3 py-1.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-400 hover:bg-amber-500/30"
                >
                  Mark Investigating
                </button>
                <button
                  onClick={() => handleStatusUpdate('RESOLVED')}
                  className="px-3 py-1.5 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/30"
                >
                  Mark Resolved
                </button>
                <button
                  onClick={() => handleStatusUpdate('FALSE_POSITIVE')}
                  className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-400 hover:bg-slate-700"
                >
                  False Positive
                </button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
