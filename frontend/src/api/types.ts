export interface RecordItem {
  id: number;
  zone_id: number;
  name: string;
  record_type: string;
  value: string;
  ttl?: number | null;
  priority?: number | null;
  weight?: number | null;
  port?: number | null;
  comment?: string | null;
}

export interface Zone {
  id: number;
  name: string;
  zone_type: string;
  view_id?: number | null;
  file_path?: string | null;
  ttl: number;
  primary_ns: string;
  admin_email: string;
  serial: number;
  refresh: number;
  retry: number;
  expire: number;
  minimum_ttl: number;
  allow_transfer: string[];
  allow_update: string[];
  masters: string[];
  forwarders: string[];
  is_dnssec_signed: boolean;
  records: RecordItem[];
}

export interface ACL {
  id: number;
  name: string;
  entries: string[];
  references: number;
}

export interface DNSView {
  id: number;
  name: string;
  match_clients: string[];
  recursion: boolean;
  sort_order: number;
  zone_count: number;
}

export interface Options {
  id: number;
  listen_on: string[];
  listen_on_v6: string[];
  forwarders: string[];
  forward_mode: string;
  recursion: boolean;
  allow_query: string[];
  allow_recursion: string[];
  dnssec_validation: string;
  rate_limit: Record<string, unknown>;
  response_policy: string[];
  logging_channels: Record<string, unknown>;
  logging_categories: Record<string, unknown>;
}

export interface BackupItem {
  id: number;
  created_at: string;
  operator: string;
  summary: string;
  archive_path: string;
}

export interface MonitoringStatus {
  generated_at: string;
  named_running: boolean;
  rndc_status: CommandResult;
  zones: Array<{ zone: string; type: string; status: CommandResult }>;
  query_latency_ms?: number | null;
  alerts: string[];
}

export interface CommandResult {
  command: string[];
  returncode: number;
  stdout: string;
  stderr: string;
  ok: boolean;
}

export interface AuditLog {
  id: number;
  created_at: string;
  username?: string | null;
  client_ip?: string | null;
  method: string;
  path: string;
  action: string;
  object_type?: string | null;
  object_id?: string | null;
  status_code: number;
  diff?: string | null;
}

export interface TSIGKey {
  id: number;
  name: string;
  algorithm: string;
  secret: string;
  zones: string[];
  allow_update_zones: string[];
  created_at: string;
}

export interface DNSSECKey {
  id: number;
  zone_id: number;
  key_type: string;
  algorithm: string;
  key_tag?: string | null;
  path?: string | null;
  active: boolean;
  created_at: string;
}
