import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Accounts from '../pages/Accounts.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/accounts', name: 'accounts', component: Accounts },
  ],
})

export default router
