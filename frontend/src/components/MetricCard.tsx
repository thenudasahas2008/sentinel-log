import React from 'react';
import { LucideIcon } from 'lucide-react';

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'cyan' | 'red' | 'amber' | 'emerald' | 'slate';
  trend?: string;
}

export const MetricCard: React.FC<Props> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'cyan',
  trend
}) => {
  const variantStyles = {
    cyan: 'border-cyan-500/30 text-cyan-400 bg-cyan-950/20',
    red: 'border-red-500/30 text-red-400 bg-red-950/20',
    amber: 'border-amber-500/30 text-amber-400 bg-amber-950/20',
    emerald: 'border-emerald-500/30 text-emerald-400 bg-emerald-950/20',
    slate: 'border-slate-700 text-slate-300 bg-slate-900/50'
  };

  return (
    <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all duration-200">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono uppercase tracking-wider text-slate-400">{title}</span>
        <div className={`p-2 rounded-lg border ${variantStyles[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-bold font-mono text-slate-100">{value}</span>
        {trend && (
          <span className="text-xs font-mono text-slate-400">{trend}</span>
        )}
      </div>
      {subtitle && (
        <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
      )}
    </div>
  );
};
