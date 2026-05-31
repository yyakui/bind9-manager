<script setup lang="ts">
import { ReloadOutlined, SyncOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { computed, h, onMounted, ref } from 'vue';

import { replicationApi } from '../api/client';
import { useI18n } from '../i18n';

const loading = ref(false);
const rows = ref<Array<Record<string, any>>>([]);
const { t } = useI18n();

const columns = computed(() => [
  { title: t('zones.zone'), dataIndex: 'zone', key: 'zone' },
  { title: t('common.type'), dataIndex: 'type', key: 'type', width: 120 },
  { title: t('replication.masters'), key: 'masters' },
  { title: 'allow-transfer', key: 'allow_transfer' },
  { title: t('common.status'), key: 'status' },
  { title: t('common.actions'), key: 'actions', width: 110 },
]);

const load = async () => {
  loading.value = true;
  try {
    rows.value = await replicationApi.status();
  } finally {
    loading.value = false;
  }
};

const refresh = async (zone: string) => {
  const result = await replicationApi.refresh(zone);
  message[result.ok ? 'success' : 'error'](result.ok ? t('replication.refreshRequested') : result.stderr || t('replication.refreshFailed'));
  await load();
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('nav.replication') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
      </div>
    </div>

    <a-table row-key="zone" :columns="columns" :data-source="rows" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'masters'">
          <a-space wrap><a-tag v-for="item in record.masters" :key="item">{{ item }}</a-tag></a-space>
        </template>
        <template v-else-if="column.key === 'allow_transfer'">
          <a-space wrap><a-tag v-for="item in record.allow_transfer" :key="item">{{ item }}</a-tag></a-space>
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status.ok ? 'green' : 'red'">{{ record.status.ok ? t('common.ok') : t('common.failed') }}</a-tag>
          <span class="mono">{{ record.status.stderr || record.status.stdout }}</span>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-button :icon="h(SyncOutlined)" @click="refresh(record.zone)" />
        </template>
      </template>
    </a-table>
  </div>
</template>
