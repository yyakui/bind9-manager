<script setup lang="ts">
import { DeleteOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { h, onMounted, reactive, ref } from 'vue';

import { tsigApi } from '../api/client';
import { joinList, parseList } from '../api/form';
import type { TSIGKey } from '../api/types';

const loading = ref(false);
const modalOpen = ref(false);
const keys = ref<TSIGKey[]>([]);
const form = reactive({ name: '', algorithm: 'hmac-sha256', secret: '', zones: '', allow_update_zones: '' });

const columns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Algorithm', dataIndex: 'algorithm', key: 'algorithm', width: 160 },
  { title: 'Zones', key: 'zones' },
  { title: 'Secret', dataIndex: 'secret', key: 'secret' },
  { title: 'Actions', key: 'actions', width: 90 },
];

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
  message.success('TSIG key saved');
  await load();
};

const remove = (key: TSIGKey) => {
  Modal.confirm({
    title: `Delete ${key.name}?`,
    onOk: async () => {
      await tsigApi.remove(key.id);
      message.success('TSIG key deleted');
      await load();
    },
  });
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">TSIG Keys</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(PlusOutlined)" @click="openCreate">New key</a-button>
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

    <a-modal v-model:open="modalOpen" title="New TSIG key" @ok="save">
      <a-form layout="vertical">
        <a-form-item label="Name"><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="Algorithm"><a-input v-model:value="form.algorithm" /></a-form-item>
        <a-form-item label="Secret"><a-input v-model:value="form.secret" placeholder="Leave empty to generate" /></a-form-item>
        <a-form-item label="Zone transfer zones"><a-input v-model:value="form.zones" /></a-form-item>
        <a-form-item label="allow-update zones"><a-input v-model:value="form.allow_update_zones" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
