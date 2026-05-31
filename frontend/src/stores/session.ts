import { defineStore } from 'pinia';

import { authApi } from '../api/client';

export const useSessionStore = defineStore('session', {
  state: () => ({
    token: localStorage.getItem('bind9-token') || '',
    username: localStorage.getItem('bind9-username') || '',
    role: localStorage.getItem('bind9-role') || '',
  }),
  actions: {
    async login(username: string, password: string) {
      const data = await authApi.login(username, password);
      this.token = data.access_token;
      this.username = data.username;
      this.role = data.role;
      localStorage.setItem('bind9-token', data.access_token);
      localStorage.setItem('bind9-username', data.username);
      localStorage.setItem('bind9-role', data.role);
    },
    logout() {
      this.token = '';
      this.username = '';
      this.role = '';
      localStorage.removeItem('bind9-token');
      localStorage.removeItem('bind9-username');
      localStorage.removeItem('bind9-role');
    },
  },
});
