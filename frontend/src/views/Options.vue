<script setup lang="ts">
import { ReloadOutlined, SaveOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { h, onMounted, reactive, ref } from 'vue';

import { optionsApi } from '../api/client';
import { joinList, parseJson, parseList, toJsonText } from '../api/form';

const loading = ref(false);
const saving = ref(false);
const form = reactive({
  listen_on: '',
  listen_on_v6: '',
  forwarders: '',
  forward_mode: 'first',
  recursion: true,
  allow_query: '',
  allow_recursion: '',
  dnssec_validation: 'auto',
  response_policy: '',
  rate_limit: '{}',
  logging_channels: '{}',
  logging_categories: '{}',
});

const load = async () => {
  loading.value = true;
  try {
    const options = await optionsApi.get();
    Object.assign(form, {
      listen_on: joinList(options.listen_on),
      listen_on_v6: joinList(options.listen_on_v6),
      forwarders: joinList(options.forwarders),
      forward_mode: options.forward_mode,
      recursion: options.recursion,
      allow_query: joinList(options.allow_query),
      allow_recursion: joinList(options.allow_recursion),
      dnssec_validation: options.dnssec_validation,
      response_policy: joinList(options.response_policy),
      rate_limit: toJsonText(options.rate_limit),
      logging_channels: toJsonText(options.logging_channels),
      logging_categories: toJsonText(options.logging_categories),
    });
  } catch {
    message.error('Failed to load options');
  } finally {
    loading.value = false;
  }
};

const save = async () => {
  saving.value = true;
  try {
    await optionsApi.update({
      listen_on: parseList(form.listen_on),
      listen_on_v6: parseList(form.listen_on_v6),
      forwarders: parseList(form.forwarders),
      forward_mode: form.forward_mode,
      recursion: form.recursion,
      allow_query: parseList(form.allow_query),
      allow_recursion: parseList(form.allow_recursion),
      dnssec_validation: form.dnssec_validation,
      response_policy: parseList(form.response_policy),
      rate_limit: parseJson(form.rate_limit, {}),
      logging_channels: parseJson(form.logging_channels, {}),
      logging_categories: parseJson(form.logging_categories, {}),
    });
    message.success('Options saved');
    await load();
  } catch {
    message.error('Save failed');
  } finally {
    saving.value = false;
  }
};

onMounted(load);
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Global Options</h1>
      <div class="page-actions">
        <a-button :icon="h(ReloadOutlined)" :loading="loading" @click="load" />
        <a-button type="primary" :icon="h(SaveOutlined)" :loading="saving" @click="save">Save</a-button>
      </div>
    </div>

    <div class="section">
      <a-form layout="vertical">
        <a-row :gutter="16">
          <a-col :xs="24" :lg="12">
            <a-form-item label="listen-on"><a-input v-model:value="form.listen_on" /></a-form-item>
            <a-form-item label="listen-on-v6"><a-input v-model:value="form.listen_on_v6" /></a-form-item>
            <a-form-item label="forwarders"><a-input v-model:value="form.forwarders" /></a-form-item>
            <a-form-item label="forward mode">
              <a-segmented v-model:value="form.forward_mode" :options="['first', 'only']" />
            </a-form-item>
            <a-form-item label="recursion"><a-switch v-model:checked="form.recursion" /></a-form-item>
          </a-col>
          <a-col :xs="24" :lg="12">
            <a-form-item label="allow-query"><a-input v-model:value="form.allow_query" /></a-form-item>
            <a-form-item label="allow-recursion"><a-input v-model:value="form.allow_recursion" /></a-form-item>
            <a-form-item label="dnssec-validation">
              <a-segmented v-model:value="form.dnssec_validation" :options="['auto', 'yes', 'no']" />
            </a-form-item>
            <a-form-item label="response-policy zones"><a-input v-model:value="form.response_policy" /></a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :xs="24" :lg="8">
            <a-form-item label="rate-limit JSON"><a-textarea v-model:value="form.rate_limit" :rows="8" class="mono" /></a-form-item>
          </a-col>
          <a-col :xs="24" :lg="8">
            <a-form-item label="logging channels JSON"><a-textarea v-model:value="form.logging_channels" :rows="8" class="mono" /></a-form-item>
          </a-col>
          <a-col :xs="24" :lg="8">
            <a-form-item label="logging categories JSON"><a-textarea v-model:value="form.logging_categories" :rows="8" class="mono" /></a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </div>
  </div>
</template>
