<script setup lang="ts">
import { DeleteOutlined, DownloadOutlined, EditOutlined, PlusOutlined, ReloadOutlined, SaveOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { computed, h, onMounted, reactive, ref } from 'vue';

import { joinList, parseList } from '../api/form';
import { zonesApi } from '../api/client';
import type { Zone } from '../api/types';
import { useI18n } from '../i18n';

const loading = ref(false);
const saving = ref(false);
const modalOpen = ref(false);
const editingId = ref<number | null>(null);
const zones = ref<Zone[]>([]);
const { t } = useI18n();

const form = reactive({
  name: '',
  zone_type: 'master',
  ttl: 3600,
  primary_ns: 'ns1.example.com.',
  admin_email: 'hostmaster.example.com.',
  serial: 2025010101,
  refresh: 3600,
  retry: 900,
  expire: 1209600,
  minimum_ttl: 300,
  allow_transfer: '',
  allow_update: '',
  masters: '',
  forwarders: '',
});

const columns = computed(() => [
  { title: t('zones.zone'), dataIndex: 'name', key: 'name' },
  { title: t('common.type'), dataIndex: 'zone_type', key: 'zone_type', width: 120 },
  { title: t('zones.serial'), dataIndex: 'serial', key: 'serial', width: 140 },
  { title: t('zones.records'), key: 'records', width: 110 },
  { title: 'DNSSEC', key: 'dnssec', width: 110 },
  { title: t('common.actions'), key: 'actions', width: 220 },
]);

const load = async () => {
  loading.value = true;
  try {
    zones.value = await zonesApi.list();
  } catch {
    message.error(t('zones.loadFailed'));
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  editingId.value = null;
  Object.assign(form, {
    name: '',
    zone_type: 'master',
    ttl: 3600,
    primary_ns: 'ns1.example.com.',
    admin_email: 'hostmaster.example.com.',
    serial: 2025010101,
    refresh: 3600,
    retry: 900,
    expire: 1209600,
    minimum_ttl: 300,
    allow_transfer: '',
    allow_update: '',
    masters: '',
    forwarders: '',
  });
  modalOpen.value = true;
};

const openEdit = (zone: Zone) => {
  editingId.value = zone.id;
  Object.assign(form, {
    name: zone.name,
    zone_type: zone.zone_type,
    ttl: zone.ttl,
    primary_ns: zone.primary_ns,
    admin_email: zone.admin_email,
    serial: zone.serial,
    refresh: zone.refresh,
    retry: zone.retry,
    expire: zone.expire,
    minimum_ttl: zone.minimum_ttl,
    allow_transfer: joinList(zone.allow_transfer),
    allow_update: joinList(zone.allow_update),
    masters: joinList(zone.masters),
    forwarders: joinList(zone.forwarders),
  });
  modalOpen.value = true;
};

const payload = () => ({
  ...form,
  allow_transfer: parseList(form.allow_transfer),
  allow_update: parseList(form.allow_update),
  masters: parseList(form.masters),
  forwarders: parseList(form.forwarders),
});

const save = async () => {
  saving.value = true;
  try {
    if (editingId.value) {
      await zonesApi.update(editingId.value, payload());
      message.success(t('zones.updated'));
    } else {
      await zonesApi.create(payload());
      message.success(t('zones.created'));
    }
    modalOpen.value = false;
    await load();
  } catch {
    message.error(t('common.saveFailed'));
  } finally {
    saving.value = false;
  }
};

const remove = (zone: Zone) => {
  Modal.confirm({
    title: t('common.confirmDelete', { name: zone.name }),
    onOk: async () => {
      await zonesApi.remove(zone.id);
      message.success(t('zones.deleted'));
      await load();
    },
  });
};

const writeFiles = async (zone: Zone) => {
  await zonesApi.writeFiles(zone.id);
  message.success(t('zones.filesGenerated'));
};

const downloadZone = async (zone: Zone) => {
  const text = await zonesApi.export(zone.id);
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${zone.name}.db`;
  link.click();
  URL.revokeObjectURL(url);
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">{{ t('nav.zones') }}</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(PlusOutlined)" @click="openCreate">{{ t('zones.new') }}</a-button>
      </div>
    </div>

    <a-table row-key="id" :loading="loading" :columns="columns" :data-source="zones" :pagination="{ pageSize: 10 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'zone_type'">
          <a-tag color="blue">{{ record.zone_type }}</a-tag>
        </template>
        <template v-else-if="column.key === 'records'">
          {{ record.records?.length || 0 }}
        </template>
        <template v-else-if="column.key === 'dnssec'">
          <a-tag :color="record.is_dnssec_signed ? 'green' : 'default'">
            {{ record.is_dnssec_signed ? t('zones.signed') : t('zones.unsigned') }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-tooltip :title="t('zones.exportFile')">
              <a-button :icon="h(DownloadOutlined)" @click="downloadZone(record)" />
            </a-tooltip>
            <a-tooltip :title="t('zones.generateFiles')">
              <a-button :icon="h(SaveOutlined)" @click="writeFiles(record)" />
            </a-tooltip>
            <a-tooltip :title="t('common.edit')">
              <a-button :icon="h(EditOutlined)" @click="openEdit(record)" />
            </a-tooltip>
            <a-tooltip :title="t('common.delete')">
              <a-button danger :icon="h(DeleteOutlined)" @click="remove(record)" />
            </a-tooltip>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="editingId ? t('zones.edit') : t('zones.new')" :confirm-loading="saving" @ok="save">
      <a-form layout="vertical">
        <a-form-item :label="t('zones.name')"><a-input v-model:value="form.name" placeholder="example.com" /></a-form-item>
        <a-form-item :label="t('common.type')">
          <a-select v-model:value="form.zone_type">
            <a-select-option value="master">master</a-select-option>
            <a-select-option value="slave">slave</a-select-option>
            <a-select-option value="forward">forward</a-select-option>
            <a-select-option value="hint">hint</a-select-option>
          </a-select>
        </a-form-item>
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item label="TTL"><a-input-number v-model:value="form.ttl" style="width: 100%" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item :label="t('zones.serial')"><a-input-number v-model:value="form.serial" style="width: 100%" /></a-form-item></a-col>
        </a-row>
        <a-form-item :label="t('zones.primaryNs')"><a-input v-model:value="form.primary_ns" /></a-form-item>
        <a-form-item :label="t('zones.adminEmail')"><a-input v-model:value="form.admin_email" /></a-form-item>
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item :label="t('zones.refresh')"><a-input-number v-model:value="form.refresh" style="width: 100%" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item :label="t('zones.retry')"><a-input-number v-model:value="form.retry" style="width: 100%" /></a-form-item></a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="12"><a-form-item :label="t('zones.expire')"><a-input-number v-model:value="form.expire" style="width: 100%" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item :label="t('zones.minimumTtl')"><a-input-number v-model:value="form.minimum_ttl" style="width: 100%" /></a-form-item></a-col>
        </a-row>
        <a-form-item label="allow-transfer"><a-input v-model:value="form.allow_transfer" placeholder="secondary-acl, 10.0.0.2" /></a-form-item>
        <a-form-item label="allow-update"><a-input v-model:value="form.allow_update" /></a-form-item>
        <a-form-item label="masters"><a-input v-model:value="form.masters" /></a-form-item>
        <a-form-item label="forwarders"><a-input v-model:value="form.forwarders" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
