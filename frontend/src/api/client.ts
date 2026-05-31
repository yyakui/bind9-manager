import axios from 'axios';

import type {
  ACL,
  AuditLog,
  BackupItem,
  CommandResult,
  DNSSECKey,
  DNSView,
  MonitoringStatus,
  Options,
  RecordItem,
  TSIGKey,
  Zone,
} from './types';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('bind9-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const unwrap = <T>(request: Promise<{ data: T }>) => request.then((response) => response.data);

export const authApi = {
  login(username: string, password: string) {
    const form = new URLSearchParams();
    form.set('username', username);
    form.set('password', password);
    return unwrap<{ access_token: string; username: string; role: string }>(
      api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
    );
  },
  me: () => unwrap<{ username: string; role: string }>(api.get('/auth/me')),
};

export const zonesApi = {
  list: () => unwrap<Zone[]>(api.get('/zones')),
  create: (payload: Partial<Zone>) => unwrap<Zone>(api.post('/zones', payload)),
  update: (id: number, payload: Partial<Zone>) => unwrap<Zone>(api.put(`/zones/${id}`, payload)),
  remove: (id: number) => unwrap(api.delete(`/zones/${id}`)),
  export: (id: number) => unwrap<string>(api.get(`/zones/${id}/export`, { responseType: 'text' })),
  import: (id: number, text: string) =>
    unwrap<Zone>(api.post(`/zones/${id}/import`, text, { headers: { 'Content-Type': 'text/plain' } })),
  writeFiles: (id: number) => unwrap(api.post(`/zones/${id}/write-files`)),
};

export const recordsApi = {
  list: (zoneId: number) => unwrap<RecordItem[]>(api.get(`/zones/${zoneId}/records`)),
  create: (zoneId: number, payload: Partial<RecordItem>) => unwrap<RecordItem>(api.post(`/zones/${zoneId}/records`, payload)),
  update: (id: number, payload: Partial<RecordItem>) => unwrap<RecordItem>(api.put(`/records/${id}`, payload)),
  remove: (id: number) => unwrap(api.delete(`/records/${id}`)),
};

export const aclsApi = {
  list: () => unwrap<ACL[]>(api.get('/acls')),
  create: (payload: Partial<ACL>) => unwrap<ACL>(api.post('/acls', payload)),
  update: (id: number, payload: Partial<ACL>) => unwrap<ACL>(api.put(`/acls/${id}`, payload)),
  remove: (id: number) => unwrap(api.delete(`/acls/${id}`)),
};

export const viewsApi = {
  list: () => unwrap<DNSView[]>(api.get('/views')),
  create: (payload: Partial<DNSView>) => unwrap<DNSView>(api.post('/views', payload)),
  update: (id: number, payload: Partial<DNSView>) => unwrap<DNSView>(api.put(`/views/${id}`, payload)),
  remove: (id: number) => unwrap(api.delete(`/views/${id}`)),
};

export const optionsApi = {
  get: () => unwrap<Options>(api.get('/options')),
  update: (payload: Partial<Options>) => unwrap<Options>(api.put('/options', payload)),
};

export const backupApi = {
  list: () => unwrap<BackupItem[]>(api.get('/backups')),
  create: () => unwrap<BackupItem>(api.post('/backups')),
  rollback: (id: number) => unwrap(api.post(`/backups/${id}/rollback`)),
};

export const monitoringApi = {
  status: () => unwrap<MonitoringStatus>(api.get('/monitoring/status')),
  reload: () => unwrap<CommandResult>(api.post('/monitoring/reload')),
  reconfig: () => unwrap<CommandResult>(api.post('/monitoring/reconfig')),
  zoneStatus: (zone: string) => unwrap<CommandResult>(api.get(`/monitoring/zones/${zone}/status`)),
  refresh: (zone: string) => unwrap<CommandResult>(api.post(`/monitoring/zones/${zone}/refresh`)),
};

export const replicationApi = {
  status: () => unwrap<Array<Record<string, unknown>>>(api.get('/replication/status')),
  refresh: (zone: string) => unwrap<CommandResult>(api.post(`/replication/zones/${zone}/refresh`)),
};

export const auditApi = {
  list: () => unwrap<AuditLog[]>(api.get('/audit')),
};

export const tsigApi = {
  list: () => unwrap<TSIGKey[]>(api.get('/tsig')),
  create: (payload: Partial<TSIGKey>) => unwrap<TSIGKey>(api.post('/tsig', payload)),
  remove: (id: number) => unwrap(api.delete(`/tsig/${id}`)),
};

export const dnssecApi = {
  keys: () => unwrap<DNSSECKey[]>(api.get('/dnssec/keys')),
  createKey: (zoneId: number, keyType: string) => unwrap<DNSSECKey>(api.post(`/dnssec/zones/${zoneId}/keys/${keyType}`)),
  sign: (zoneId: number) => unwrap<CommandResult>(api.post(`/dnssec/zones/${zoneId}/sign`)),
  unsign: (zoneId: number) => unwrap<Zone>(api.post(`/dnssec/zones/${zoneId}/unsign`)),
  ds: (zoneId: number) => unwrap<{ message: string }>(api.get(`/dnssec/zones/${zoneId}/ds`)),
};
