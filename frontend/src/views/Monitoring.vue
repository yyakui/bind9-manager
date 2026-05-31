<script setup lang="ts">
import { ReloadOutlined, SyncOutlined, ThunderboltOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { computed, h, onMounted, ref } from 'vue';

import { monitoringApi } from '../api/client';
import type { CommandResult, MonitoringStatus } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const status = ref<MonitoringStatus | null>(null);
const lastCommand = ref<CommandResult | null>(null);
const { t } = useI18n();

const zoneColumns = computed(() => [
  { title: t('zones.zone'), dataIndex: 'zone', key: 'zone' },
  { title: t('common.type'), dataIndex: 'type', key: 'type', width: 120 },
  { title: t('common.status'), key: 'status' },
]);

const load = async () => {
  loading.value = true;
  try {
    status.value = await monitoringApi.status();
  } finally {
    loading.value = false;
  }
};

const run = async (action: 'reload' | 'reconfig') => {
  lastCommand.value = action === 'reload' ? await monitoringApi.reload() : await monitoringApi.reconfig();
  const actionLabel = action === 'reload' ? t('common.reload') : t('monitoring.reconfig');
  message[lastCommand.value.ok ? 'success' : 'error'](t('monitoring.finished', { action: actionLabel }));
  await load();
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('nav.monitoring') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button :icon="h(SyncOutlined)" @click="run('reconfig')">{{ t('monitoring.reconfig') }}</a-button>
        <a-button type="primary" :icon="h(ThunderboltOutlined)" @click="run('reload')">{{ t('common.reload') }}</a-button>
      </div>
    </div>

    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">named</div>
        <div class="metric-value" :class="status?.named_running ? 'status-ok' : 'status-bad'">
          {{ status?.named_running ? t('common.up') : t('common.down') }}
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ t('monitoring.latency') }}</div>
        <div class="metric-value">{{ status?.query_latency_ms ?? 'n/a' }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ t('common.alerts') }}</div>
        <div class="metric-value" :class="status?.alerts.length ? 'status-bad' : 'status-ok'">
          {{ status?.alerts.length ?? 0 }}
        </div>
      </div>
    </div>

    <a-alert
      v-for="alert in status?.alerts"
      :key="alert"
      type="error"
      show-icon
      :message="alert"
    />

    <a-table
      row-key="zone"
      :columns="zoneColumns"
      :data-source="status?.zones || []"
      :pagination="false"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status.ok ? 'green' : 'red'">{{ record.status.ok ? t('common.ok') : t('common.failed') }}</a-tag>
          <span class="mono">{{ record.status.stderr || record.status.stdout }}</span>
        </template>
      </template>
    </a-table>

    <div v-if="lastCommand" class="section">
      <strong>{{ t('monitoring.lastCommand') }}</strong>
      <pre class="mono">{{ JSON.stringify(lastCommand, null, 2) }}</pre>
    </div>
  </div>
</template>
