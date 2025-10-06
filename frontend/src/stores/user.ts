import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    email: '' as string,
    username: '' as string,
  }),
  actions: {
    setUser(payload: { email: string; username: string }) {
      this.email = payload.email
      this.username = payload.username
    },
    clear() {
      this.email = ''
      this.username = ''
    },
  },
})
