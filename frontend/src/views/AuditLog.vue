<script setup lang="ts">
import { ReloadOutlined } from '@ant-design/icons-vue';
import { computed, h, onMounted, ref } from 'vue';

import { auditApi } from '../api/client';
import type { AuditLog } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const logs = ref<AuditLog[]>([]);
const { t } = useI18n();

const columns = computed(() => [
  { title: t('common.time'), dataIndex: 'created_at', key: 'created_at', width: 220 },
  { title: t('common.user'), dataIndex: 'username', key: 'username', width: 140 },
  { title: t('audit.method'), dataIndex: 'method', key: 'method', width: 100 },
  { title: t('common.path'), dataIndex: 'path', key: 'path' },
  { title: t('common.status'), dataIndex: 'status_code', key: 'status_code', width: 100 },
  { title: t('common.client'), dataIndex: 'client_ip', key: 'client_ip', width: 140 },
]);

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
      <h1 class="page-title">{{ t('nav.audit') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
      </div>
    </div>
    <a-table row-key="id" :columns="columns" :data-source="logs" :loading="loading">
      <template #expandedRowRender="{ record }">
        <pre class="mono">{{ record.diff || t('audit.noPayload') }}</pre>
      </template>
    </a-table>
  </div>
</template>
