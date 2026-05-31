<script setup lang="ts">
import { ReloadOutlined, SyncOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { h, onMounted, ref } from 'vue';

import { replicationApi } from '../api/client';

const loading = ref(false);
const rows = ref<Array<Record<string, any>>>([]);

const columns = [
  { title: 'Zone', dataIndex: 'zone', key: 'zone' },
  { title: 'Type', dataIndex: 'type', key: 'type', width: 120 },
  { title: 'Masters', key: 'masters' },
  { title: 'allow-transfer', key: 'allow_transfer' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', width: 110 },
];

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
  message[result.ok ? 'success' : 'error'](result.ok ? 'Refresh requested' : result.stderr || 'Refresh failed');
  await load();
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Replication</h1>
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
          <a-tag :color="record.status.ok ? 'green' : 'red'">{{ record.status.ok ? 'ok' : 'failed' }}</a-tag>
          <span class="mono">{{ record.status.stderr || record.status.stdout }}</span>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-button :icon="h(SyncOutlined)" @click="refresh(record.zone)" />
        </template>
      </template>
    </a-table>
  </div>
</template>
