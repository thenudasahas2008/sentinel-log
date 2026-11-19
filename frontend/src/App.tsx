import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { LiveMonitor } from './pages/LiveMonitor';
import { LogExplorer } from './pages/LogExplorer';
import { ThreatDetection } from './pages/ThreatDetection';
import { IpIntelligencePage } from './pages/IpIntelligence';
import { IncidentInvestigation } from './pages/IncidentInvestigation';
import { Reports } from './pages/Reports';
import { UserManagement } from './pages/UserManagement';
import { AuditLogs } from './pages/AuditLogs';
import { SystemSettings } from './pages/SystemSettings';
import { About } from './pages/About';

export const App: React.FC = () => {
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  if (!token) {
    return <Login />;
  }

  const renderContent = (refreshTrigger: number) => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard refreshTrigger={refreshTrigger} onNavigateToTab={setActiveTab} />;
      case 'live-monitor':
        return <LiveMonitor />;
      case 'log-explorer':
        return <LogExplorer />;
      case 'threat-detection':
        return <ThreatDetection />;
      case 'ip-intel':
        return <IpIntelligencePage />;
      case 'investigation':
        return <IncidentInvestigation />;
      case 'reports':
        return <Reports />;
      case 'users':
        return <UserManagement />;
      case 'audit':
        return <AuditLogs />;
      case 'settings':
        return <SystemSettings />;
      case 'about':
        return <About />;
      default:
        return <Dashboard refreshTrigger={refreshTrigger} onNavigateToTab={setActiveTab} />;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {(refreshTrigger) => renderContent(refreshTrigger)}
    </Layout>
  );
};
