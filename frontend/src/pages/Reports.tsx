import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { FileText, Download, Plus, RefreshCw, FileCode, FileSpreadsheet } from 'lucide-react';
import { Modal } from '../components/Modal';

export const Reports: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('SentinelLog Incident Dossier');
  const [reportType, setReportType] = useState('INCIDENT');
  const [format, setFormat] = useState('PDF');
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchReports = async () => {
    try {
      const data = await api.getReports();
      setReports(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    try {
      await api.generateReport({
        title,
        report_type: reportType,
        format
      });
      setIsModalOpen(false);
      fetchReports();
    } catch (err: any) {
      alert(err.message || 'Report generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            SECURITY REPORTING &amp; COMPLIANCE EXPORT
          </h2>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Generate executive summaries, forensic CSV dumps, JSON SIEM exports, and printable PDF threat dossiers
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-black font-semibold text-xs font-mono transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
        >
          <Plus className="w-4 h-4" />
          GENERATE REPORT
        </button>
      </div>

      {/* Reports Archive Table */}
      <div className="bg-[#0d1322] border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase">
                <th className="py-3 px-4">Report UUID</th>
                <th className="py-3 px-4">Title</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">File Size</th>
                <th className="py-3 px-4">Generated At</th>
                <th className="py-3 px-4 text-right">Download</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {reports.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No reports generated yet. Click "Generate Report" above.
                  </td>
                </tr>
              ) : (
                reports.map((rep) => (
                  <tr key={rep.report_uuid} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-4 text-slate-400">{rep.report_uuid}</td>
                    <td className="py-2.5 px-4 font-semibold text-slate-200">{rep.title}</td>
                    <td className="py-2.5 px-4 text-cyan-400">{rep.report_type}</td>
                    <td className="py-2.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        rep.format === 'PDF' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                        rep.format === 'HTML' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                        rep.format === 'JSON' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {rep.format}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {(rep.file_size_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {new Date(rep.created_at).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <a
                        href={`/api/v1/reports/${rep.report_uuid}/download`}
                        download
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 hover:text-cyan-300 font-semibold text-xs transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" />
                        Download
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Generate Report Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="GENERATE SECURITY COMPLIANCE REPORT"
      >
        <form onSubmit={handleGenerate} className="space-y-4 font-mono text-xs">
          <div>
            <label className="block text-slate-400 uppercase mb-1">Report Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 uppercase mb-1">Report Category</label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="INCIDENT">INCIDENT SUMMARY</option>
                <option value="EXECUTIVE">EXECUTIVE BRIEFING</option>
                <option value="AUDIT">COMPLIANCE AUDIT</option>
                <option value="THREAT_INTEL">THREAT INTELLIGENCE</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 uppercase mb-1">Format</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="PDF">PDF (Printable Document)</option>
                <option value="HTML">HTML (Interactive Webpage)</option>
                <option value="JSON">JSON (Machine Readable)</option>
                <option value="CSV">CSV (Spreadsheet Tabular)</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isGenerating}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-semibold rounded-lg disabled:opacity-50"
            >
              {isGenerating ? 'Compiling Dossier...' : 'Generate & Export'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
