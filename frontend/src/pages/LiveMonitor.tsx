import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import { api } from '../services/api';
import { SecurityEvent } from '../types';
import { Radio, Pause, Play, Trash2, Filter } from 'lucide-react';

export const LiveMonitor: React.FC = () => {
  const { isConnected, isPaused, togglePause, lastMessage } = useWebSocket();
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [filterType, setFilterType] = useState<string>('ALL');

  useEffect(() => {
    // Initial fetch of recent 25 events to populate stream
    api.getEvents({ limit: 25 }).then(setEvents).catch(console.error);
  }, []);

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'NEW_EVENT' && lastMessage.event) {
      setEvents(prev => [lastMessage.event, ...prev.slice(0, 100)]);
    }
  }, [lastMessage]);

  const clearStream = () => setEvents([]);

  const filteredEvents = events.filter(e => {
    if (filterType === 'FAILURES') return e.status === 'FAILURE';
    if (filterType === 'SUCCESS') return e.status === 'SUCCESS';
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            LIVE SECURITY EVENT MONITOR
            <span className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`} />
          </h2>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Real-time streaming ingestion pipeline connected via WebSocket (ws://localhost:8000/api/v1/ws/live)
          </p>
        </div>

        {/* Action Toolbar */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs font-mono">
            <button
              onClick={() => setFilterType('ALL')}
              className={`px-2.5 py-1 rounded ${filterType === 'ALL' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400'}`}
            >
              ALL
            </button>
            <button
              onClick={() => setFilterType('FAILURES')}
              className={`px-2.5 py-1 rounded ${filterType === 'FAILURES' ? 'bg-red-500/20 text-red-400' : 'text-slate-400'}`}
            >
              FAILURES ONLY
            </button>
            <button
              onClick={() => setFilterType('SUCCESS')}
              className={`px-2.5 py-1 rounded ${filterType === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400'}`}
            >
              SUCCESS ONLY
            </button>
          </div>

          <button
            onClick={togglePause}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono font-medium transition-all ${
              isPaused
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-400'
                : 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
            }`}
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
            {isPaused ? 'RESUME STREAM' : 'PAUSE'}
          </button>

          <button
            onClick={clearStream}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-mono text-slate-400 hover:text-red-400 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            CLEAR
          </button>
        </div>
      </div>

      {/* Live Stream Terminal Box */}
      <div className="bg-[#0a0e1a] border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
        <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between text-xs font-mono text-slate-500">
          <span>EVENT STREAM ({filteredEvents.length} BUFFERED)</span>
          <span>AUTOSCROLL: {isPaused ? 'HALTED' : 'ACTIVE'}</span>
        </div>

        <div className="p-4 space-y-2 max-h-[600px] overflow-y-auto font-mono text-xs">
          {filteredEvents.length === 0 ? (
            <div className="text-center py-16 text-slate-600">
              [STREAM IDLE] Waiting for incoming logs or click "LOAD DEMO ATTACKS" in header.
            </div>
          ) : (
            filteredEvents.map((ev) => (
              <div
                key={ev.event_uuid}
                className="p-2.5 rounded bg-[#0d1322] border border-slate-800/80 hover:border-slate-700 flex items-start gap-4 transition-all"
              >
                <span className="text-slate-500 shrink-0">
                  {new Date(ev.timestamp).toLocaleTimeString()}
                </span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] shrink-0 font-bold ${
                  ev.status === 'FAILURE' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                  ev.status === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                  'bg-slate-800 text-slate-400'
                }`}>
                  {ev.status}
                </span>
                <span className="text-cyan-400 shrink-0 font-semibold">
                  [{ev.event_type}]
                </span>
                <span className="text-slate-300 shrink-0">
                  IP: <code className="text-slate-200">{ev.source_ip || 'N/A'}</code>
                </span>
                <span className="text-slate-300 shrink-0">
                  User: <code className="text-slate-200">{ev.username || 'unknown'}</code>
                </span>
                <span className="text-slate-500 truncate flex-1">
                  {ev.raw_log}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
