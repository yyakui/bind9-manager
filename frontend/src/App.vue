<script setup lang="ts">
import {
  ApiOutlined,
  AuditOutlined,
  CloudServerOutlined,
  ClusterOutlined,
  ControlOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  FileProtectOutlined,
  HddOutlined,
  KeyOutlined,
  LockOutlined,
  LogoutOutlined,
  SafetyCertificateOutlined,
  SettingOutlined,
  ShareAltOutlined,
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { computed, h, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useSessionStore } from './stores/session';

const router = useRouter();
const route = useRoute();
const session = useSessionStore();

const loginForm = reactive({
  username: 'admin',
  password: '',
  loading: false,
});

const menuItems = [
  { key: '/dashboard', icon: () => h(DashboardOutlined), label: 'Dashboard' },
  { key: '/zones', icon: () => h(CloudServerOutlined), label: 'Zones' },
  { key: '/records', icon: () => h(DatabaseOutlined), label: 'Records' },
  { key: '/acls', icon: () => h(LockOutlined), label: 'ACLs' },
  { key: '/views', icon: () => h(ClusterOutlined), label: 'Views' },
  { key: '/options', icon: () => h(SettingOutlined), label: 'Options' },
  { key: '/dnssec', icon: () => h(SafetyCertificateOutlined), label: 'DNSSEC' },
  { key: '/tsig', icon: () => h(KeyOutlined), label: 'TSIG' },
  { key: '/replication', icon: () => h(ShareAltOutlined), label: 'Replication' },
  { key: '/backup', icon: () => h(FileProtectOutlined), label: 'Backup' },
  { key: '/monitoring', icon: () => h(ControlOutlined), label: 'Monitoring' },
  { key: '/audit', icon: () => h(AuditOutlined), label: 'Audit Log' },
];

const selectedKeys = computed(() => [route.path]);

const goToMenu = ({ key }: { key: string | number }) => {
  router.push(String(key));
};

const doLogin = async () => {
  loginForm.loading = true;
  try {
    await session.login(loginForm.username, loginForm.password);
    message.success('Signed in');
    await router.push('/dashboard');
  } catch {
    message.error('Login failed');
  } finally {
    loginForm.loading = false;
  }
};

const logout = () => {
  session.logout();
  message.success('Signed out');
};
</script>

<template>
  <a-config-provider
    :theme="{
      token: {
        colorPrimary: '#167d7f',
        borderRadius: 6,
        fontSize: 14,
      },
    }"
  >
    <div v-if="!session.token" class="login-shell">
      <div class="login-panel">
        <div class="login-mark"><HddOutlined /></div>
        <h1>BIND9 Manager</h1>
        <a-form layout="vertical" @submit.prevent="doLogin">
          <a-form-item label="Username">
            <a-input v-model:value="loginForm.username" autocomplete="username" />
          </a-form-item>
          <a-form-item label="Password">
            <a-input-password v-model:value="loginForm.password" autocomplete="current-password" />
          </a-form-item>
          <a-button type="primary" block :loading="loginForm.loading" @click="doLogin">Sign in</a-button>
        </a-form>
      </div>
    </div>

    <a-layout v-else class="app-layout">
      <a-layout-sider breakpoint="lg" collapsed-width="0" width="232" class="app-sider">
        <div class="brand">
          <ApiOutlined />
          <span>BIND9 Manager</span>
        </div>
        <a-menu
          mode="inline"
          theme="dark"
          :selected-keys="selectedKeys"
          :items="menuItems"
          @click="goToMenu"
        />
      </a-layout-sider>
      <a-layout>
        <a-layout-header class="app-header">
          <div>
            <strong>{{ route.path.split('/')[1] || 'dashboard' }}</strong>
          </div>
          <a-space>
            <a-tag color="cyan">{{ session.role }}</a-tag>
            <span>{{ session.username }}</span>
            <a-tooltip title="Sign out">
              <a-button shape="circle" :icon="h(LogoutOutlined)" @click="logout" />
            </a-tooltip>
          </a-space>
        </a-layout-header>
        <a-layout-content class="app-content">
          <router-view />
        </a-layout-content>
      </a-layout>
    </a-layout>
  </a-config-provider>
</template>

<style scoped>
.login-shell {
  align-items: center;
  background:
    linear-gradient(135deg, rgba(22, 125, 127, 0.08), rgba(180, 83, 9, 0.08)),
    #f3f5f7;
  display: flex;
  min-height: 100vh;
  justify-content: center;
  padding: 24px;
}

.login-panel {
  background: #fff;
  border: 1px solid #dce3ea;
  border-radius: 8px;
  box-shadow: 0 16px 45px rgba(42, 54, 71, 0.12);
  width: min(420px, 100%);
  padding: 28px;
}

.login-mark {
  align-items: center;
  background: #e6f4f1;
  border-radius: 8px;
  color: #167d7f;
  display: inline-flex;
  font-size: 26px;
  height: 44px;
  justify-content: center;
  margin-bottom: 14px;
  width: 44px;
}

.login-panel h1 {
  font-size: 24px;
  margin: 0 0 22px;
}

.app-layout {
  min-height: 100vh;
}

.app-sider {
  background: #26313b;
}

.brand {
  align-items: center;
  color: #fff;
  display: flex;
  font-size: 16px;
  font-weight: 700;
  gap: 10px;
  height: 56px;
  padding: 0 18px;
}

.app-header {
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e1e6eb;
  display: flex;
  height: 56px;
  justify-content: space-between;
  padding: 0 20px;
}

.app-content {
  padding: 20px;
}
</style>
