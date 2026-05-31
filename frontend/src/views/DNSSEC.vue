<script setup lang="ts">
import { KeyOutlined, ReloadOutlined, SafetyCertificateOutlined, StopOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { h, onMounted, ref } from 'vue';

import { dnssecApi, zonesApi } from '../api/client';
import type { DNSSECKey, Zone } from '../api/types';

const loading = ref(false);
const zones = ref<Zone[]>([]);
const keys = ref<DNSSECKey[]>([]);
const selectedZoneId = ref<number | null>(null);

const keyColumns = [
  { title: 'Zone ID', dataIndex: 'zone_id', key: 'zone_id', width: 100 },
  { title: 'Type', dataIndex: 'key_type', key: 'key_type', width: 100 },
  { title: 'Algorithm', dataIndex: 'algorithm', key: 'algorithm' },
  { title: 'Active', dataIndex: 'active', key: 'active', width: 100 },
  { title: 'Path', dataIndex: 'path', key: 'path' },
  { title: 'Created', dataIndex: 'created_at', key: 'created_at', width: 220 },
];

const load = async () => {
  loading.value = true;
  try {
    [zones.value, keys.value] = await Promise.all([zonesApi.list(), dnssecApi.keys()]);
    selectedZoneId.value ||= zones.value[0]?.id ?? null;
  } finally {
    loading.value = false;
  }
};

const createKey = async (keyType: 'KSK' | 'ZSK') => {
  if (!selectedZoneId.value) return;
  const key = await dnssecApi.createKey(selectedZoneId.value, keyType);
  message[key.active ? 'success' : 'warning'](`${keyType} request completed`);
  await load();
};

const sign = async () => {
  if (!selectedZoneId.value) return;
  const result = await dnssecApi.sign(selectedZoneId.value);
  message[result.ok ? 'success' : 'error'](result.ok ? 'Zone signed' : result.stderr || 'Sign failed');
  await load();
};

const unsign = async () => {
  if (!selectedZoneId.value) return;
  await dnssecApi.unsign(selectedZoneId.value);
  message.success('Zone marked unsigned');
  await load();
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">DNSSEC</h1>
      <div class="page-actions">
        <a-select v-model:value="selectedZoneId" style="width: 260px" placeholder="Select zone">
          <a-select-option v-for="zone in zones" :key="zone.id" :value="zone.id">
            {{ zone.name }} {{ zone.is_dnssec_signed ? '(signed)' : '' }}
          </a-select-option>
        </a-select>
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button :icon="h(KeyOutlined)" @click="createKey('KSK')">KSK</a-button>
        <a-button :icon="h(KeyOutlined)" @click="createKey('ZSK')">ZSK</a-button>
        <a-button type="primary" :icon="h(SafetyCertificateOutlined)" @click="sign">Sign</a-button>
        <a-button danger :icon="h(StopOutlined)" @click="unsign">Unsign</a-button>
      </div>
    </div>

    <a-table row-key="id" :columns="keyColumns" :data-source="keys" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'active'">
          <a-tag :color="record.active ? 'green' : 'red'">{{ record.active ? 'yes' : 'no' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'path'">
          <span class="mono">{{ record.path }}</span>
        </template>
      </template>
    </a-table>
  </div>
</template>
