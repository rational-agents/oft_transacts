<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { fetchJson } from '../lib/api'

type Account = { account_id: number; account_name: string; currency: string; }

const { data, isLoading, isError, error } = useQuery({
  queryKey: ['accounts'],
  queryFn: () => fetchJson<Account[]>('/api/accounts'),
})
</script>

<template>
  <section>
    <h2 class="text-xl font-semibold mb-4">Accounts</h2>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="isError" class="text-red-600">{{ (error as Error).message }}</div>
    <ul v-else class="space-y-2">
      <li v-for="a in data" :key="a.account_id" class="p-3 rounded border bg-white">
        <div class="font-medium">{{ a.account_name }}</div>
        <div class="text-sm text-gray-500">{{ a.currency }}</div>
      </li>
    </ul>
  </section>
</template>
