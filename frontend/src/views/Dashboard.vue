<script setup lang="ts">
import { CheckCircleOutlined, ReloadOutlined, WarningOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { computed, h, onMounted, ref } from 'vue';

import { aclsApi, auditApi, backupApi, monitoringApi, viewsApi, zonesApi } from '../api/client';
import type { ACL, AuditLog, BackupItem, DNSView, MonitoringStatus, Zone } from '../api/types';

const loading = ref(false);
const zones = ref<Zone[]>([]);
const acls = ref<ACL[]>([]);
const views = ref<DNSView[]>([]);
const backups = ref<BackupItem[]>([]);
const audits = ref<AuditLog[]>([]);
const status = ref<MonitoringStatus | null>(null);

const load = async () => {
  loading.value = true;
  try {
    const [zoneList, aclList, viewList, backupList, auditList, monitorStatus] = await Promise.all([
      zonesApi.list(),
      aclsApi.list(),
      viewsApi.list(),
      backupApi.list(),
      auditApi.list(),
      monitoringApi.status(),
    ]);
    zones.value = zoneList;
    acls.value = aclList;
    views.value = viewList;
    backups.value = backupList;
    audits.value = auditList;
    status.value = monitorStatus;
  } catch {
    message.error('Failed to load dashboard');
  } finally {
    loading.value = false;
  }
};

const signedZones = computed(() => zones.value.filter((zone) => zone.is_dnssec_signed).length);
const alertCount = computed(() => status.value?.alerts.length ?? 0);

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
      </div>
    </div>

    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">Zones</div>
        <div class="metric-value">{{ zones.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Records</div>
        <div class="metric-value">{{ zones.reduce((total, zone) => total + zone.records.length, 0) }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">ACLs / Views</div>
        <div class="metric-value">{{ acls.length }} / {{ views.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">DNSSEC Signed</div>
        <div class="metric-value">{{ signedZones }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Backups</div>
        <div class="metric-value">{{ backups.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Active Alerts</div>
        <div class="metric-value" :class="alertCount ? 'status-bad' : 'status-ok'">{{ alertCount }}</div>
      </div>
    </div>

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :lg="12">
        <div class="section">
          <a-space direction="vertical" size="middle" style="width: 100%">
            <a-space>
              <CheckCircleOutlined v-if="status?.named_running" class="status-ok" />
              <WarningOutlined v-else class="status-bad" />
              <strong>named status</strong>
              <a-tag :color="status?.named_running ? 'green' : 'red'">
                {{ status?.named_running ? 'running' : 'not healthy' }}
              </a-tag>
            </a-space>
            <a-descriptions size="small" :column="1" bordered>
              <a-descriptions-item label="Query latency">
                {{ status?.query_latency_ms ?? 'n/a' }} ms
              </a-descriptions-item>
              <a-descriptions-item label="rndc">
                {{ status?.rndc_status.ok ? 'ok' : status?.rndc_status.stderr || 'failed' }}
              </a-descriptions-item>
              <a-descriptions-item label="Generated">
                {{ status?.generated_at || 'n/a' }}
              </a-descriptions-item>
            </a-descriptions>
          </a-space>
        </div>
      </a-col>
      <a-col :xs="24" :lg="12">
        <div class="section">
          <a-list size="small" :data-source="audits.slice(0, 6)">
            <template #header><strong>Recent writes</strong></template>
            <template #renderItem="{ item }">
              <a-list-item>
                <a-space>
                  <a-tag>{{ item.method }}</a-tag>
                  <span>{{ item.path }}</span>
                  <span class="muted">{{ item.username || 'anonymous' }}</span>
                </a-space>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
.muted {
  color: #778695;
}
</style>
