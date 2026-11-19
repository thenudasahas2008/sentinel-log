import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Investigation } from '../types';
import { FolderGit2, Plus, MessageSquare, ShieldAlert, CheckCircle2, RefreshCw } from 'lucide-react';
import { Modal } from '../components/Modal';

export const IncidentInvestigation: React.FC = () => {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedCase, setSelectedCase] = useState<Investigation | null>(null);
  const [newNote, setNewNote] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSeverity, setNewSeverity] = useState('HIGH');
  const [isLoading, setIsLoading] = useState(false);

  const fetchCases = async () => {
    setIsLoading(true);
    try {
      const data = await api.getInvestigations();
      setInvestigations(data);
      if (selectedCase) {
        const refreshed = data.find((c: Investigation) => c.id === selectedCase.id);
        if (refreshed) setSelectedCase(refreshed);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;

    try {
      const created = await api.createInvestigation({
        title: newTitle,
        description: newDesc,
        severity: newSeverity
      });
      setIsCreateModalOpen(false);
      setNewTitle('');
      setNewDesc('');
      fetchCases();
    } catch (err: any) {
      alert(err.message || 'Failed to create case');
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCase || !newNote.trim()) return;

    try {
      await api.addInvestigationNote(selectedCase.id, newNote.trim());
      setNewNote('');
      fetchCases();
    } catch (err: any) {
      alert(err.message || 'Failed to add note');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            INCIDENT INVESTIGATION &amp; TRIAGE
            <span className="text-xs font-mono text-cyan-400">({investigations.length} CASES)</span>
          </h2>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Case management, evidence correlation, containment tracking, and analyst investigation notes
          </p>
        </div>

        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-black font-semibold text-xs font-mono transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
        >
          <Plus className="w-4 h-4" />
          NEW INVESTIGATION
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Case List (1 col) */}
        <div className="bg-[#0d1322] border border-slate-800 rounded-xl p-4 space-y-3 max-h-[700px] overflow-y-auto">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs font-mono text-slate-400">
            <span>ACTIVE CASES</span>
            <button onClick={fetchCases} className="hover:text-cyan-400">
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {investigations.length === 0 ? (
            <div className="text-center py-10 text-xs font-mono text-slate-500">
              No active investigations. Click "New Investigation" or load demo data.
            </div>
          ) : (
            investigations.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedCase(item)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedCase?.id === item.id
                    ? 'bg-cyan-950/30 border-cyan-500/50 text-slate-100'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 mb-1">
                  <span>{item.case_number}</span>
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    item.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                    item.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                    'bg-amber-500/20 text-amber-400'
                  }`}>
                    {item.severity}
                  </span>
                </div>
                <h4 className="text-xs font-semibold line-clamp-1">{item.title}</h4>
                <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span>Status: <strong className="text-cyan-400">{item.status}</strong></span>
                  <span>{new Date(item.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Selected Case Workspace (2 cols) */}
        <div className="lg:col-span-2 bg-[#0d1322] border border-slate-800 rounded-xl p-6 font-mono text-xs">
          {selectedCase ? (
            <div className="space-y-6">
              <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                <div>
                  <span className="text-xs text-cyan-400 font-bold block">{selectedCase.case_number}</span>
                  <h3 className="text-base font-bold text-slate-100 mt-1">{selectedCase.title}</h3>
                  <p className="text-slate-400 mt-1">{selectedCase.description || 'No description provided.'}</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-slate-300">
                  {selectedCase.status}
                </span>
              </div>

              {/* Associated Indicators */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block mb-1">Associated Adversary IPs</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedCase.associated_ips.length === 0 ? (
                      <span className="text-slate-500">None attached</span>
                    ) : (
                      selectedCase.associated_ips.map((ip) => (
                        <span key={ip} className="px-2 py-0.5 rounded bg-slate-800 text-cyan-400 text-[11px]">
                          {ip}
                        </span>
                      ))
                    )}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block mb-1">Target Accounts</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedCase.associated_users.length === 0 ? (
                      <span className="text-slate-500">None attached</span>
                    ) : (
                      selectedCase.associated_users.map((u) => (
                        <span key={u} className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 text-[11px]">
                          {u}
                        </span>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Analyst Investigation Notes Timeline */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-cyan-400" />
                  Analyst Timeline Notes ({selectedCase.notes?.length || 0})
                </h4>

                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {(!selectedCase.notes || selectedCase.notes.length === 0) ? (
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-500 text-center">
                      No investigation notes recorded yet. Add notes below.
                    </div>
                  ) : (
                    selectedCase.notes.map((note) => (
                      <div key={note.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
                        <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                          <span>Analyst ID: {note.author_id}</span>
                          <span>{new Date(note.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-slate-200">{note.content}</p>
                      </div>
                    ))
                  )}
                </div>

                {/* Add Note Form */}
                <form onSubmit={handleAddNote} className="flex gap-2 pt-2">
                  <input
                    type="text"
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Document containment action, evidence discovery, or mitigation step..."
                    className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500 text-xs"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-semibold rounded-lg text-xs"
                  >
                    Post Note
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-24 text-slate-500 space-y-2">
              <FolderGit2 className="w-12 h-12 text-slate-600" />
              <span>Select an investigation case from the left panel to review telemetry.</span>
            </div>
          )}
        </div>
      </div>

      {/* Create Case Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="CREATE NEW INCIDENT INVESTIGATION"
      >
        <form onSubmit={handleCreateCase} className="space-y-4 font-mono text-xs">
          <div>
            <label className="block text-slate-400 uppercase mb-1">Case Title</label>
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g., Investigation: Suspicious SSH Brute-Force against Bastion"
              required
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 uppercase mb-1">Severity</label>
            <select
              value={newSeverity}
              onChange={(e) => setNewSeverity(e.target.value)}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 uppercase mb-1">Incident Description &amp; Scope</label>
            <textarea
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              rows={4}
              placeholder="Initial context, affected systems, observed adversary tactics..."
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-semibold rounded-lg"
            >
              Initialize Case
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
