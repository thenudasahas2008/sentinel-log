import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SecurityEvent } from '../types';
import { FileSearch, Upload, Search, Filter, RefreshCw, CheckCircle2 } from 'lucide-react';
import { Modal } from '../components/Modal';

export const LogExplorer: React.FC = () => {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [parserFilter, setParserFilter] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const fetchEvents = async () => {
    setIsLoading(true);
    try {
      const params: Record<string, any> = { limit: 100 };
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (parserFilter) params.event_type = parserFilter;
      const data = await api.getEvents(params);
      setEvents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [statusFilter, parserFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvents();
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploadStatus('Processing and streaming logs...');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const result = await api.uploadLogFile(formData);
      setUploadStatus(`Success! Ingested ${result.successful_records} records. ${result.alerts_generated} alerts generated.`);
      setTimeout(() => {
        setIsUploadModalOpen(false);
        setSelectedFile(null);
        setUploadStatus(null);
        fetchEvents();
      }, 1500);
    } catch (err: any) {
      setUploadStatus(`Error: ${err.message || 'Ingestion failed'}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            LOG EXPLORER
            <span className="text-xs font-mono text-cyan-400">({events.length} RECORDS LOADED)</span>
          </h2>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Search, filter, and inspect normalized security events across Linux, Windows, Web, and Syslog sources
          </p>
        </div>

        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-black font-semibold text-xs font-mono transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
        >
          <Upload className="w-4 h-4" />
          INGEST LOG FILE
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-4 flex flex-wrap items-center gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[280px] relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by IP, username, hostname, or raw log contents..."
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
          />
        </form>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
        >
          <option value="">Status: All</option>
          <option value="FAILURE">Status: FAILURE</option>
          <option value="SUCCESS">Status: SUCCESS</option>
        </select>

        <select
          value={parserFilter}
          onChange={(e) => setParserFilter(e.target.value)}
          className="px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
        >
          <option value="">Log Type: All</option>
          <option value="SSH_AUTH">SSH Auth</option>
          <option value="SYSLOG">Syslog</option>
          <option value="WIN_EVENT_4625">Win Event 4625 (Logon Fail)</option>
          <option value="WIN_EVENT_4624">Win Event 4624 (Logon OK)</option>
          <option value="NGINX_ACCESS">Nginx Access</option>
          <option value="APACHE_ACCESS">Apache Access</option>
          <option value="CSV_AUTH">CSV Ingested</option>
        </select>

        <button
          onClick={fetchEvents}
          className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-cyan-400"
          title="Reload"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Events Table */}
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase">
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Source IP</th>
                <th className="py-3 px-4">Username</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Service</th>
                <th className="py-3 px-4">Raw Log Line</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {events.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No security events match the current criteria.
                  </td>
                </tr>
              ) : (
                events.map((ev) => (
                  <tr key={ev.event_uuid} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">
                      {new Date(ev.timestamp).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ev.status === 'FAILURE' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                        ev.status === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {ev.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-cyan-400 whitespace-nowrap">
                      {ev.source_ip || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-200 font-semibold whitespace-nowrap">
                      {ev.username || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">
                      {ev.event_type}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {ev.service || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-500 max-w-md truncate" title={ev.raw_log}>
                      {ev.raw_log}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload File Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="INGEST SECURITY LOG FILE"
      >
        <form onSubmit={handleFileUpload} className="space-y-4 font-mono text-xs">
          <p className="text-slate-400">
            Select a raw log file (Linux SSH auth.log, Syslog, JSON, CSV, Windows Events export, Apache/Nginx).
            Encoding and format are automatically identified and verified with SHA-256 deduplication.
          </p>

          <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:border-cyan-500/60 transition-colors">
            <input
              type="file"
              id="file-upload"
              onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <Upload className="w-8 h-8 text-cyan-400 mb-2" />
              <span className="text-slate-200 font-semibold">
                {selectedFile ? selectedFile.name : 'Click to choose file or drag and drop'}
              </span>
              <span className="text-slate-500 text-[10px] mt-1">
                Supported: .log, .txt, .json, .csv, .syslog (Up to 50MB)
              </span>
            </label>
          </div>

          {uploadStatus && (
            <div className={`p-3 rounded-lg border ${
              uploadStatus.startsWith('Success') ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
              uploadStatus.startsWith('Error') ? 'bg-red-500/10 border-red-500/30 text-red-400' :
              'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
            }`}>
              {uploadStatus}
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setIsUploadModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedFile}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-semibold rounded-lg disabled:opacity-50"
            >
              Ingest &amp; Analyze
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
