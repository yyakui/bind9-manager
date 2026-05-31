<script setup lang="ts">
import { CheckCircleOutlined, ReloadOutlined, WarningOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { computed, h, onMounted, ref } from 'vue';

import { aclsApi, auditApi, backupApi, monitoringApi, viewsApi, zonesApi } from '../api/client';
import type { ACL, AuditLog, BackupItem, DNSView, MonitoringStatus, Zone } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const zones = ref<Zone[]>([]);
const acls = ref<ACL[]>([]);
const views = ref<DNSView[]>([]);
const backups = ref<BackupItem[]>([]);
const audits = ref<AuditLog[]>([]);
const status = ref<MonitoringStatus | null>(null);
const { t } = useI18n();

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
    message.error(t('dashboard.loadFailed'));
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
      <h1 class="page-title">{{ t('nav.dashboard') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
      </div>
    </div>

    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">{{ t('nav.zones') }}</div>
        <div class="metric-value">{{ zones.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ t('dashboard.records') }}</div>
        <div class="metric-value">{{ zones.reduce((total, zone) => total + zone.records.length, 0) }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ t('dashboard.aclsViews') }}</div>
        <div class="metric-value">{{ acls.length }} / {{ views.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ t('dashboard.dnssecSigned') }}</div>
        <div class="metric-value">{{ signedZones }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ t('dashboard.backups') }}</div>
        <div class="metric-value">{{ backups.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ t('dashboard.activeAlerts') }}</div>
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
              <strong>{{ t('dashboard.namedStatus') }}</strong>
              <a-tag :color="status?.named_running ? 'green' : 'red'">
                {{ status?.named_running ? t('common.running') : t('dashboard.notHealthy') }}
              </a-tag>
            </a-space>
            <a-descriptions size="small" :column="1" bordered>
              <a-descriptions-item :label="t('dashboard.queryLatency')">
                {{ status?.query_latency_ms ?? 'n/a' }} ms
              </a-descriptions-item>
              <a-descriptions-item label="rndc">
                {{ status?.rndc_status.ok ? t('common.ok') : status?.rndc_status.stderr || t('common.failed') }}
              </a-descriptions-item>
              <a-descriptions-item :label="t('common.generated')">
                {{ status?.generated_at || 'n/a' }}
              </a-descriptions-item>
            </a-descriptions>
          </a-space>
        </div>
      </a-col>
      <a-col :xs="24" :lg="12">
        <div class="section">
          <a-list size="small" :data-source="audits.slice(0, 6)">
            <template #header><strong>{{ t('dashboard.recentWrites') }}</strong></template>
            <template #renderItem="{ item }">
              <a-list-item>
                <a-space>
                  <a-tag>{{ item.method }}</a-tag>
                  <span>{{ item.path }}</span>
                  <span class="muted">{{ item.username || t('dashboard.anonymous') }}</span>
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
