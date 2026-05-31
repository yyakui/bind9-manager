<script setup lang="ts">
import { DeleteOutlined, EditOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { h, onMounted, reactive, ref } from 'vue';

import { viewsApi } from '../api/client';
import { joinList, parseList } from '../api/form';
import type { DNSView } from '../api/types';

const loading = ref(false);
const modalOpen = ref(false);
const editingId = ref<number | null>(null);
const views = ref<DNSView[]>([]);
const form = reactive({ name: '', match_clients: '', recursion: true, sort_order: 100 });

const columns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Match clients', key: 'match_clients' },
  { title: 'Recursion', dataIndex: 'recursion', key: 'recursion', width: 120 },
  { title: 'Zones', dataIndex: 'zone_count', key: 'zone_count', width: 100 },
  { title: 'Order', dataIndex: 'sort_order', key: 'sort_order', width: 100 },
  { title: 'Actions', key: 'actions', width: 120 },
];

const load = async () => {
  loading.value = true;
  try {
    views.value = await viewsApi.list();
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  editingId.value = null;
  Object.assign(form, { name: '', match_clients: '', recursion: true, sort_order: 100 });
  modalOpen.value = true;
};

const openEdit = (view: DNSView) => {
  editingId.value = view.id;
  Object.assign(form, {
    name: view.name,
    match_clients: joinList(view.match_clients),
    recursion: view.recursion,
    sort_order: view.sort_order,
  });
  modalOpen.value = true;
};

const save = async () => {
  const payload = { ...form, match_clients: parseList(form.match_clients) };
  if (editingId.value) {
    await viewsApi.update(editingId.value, payload);
    message.success('View updated');
  } else {
    await viewsApi.create(payload);
    message.success('View created');
  }
  modalOpen.value = false;
  await load();
};

const remove = (view: DNSView) => {
  Modal.confirm({
    title: `Delete ${view.name}?`,
    onOk: async () => {
      await viewsApi.remove(view.id);
      message.success('View deleted');
      await load();
    },
  });
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">DNS Views</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(PlusOutlined)" @click="openCreate">New view</a-button>
      </div>
    </div>

    <a-table row-key="id" :columns="columns" :data-source="views" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'match_clients'">
          <a-space wrap>
            <a-tag v-for="entry in record.match_clients" :key="entry">{{ entry }}</a-tag>
          </a-space>
        </template>
        <template v-else-if="column.key === 'recursion'">
          <a-tag :color="record.recursion ? 'green' : 'default'">{{ record.recursion ? 'yes' : 'no' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button :icon="h(EditOutlined)" @click="openEdit(record)" />
            <a-button danger :icon="h(DeleteOutlined)" :disabled="record.zone_count > 0" @click="remove(record)" />
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="editingId ? 'Edit view' : 'New view'" @ok="save">
      <a-form layout="vertical">
        <a-form-item label="Name"><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="Match clients"><a-input v-model:value="form.match_clients" placeholder="corp-net, 10.0.0.0/8" /></a-form-item>
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item label="Recursion"><a-switch v-model:checked="form.recursion" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="Order"><a-input-number v-model:value="form.sort_order" style="width: 100%" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>
