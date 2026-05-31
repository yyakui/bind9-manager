<script setup lang="ts">
import { DeleteOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { computed, h, onMounted, reactive, ref } from 'vue';

import { tsigApi } from '../api/client';
import { joinList, parseList } from '../api/form';
import type { TSIGKey } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const modalOpen = ref(false);
const keys = ref<TSIGKey[]>([]);
const form = reactive({ name: '', algorithm: 'hmac-sha256', secret: '', zones: '', allow_update_zones: '' });
const { t } = useI18n();

const columns = computed(() => [
  { title: t('common.name'), dataIndex: 'name', key: 'name' },
  { title: t('common.algorithm'), dataIndex: 'algorithm', key: 'algorithm', width: 160 },
  { title: t('nav.zones'), key: 'zones' },
  { title: t('common.secret'), dataIndex: 'secret', key: 'secret' },
  { title: t('common.actions'), key: 'actions', width: 90 },
]);

const load = async () => {
  loading.value = true;
  try {
    keys.value = await tsigApi.list();
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  Object.assign(form, { name: '', algorithm: 'hmac-sha256', secret: '', zones: '', allow_update_zones: '' });
  modalOpen.value = true;
};

const save = async () => {
  await tsigApi.create({
    name: form.name,
    algorithm: form.algorithm,
    secret: form.secret || undefined,
    zones: parseList(form.zones),
    allow_update_zones: parseList(form.allow_update_zones),
  });
  modalOpen.value = false;
  message.success(t('tsig.saved'));
  await load();
};

const remove = (key: TSIGKey) => {
  Modal.confirm({
    title: t('common.confirmDelete', { name: key.name }),
    onOk: async () => {
      await tsigApi.remove(key.id);
      message.success(t('tsig.deleted'));
      await load();
    },
  });
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('tsig.title') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(PlusOutlined)" @click="openCreate">{{ t('tsig.new') }}</a-button>
      </div>
    </div>

    <a-table row-key="id" :columns="columns" :data-source="keys" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'zones'">
          {{ joinList(record.zones) }}
        </template>
        <template v-else-if="column.key === 'secret'">
          <span class="mono">{{ record.secret }}</span>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-button danger :icon="h(DeleteOutlined)" @click="remove(record)" />
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="t('tsig.newTitle')" @ok="save">
      <a-form layout="vertical">
        <a-form-item :label="t('common.name')"><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item :label="t('common.algorithm')"><a-input v-model:value="form.algorithm" /></a-form-item>
        <a-form-item :label="t('common.secret')"><a-input v-model:value="form.secret" :placeholder="t('tsig.leaveEmpty')" /></a-form-item>
        <a-form-item :label="t('tsig.zoneTransferZones')"><a-input v-model:value="form.zones" /></a-form-item>
        <a-form-item :label="t('tsig.allowUpdateZones')"><a-input v-model:value="form.allow_update_zones" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
