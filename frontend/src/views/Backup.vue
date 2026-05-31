<script setup lang="ts">
import { RollbackOutlined, SaveOutlined, SyncOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { h, onMounted, ref } from 'vue';

import { backupApi } from '../api/client';
import type { BackupItem } from '../api/types';

const loading = ref(false);
const backups = ref<BackupItem[]>([]);

const columns = [
  { title: 'Created', dataIndex: 'created_at', key: 'created_at', width: 220 },
  { title: 'Operator', dataIndex: 'operator', key: 'operator', width: 140 },
  { title: 'Summary', dataIndex: 'summary', key: 'summary' },
  { title: 'Archive', dataIndex: 'archive_path', key: 'archive_path' },
  { title: 'Actions', key: 'actions', width: 120 },
];

const load = async () => {
  loading.value = true;
  try {
    backups.value = await backupApi.list();
  } finally {
    loading.value = false;
  }
};

const create = async () => {
  await backupApi.create();
  message.success('Snapshot created');
  await load();
};

const rollback = (backup: BackupItem) => {
  Modal.confirm({
    title: `Rollback to backup #${backup.id}?`,
    onOk: async () => {
      await backupApi.rollback(backup.id);
      message.success('Rollback completed');
      await load();
    },
  });
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Backup</h1>
      <div class="page-actions">
        <a-button :icon="h(SyncOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(SaveOutlined)" @click="create">Snapshot</a-button>
      </div>
    </div>

    <a-table row-key="id" :columns="columns" :data-source="backups" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'archive_path'">
          <span class="mono">{{ record.archive_path }}</span>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-tooltip title="Rollback">
            <a-button :icon="h(RollbackOutlined)" @click="rollback(record)" />
          </a-tooltip>
        </template>
      </template>
    </a-table>
  </div>
</template>
