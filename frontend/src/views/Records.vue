<script setup lang="ts">
import { DeleteOutlined, EditOutlined, PlusOutlined, ReloadOutlined, UploadOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { computed, h, onMounted, reactive, ref, watch } from 'vue';

import { recordsApi, zonesApi } from '../api/client';
import type { RecordItem, Zone } from '../api/types';
import { useI18n } from '../i18n';

const zones = ref<Zone[]>([]);
const records = ref<RecordItem[]>([]);
const selectedZoneId = ref<number | null>(null);
const loading = ref(false);
const modalOpen = ref(false);
const importOpen = ref(false);
const editingId = ref<number | null>(null);
const importText = ref('');
const { t } = useI18n();

const form = reactive({
  name: '@',
  record_type: 'A',
  value: '',
  ttl: null as number | null,
  priority: null as number | null,
  weight: null as number | null,
  port: null as number | null,
  comment: '',
});

const selectedZone = computed(() => zones.value.find((zone) => zone.id === selectedZoneId.value));

const columns = computed(() => [
  { title: t('common.name'), dataIndex: 'name', key: 'name' },
  { title: t('common.type'), dataIndex: 'record_type', key: 'record_type', width: 100 },
  { title: t('common.value'), dataIndex: 'value', key: 'value' },
  { title: t('common.ttl'), dataIndex: 'ttl', key: 'ttl', width: 110 },
  { title: t('common.priority'), dataIndex: 'priority', key: 'priority', width: 110 },
  { title: t('common.actions'), key: 'actions', width: 120 },
]);

const loadZones = async () => {
  zones.value = await zonesApi.list();
  selectedZoneId.value ||= zones.value[0]?.id ?? null;
};

const loadRecords = async () => {
  if (!selectedZoneId.value) {
    records.value = [];
    return;
  }
  loading.value = true;
  try {
    records.value = await recordsApi.list(selectedZoneId.value);
  } catch {
    message.error(t('records.loadFailed'));
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  Object.assign(form, {
    name: '@',
    record_type: 'A',
    value: '',
    ttl: null,
    priority: null,
    weight: null,
    port: null,
    comment: '',
  });
};

const openCreate = () => {
  editingId.value = null;
  resetForm();
  modalOpen.value = true;
};

const openEdit = (record: RecordItem) => {
  editingId.value = record.id;
  Object.assign(form, record);
  modalOpen.value = true;
};

const save = async () => {
  if (!selectedZoneId.value) return;
  const payload = { ...form };
  try {
    if (editingId.value) {
      await recordsApi.update(editingId.value, payload);
      message.success(t('records.updated'));
    } else {
      await recordsApi.create(selectedZoneId.value, payload);
      message.success(t('records.created'));
    }
    modalOpen.value = false;
    await loadRecords();
  } catch {
    message.error(t('common.saveFailed'));
  }
};

const remove = (record: RecordItem) => {
  Modal.confirm({
    title: t('records.confirmDelete', { name: record.name, type: record.record_type }),
    onOk: async () => {
      await recordsApi.remove(record.id);
      message.success(t('records.deleted'));
      await loadRecords();
    },
  });
};

const importZone = async () => {
  if (!selectedZoneId.value) return;
  await zonesApi.import(selectedZoneId.value, importText.value);
  importOpen.value = false;
  message.success(t('records.imported'));
  await loadRecords();
};

watch(selectedZoneId, loadRecords);
onMounted(async () => {
  await loadZones();
  await loadRecords();
});
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('nav.records') }}</h1>
      <div class="page-actions">
        <a-select v-model:value="selectedZoneId" style="width: 260px" :placeholder="t('common.selectZone')">
          <a-select-option v-for="zone in zones" :key="zone.id" :value="zone.id">{{ zone.name }}</a-select-option>
        </a-select>
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="loadRecords" />
        <a-button :icon="h(UploadOutlined)" :disabled="!selectedZoneId" @click="importOpen = true">{{ t('common.import') }}</a-button>
        <a-button type="primary" :icon="h(PlusOutlined)" :disabled="!selectedZoneId" @click="openCreate">{{ t('records.new') }}</a-button>
      </div>
    </div>

    <a-alert v-if="selectedZone" type="info" show-icon>
      <template #message>{{ selectedZone.name }} serial {{ selectedZone.serial }}</template>
    </a-alert>

    <a-table row-key="id" :loading="loading" :columns="columns" :data-source="records" :pagination="{ pageSize: 12 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'record_type'">
          <a-tag color="purple">{{ record.record_type }}</a-tag>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button :icon="h(EditOutlined)" @click="openEdit(record)" />
            <a-button danger :icon="h(DeleteOutlined)" @click="remove(record)" />
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="editingId ? t('records.edit') : t('records.new')" @ok="save">
      <a-form layout="vertical">
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item :label="t('common.name')"><a-input v-model:value="form.name" /></a-form-item></a-col>
          <a-col :span="12">
            <a-form-item :label="t('common.type')">
              <a-select v-model:value="form.record_type">
                <a-select-option value="A">A</a-select-option>
                <a-select-option value="AAAA">AAAA</a-select-option>
                <a-select-option value="CNAME">CNAME</a-select-option>
                <a-select-option value="MX">MX</a-select-option>
                <a-select-option value="TXT">TXT</a-select-option>
                <a-select-option value="NS">NS</a-select-option>
                <a-select-option value="PTR">PTR</a-select-option>
                <a-select-option value="SRV">SRV</a-select-option>
                <a-select-option value="CAA">CAA</a-select-option>
                <a-select-option value="NAPTR">NAPTR</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item :label="t('common.value')"><a-input v-model:value="form.value" /></a-form-item>
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item :label="t('common.ttl')"><a-input-number v-model:value="form.ttl" style="width: 100%" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item :label="t('common.priority')"><a-input-number v-model:value="form.priority" style="width: 100%" /></a-form-item></a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item :label="t('common.weight')"><a-input-number v-model:value="form.weight" style="width: 100%" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item :label="t('common.port')"><a-input-number v-model:value="form.port" style="width: 100%" /></a-form-item></a-col>
        </a-row>
        <a-form-item :label="t('common.comment')"><a-input v-model:value="form.comment" /></a-form-item>
      </a-form>
    </a-modal>

    <a-modal v-model:open="importOpen" :title="t('records.importZoneFile')" width="720px" @ok="importZone">
      <a-textarea v-model:value="importText" :rows="16" class="mono" />
    </a-modal>
  </div>
</template>
