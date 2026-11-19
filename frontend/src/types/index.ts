export type AlertSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
export type AlertStatus = 'NEW' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';
export type UserRole = 'ADMIN' | 'ANALYST' | 'VIEWER';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface SecurityEvent {
  id: number;
  event_uuid: string;
  timestamp: string;
  source_ip?: string;
  source_port?: number;
  destination_ip?: string;
  destination_port?: number;
  event_type: string;
  action: string;
  status: string;
  username?: string;
  hostname?: string;
  service?: string;
  raw_log: string;
  parser_type: string;
  is_synthetic: boolean;
  metadata_json?: Record<string, any>;
  created_at: string;
}

export interface Alert {
  id: number;
  alert_uuid: string;
  rule_id: string;
  title: string;
  category: string;
  severity: AlertSeverity;
  source_ip?: string;
  target_username?: string;
  timestamp: string;
  evidence: Record<string, any>;
  detection_rule_name: string;
  recommended_action: string;
  confidence_score: number;
  status: AlertStatus;
  is_synthetic: boolean;
  created_at: string;
  resolution_notes?: string;
}

export interface Investigation {
  id: number;
  case_number: string;
  title: string;
  description?: string;
  severity: string;
  status: string;
  lead_analyst_id?: number;
  associated_alert_ids: string[];
  associated_ips: string[];
  associated_users: string[];
  verdict?: string;
  summary?: string;
  created_at: string;
  updated_at: string;
  notes: { id: number; author_id: number; content: string; created_at: string }[];
}

export interface DashboardStats {
  total_events: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  suspicious_ips_count: number;
  failed_auth_count: number;
  successful_logins_count: number;
  active_investigations: number;
  timeline: {
    timestamp: string;
    total_events: number;
    failed_logins: number;
    critical_alerts: number;
    high_alerts: number;
  }[];
  attack_distribution: {
    category: string;
    count: number;
    percentage: number;
  }[];
  top_targeted_accounts: {
    username: string;
    attempt_count: number;
    failure_count: number;
    status: string;
  }[];
  top_suspicious_ips: {
    ip: string;
    failure_count: number;
    alert_count: number;
    highest_severity: string;
    is_private: boolean;
  }[];
}

export interface IpIntelligence {
  ip: string;
  is_valid: boolean;
  version: number;
  is_private: boolean;
  is_loopback: boolean;
  is_multicast: boolean;
  threat_score: number;
  classification: string;
  reputation_history: {
    first_seen?: string;
    last_seen?: string;
    total_events: number;
    failed_attempts: number;
    successful_attempts: number;
    total_alerts: number;
    critical_alerts: number;
  };
  targeted_accounts: string[];
  detected_rules: string[];
  external_intel?: any;
}
