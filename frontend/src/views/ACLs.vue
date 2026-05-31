<script setup lang="ts">
import { DeleteOutlined, EditOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { computed, h, onMounted, reactive, ref } from 'vue';

import { aclsApi } from '../api/client';
import { joinList, parseList } from '../api/form';
import type { ACL } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const modalOpen = ref(false);
const editingId = ref<number | null>(null);
const acls = ref<ACL[]>([]);
const form = reactive({ name: '', entries: '' });
const { t } = useI18n();

const columns = computed(() => [
  { title: t('common.name'), dataIndex: 'name', key: 'name' },
  { title: t('common.entries'), key: 'entries' },
  { title: t('common.references'), dataIndex: 'references', key: 'references', width: 120 },
  { title: t('common.actions'), key: 'actions', width: 120 },
]);

const load = async () => {
  loading.value = true;
  try {
    acls.value = await aclsApi.list();
  } catch {
    message.error(t('acls.loadFailed'));
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  editingId.value = null;
  Object.assign(form, { name: '', entries: '' });
  modalOpen.value = true;
};

const openEdit = (acl: ACL) => {
  editingId.value = acl.id;
  Object.assign(form, { name: acl.name, entries: joinList(acl.entries) });
  modalOpen.value = true;
};

const save = async () => {
  const payload = { name: form.name, entries: parseList(form.entries) };
  if (editingId.value) {
    await aclsApi.update(editingId.value, payload);
    message.success(t('acls.updated'));
  } else {
    await aclsApi.create(payload);
    message.success(t('acls.created'));
  }
  modalOpen.value = false;
  await load();
};

const remove = (acl: ACL) => {
  Modal.confirm({
    title: t('common.confirmDelete', { name: acl.name }),
    onOk: async () => {
      await aclsApi.remove(acl.id);
      message.success(t('acls.deleted'));
      await load();
    },
  });
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('nav.acls') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(PlusOutlined)" @click="openCreate">{{ t('acls.new') }}</a-button>
      </div>
    </div>

    <a-table row-key="id" :columns="columns" :data-source="acls" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'entries'">
          <a-space wrap>
            <a-tag v-for="entry in record.entries" :key="entry">{{ entry }}</a-tag>
          </a-space>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button :icon="h(EditOutlined)" @click="openEdit(record)" />
            <a-button danger :icon="h(DeleteOutlined)" :disabled="record.references > 0" @click="remove(record)" />
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="editingId ? t('acls.edit') : t('acls.new')" @ok="save">
      <a-form layout="vertical">
        <a-form-item :label="t('common.name')"><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item :label="t('common.entries')"><a-input v-model:value="form.entries" placeholder="10.0.0.0/8, localhost, any" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
