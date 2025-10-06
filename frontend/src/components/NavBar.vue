<template>
  <header class="bg-white border-b">
    <nav class="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
      <RouterLink to="/" class="font-semibold">OFT</RouterLink>
      <RouterLink to="/accounts" class="text-gray-700 hover:text-black">Accounts</RouterLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>
