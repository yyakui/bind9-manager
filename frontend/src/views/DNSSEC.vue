<script setup lang="ts">
import { KeyOutlined, ReloadOutlined, SafetyCertificateOutlined, StopOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { computed, h, onMounted, ref } from 'vue';

import { dnssecApi, zonesApi } from '../api/client';
import type { DNSSECKey, Zone } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const zones = ref<Zone[]>([]);
const keys = ref<DNSSECKey[]>([]);
const selectedZoneId = ref<number | null>(null);
const { t } = useI18n();

const keyColumns = computed(() => [
  { title: t('dnssec.zoneId'), dataIndex: 'zone_id', key: 'zone_id', width: 100 },
  { title: t('common.type'), dataIndex: 'key_type', key: 'key_type', width: 100 },
  { title: t('common.algorithm'), dataIndex: 'algorithm', key: 'algorithm' },
  { title: t('common.active'), dataIndex: 'active', key: 'active', width: 100 },
  { title: t('common.path'), dataIndex: 'path', key: 'path' },
  { title: t('common.created'), dataIndex: 'created_at', key: 'created_at', width: 220 },
]);

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
  message[key.active ? 'success' : 'warning'](t('dnssec.keyRequestCompleted', { type: keyType }));
  await load();
};

const sign = async () => {
  if (!selectedZoneId.value) return;
  const result = await dnssecApi.sign(selectedZoneId.value);
  message[result.ok ? 'success' : 'error'](result.ok ? t('dnssec.zoneSigned') : result.stderr || t('dnssec.signFailed'));
  await load();
};

const unsign = async () => {
  if (!selectedZoneId.value) return;
  await dnssecApi.unsign(selectedZoneId.value);
  message.success(t('dnssec.markedUnsigned'));
  await load();
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('nav.dnssec') }}</h1>
      <div class="page-actions">
        <a-select v-model:value="selectedZoneId" style="width: 260px" :placeholder="t('common.selectZone')">
          <a-select-option v-for="zone in zones" :key="zone.id" :value="zone.id">
            {{ zone.name }} {{ zone.is_dnssec_signed ? `(${t('zones.signed')})` : '' }}
          </a-select-option>
        </a-select>
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button :icon="h(KeyOutlined)" @click="createKey('KSK')">KSK</a-button>
        <a-button :icon="h(KeyOutlined)" @click="createKey('ZSK')">ZSK</a-button>
        <a-button type="primary" :icon="h(SafetyCertificateOutlined)" @click="sign">{{ t('dnssec.sign') }}</a-button>
        <a-button danger :icon="h(StopOutlined)" @click="unsign">{{ t('dnssec.unsign') }}</a-button>
      </div>
    </div>

    <a-table row-key="id" :columns="keyColumns" :data-source="keys" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'active'">
          <a-tag :color="record.active ? 'green' : 'red'">{{ record.active ? t('common.yes') : t('common.no') }}</a-tag>
        </template>
        <template v-else-if="column.key === 'path'">
          <span class="mono">{{ record.path }}</span>
        </template>
      </template>
    </a-table>
  </div>
</template>
