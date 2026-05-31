import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/zones', component: () => import('../views/Zones.vue') },
  { path: '/records', component: () => import('../views/Records.vue') },
  { path: '/acls', component: () => import('../views/ACLs.vue') },
  { path: '/views', component: () => import('../views/Views.vue') },
  { path: '/options', component: () => import('../views/Options.vue') },
  { path: '/dnssec', component: () => import('../views/DNSSEC.vue') },
  { path: '/tsig', component: () => import('../views/TSIG.vue') },
  { path: '/replication', component: () => import('../views/Replication.vue') },
  { path: '/backup', component: () => import('../views/Backup.vue') },
  { path: '/monitoring', component: () => import('../views/Monitoring.vue') },
  { path: '/audit', component: () => import('../views/AuditLog.vue') },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
