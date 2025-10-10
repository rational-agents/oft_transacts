<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useQuery } from '@tanstack/vue-query'
//import { useAuth } from '@okta/okta-vue'
import { oidc } from '../lib/oidc'
import { api } from '../lib/api'

// --- Types ---
type User = {
  username: string
  email: string
}

type Account = {
  account_id: number
  account_name: string
  currency: string
  balance: number
}

type Transaction = {
  id: number
  direction: 'credit' | 'debit'
  amount: number
  currency: string
  status: 'posted' | 'pending'
  notes: string
  timestamp: string
}

// --- Auth State ---
const isAuthenticated = ref(false)

// Check authentication status using existing OIDC
onMounted(async () => {
  const user = await oidc.getUser()
  isAuthenticated.value = !!user && !user.expired
})

// --- Mock Transaction Data (as requested) ---
const allTransactions: { [key: number]: Transaction[] } = {
  1: [ // Transactions for 'chase checking'
    { id: 1, direction: 'debit', amount: 500.00, currency: 'USD', status: 'posted', notes: 'purchased ebike', timestamp: 'October 11, 2025 1:00pm' },
    { id: 2, direction: 'credit', amount: 1500.00, currency: 'USD', status: 'posted', notes: 'Paycheck deposit', timestamp: 'October 10, 2025 9:00am' },
  ],
  2: [ // Transactions for 'crypto'
    { id: 3, direction: 'credit', amount: 0.5, currency: 'BTC', status: 'pending', notes: 'Received from exchange', timestamp: 'October 9, 2025 5:45pm' },
  ]
}

// --- State ---
const selectedAccountId = ref<number | null>(null)

// --- Queries ---
const { data: user, isLoading: isUserLoading } = useQuery({
  queryKey: ['user', 'me'],
  queryFn: () => api.get<User>('/users/me'),
  enabled: isAuthenticated,
})

const { data: accounts, isLoading: areAccountsLoading } = useQuery({
  queryKey: ['accounts'],
  queryFn: () => api.get<Account[]>('/accounts'),
  enabled: isAuthenticated,
})

// --- Computed Properties ---
const transactionsForSelectedAccount = computed(() => {
  if (!selectedAccountId.value) return []
  return allTransactions[selectedAccountId.value] || []
})

// --- Methods ---
const selectAccount = (accountId: number) => {
  selectedAccountId.value = selectedAccountId.value === accountId ? null : accountId
}

const formatCurrency = (amount: number, currency: string) => {
  // Handle balances that are in cents for USD
  const value = currency === 'USD' ? amount / 100 : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: currency === 'BTC' ? 8 : 2,
  }).format(value)
}
</script>

<template>
  <div class="p-4 sm:p-6 lg:p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">

      <!-- User Details Section -->
      <section class="mb-8 p-6 bg-white rounded-xl shadow-sm border border-gray-200">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">User Profile</h2>
        <div v-if="isUserLoading" class="text-gray-500">Loading user...</div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <div class="text-sm font-medium text-gray-500">Username</div>
            <div class="text-lg text-gray-900">{{ user?.username || 'N/A' }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">Email</div>
            <div class="text-lg text-gray-900">{{ user?.email || 'N/A' }}</div>
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Accounts List Section -->
        <section class="lg:col-span-1">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">Accounts</h2>
          <div v-if="areAccountsLoading" class="text-gray-500">Loading accounts...</div>
          <ul v-else class="space-y-3">
            <li v-for="account in accounts" :key="account.account_id" @click="selectAccount(account.account_id)" class="p-4 rounded-lg border transition-all duration-200 cursor-pointer" :class="[selectedAccountId === account.account_id ? 'bg-blue-500 text-white shadow-lg ring-2 ring-blue-300' : 'bg-white hover:bg-gray-100 hover:shadow-md']">
              <div class="flex justify-between items-center">
                <div class="font-semibold text-lg">{{ account.account_name }}</div>
                <div class="font-mono text-sm px-2 py-1 rounded" :class="selectedAccountId === account.account_id ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700'">
                  {{ account.currency }}
                </div>
              </div>
              <div class="text-xl font-semibold mt-1">
                {{ formatCurrency(account.balance, account.currency) }}
              </div>
            </li>
          </ul>
        </section>

        <!-- Transactions List Section -->
        <section class="lg:col-span-2">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">Transactions</h2>
          <div v-if="!selectedAccountId" class="text-center py-12 px-6 bg-white rounded-xl shadow-sm border border-gray-200">
            <p class="text-gray-500">Select an account to view transactions.</p>
          </div>
          <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                  <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="tx in transactionsForSelectedAccount" :key="tx.id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ tx.timestamp }}</td>
                  <td class="px-6 py-4 text-sm text-gray-800">{{ tx.notes }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-right font-mono text-sm">
                    <span :class="tx.direction === 'credit' ? 'text-green-600' : 'text-red-600'">
                      {{ tx.direction === 'credit' ? '+' : '-' }} {{ tx.amount }} {{ tx.currency }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="tx.status === 'posted' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                      {{ tx.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

    </div>
  </div>
</template>
