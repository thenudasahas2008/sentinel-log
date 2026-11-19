import React from 'react';
import { AlertSeverity } from '../types';

interface Props {
  severity: AlertSeverity | string;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<Props> = ({ severity, size = 'md' }) => {
  const sev = severity.toUpperCase();

  const styles: Record<string, string> = {
    CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/50 shadow-[0_0_10px_rgba(239,68,68,0.2)]',
    HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    MEDIUM: 'bg-amber-500/20 text-amber-400 border-amber-500/50',
    LOW: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    INFO: 'bg-slate-500/20 text-slate-400 border-slate-500/50'
  };

  const currentStyle = styles[sev] || styles.INFO;
  const sizeClasses = size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1 font-mono font-semibold uppercase tracking-wider rounded border ${sizeClasses} ${currentStyle}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${sev === 'CRITICAL' ? 'bg-red-400 animate-pulse' : 'bg-current'}`} />
      {sev}
    </span>
  );
};
