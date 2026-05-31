<script setup lang="ts">
import { ReloadOutlined } from '@ant-design/icons-vue';
import { h, onMounted, ref } from 'vue';

import { auditApi } from '../api/client';
import type { AuditLog } from '../api/types';

const loading = ref(false);
const logs = ref<AuditLog[]>([]);

const columns = [
  { title: 'Time', dataIndex: 'created_at', key: 'created_at', width: 220 },
  { title: 'User', dataIndex: 'username', key: 'username', width: 140 },
  { title: 'Method', dataIndex: 'method', key: 'method', width: 100 },
  { title: 'Path', dataIndex: 'path', key: 'path' },
  { title: 'Status', dataIndex: 'status_code', key: 'status_code', width: 100 },
  { title: 'Client', dataIndex: 'client_ip', key: 'client_ip', width: 140 },
];

const load = async () => {
  loading.value = true;
  try {
    logs.value = await auditApi.list();
  } finally {
    loading.value = false;
  }
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Audit Log</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
      </div>
    </div>
    <a-table row-key="id" :columns="columns" :data-source="logs" :loading="loading">
      <template #expandedRowRender="{ record }">
        <pre class="mono">{{ record.diff || 'No request payload captured' }}</pre>
      </template>
    </a-table>
  </div>
</template>
