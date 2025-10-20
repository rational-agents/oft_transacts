<template>
  <header class="bg-white border-b">
    <nav class="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
      <RouterLink to="/" class="font-semibold">OFT</RouterLink>
      <RouterLink to="/accounts" class="text-gray-700 hover:text-black">Accounts</RouterLink>
      <a :href="apiDocsUrl" target="_blank" rel="noopener noreferrer" class="text-gray-700 hover:text-black">API Docs</a>
      <button @click="hardLogout" class="ml-auto text-gray-700 hover:text-black">log out</button>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { computed } from 'vue'
import { hardLogout } from '@/lib/logout'

const apiDocsUrl = computed(() => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}/docs`
})
</script>
