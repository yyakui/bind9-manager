<script setup lang="ts">
import { RollbackOutlined, SaveOutlined, SyncOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { computed, h, onMounted, ref } from 'vue';

import { backupApi } from '../api/client';
import type { BackupItem } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const backups = ref<BackupItem[]>([]);
const { t } = useI18n();

const columns = computed(() => [
  { title: t('common.created'), dataIndex: 'created_at', key: 'created_at', width: 220 },
  { title: t('common.operator'), dataIndex: 'operator', key: 'operator', width: 140 },
  { title: t('common.summary'), dataIndex: 'summary', key: 'summary' },
  { title: t('common.archive'), dataIndex: 'archive_path', key: 'archive_path' },
  { title: t('common.actions'), key: 'actions', width: 120 },
]);

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
  message.success(t('backup.snapshotCreated'));
  await load();
};

const rollback = (backup: BackupItem) => {
  Modal.confirm({
    title: t('backup.rollbackConfirm', { id: backup.id }),
    onOk: async () => {
      await backupApi.rollback(backup.id);
      message.success(t('backup.rollbackCompleted'));
      await load();
    },
  });
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('nav.backup') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(SyncOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(SaveOutlined)" @click="create">{{ t('backup.snapshot') }}</a-button>
      </div>
    </div>

    <a-table row-key="id" :columns="columns" :data-source="backups" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'archive_path'">
          <span class="mono">{{ record.archive_path }}</span>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-tooltip :title="t('backup.rollback')">
            <a-button :icon="h(RollbackOutlined)" @click="rollback(record)" />
          </a-tooltip>
        </template>
      </template>
    </a-table>
  </div>
</template>
