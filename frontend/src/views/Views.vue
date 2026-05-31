<script setup lang="ts">
import { DeleteOutlined, EditOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { computed, h, onMounted, reactive, ref } from 'vue';

import { viewsApi } from '../api/client';
import { joinList, parseList } from '../api/form';
import type { DNSView } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const modalOpen = ref(false);
const editingId = ref<number | null>(null);
const views = ref<DNSView[]>([]);
const form = reactive({ name: '', match_clients: '', recursion: true, sort_order: 100 });
const { t } = useI18n();

const columns = computed(() => [
  { title: t('common.name'), dataIndex: 'name', key: 'name' },
  { title: t('views.matchClients'), key: 'match_clients' },
  { title: t('views.recursion'), dataIndex: 'recursion', key: 'recursion', width: 120 },
  { title: t('views.zones'), dataIndex: 'zone_count', key: 'zone_count', width: 100 },
  { title: t('views.order'), dataIndex: 'sort_order', key: 'sort_order', width: 100 },
  { title: t('common.actions'), key: 'actions', width: 120 },
]);

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
    message.success(t('views.updated'));
  } else {
    await viewsApi.create(payload);
    message.success(t('views.created'));
  }
  modalOpen.value = false;
  await load();
};

const remove = (view: DNSView) => {
  Modal.confirm({
    title: t('common.confirmDelete', { name: view.name }),
    onOk: async () => {
      await viewsApi.remove(view.id);
      message.success(t('views.deleted'));
      await load();
    },
  });
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('views.title') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(PlusOutlined)" @click="openCreate">{{ t('views.new') }}</a-button>
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
          <a-tag :color="record.recursion ? 'green' : 'default'">{{ record.recursion ? t('common.yes') : t('common.no') }}</a-tag>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button :icon="h(EditOutlined)" @click="openEdit(record)" />
            <a-button danger :icon="h(DeleteOutlined)" :disabled="record.zone_count > 0" @click="remove(record)" />
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="editingId ? t('views.edit') : t('views.new')" @ok="save">
      <a-form layout="vertical">
        <a-form-item :label="t('common.name')"><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item :label="t('views.matchClients')"><a-input v-model:value="form.match_clients" placeholder="corp-net, 10.0.0.0/8" /></a-form-item>
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item :label="t('views.recursion')"><a-switch v-model:checked="form.recursion" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item :label="t('views.order')"><a-input-number v-model:value="form.sort_order" style="width: 100%" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>
