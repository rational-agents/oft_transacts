<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { oidc } from '../lib/oidc'
import { api } from '../lib/api'
import TransactionEditModal from '../components/TransactionEditModal.vue'
import { formatBaseUnitsToDisplay, formatAmountWithCurrency, validateAmountPrecision, getInputStep } from '../lib/currency'

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
  trans_id: number
  account_id: number
  occurred_at: string
  amount_cents: number
  direction: 'credit' | 'debit'
  trans_status: 'posted' | 'deleted'
  notes: string
}

type TransactsPage = {
  items: Transaction[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

// --- Auth State ---
const isAuthenticated = ref(false)

// Check authentication status using existing OIDC
onMounted(async () => {
  const user = await oidc.getUser()
  isAuthenticated.value = !!user && !user.expired
})

// --- State ---
const selectedAccountId = ref<number | null>(null)
const currentPage = ref(1)
const allLoadedTransactions = ref<Transaction[]>([])

// --- Form State ---
const newTransactionNotes = ref('')
const newTransactionAmount = ref('')
const newTransactionDirection = ref<'credit' | 'debit'>('debit')
const newTransactionAmountError = ref('')

// modal state
const selectedTransactionId = ref<number | null>(null)
const isModalOpen = ref(false)

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

const { 
  data: transactsPage, 
  isLoading: areTransactsLoading,
  refetch: refetchTransacts 
} = useQuery({
  queryKey: ['transacts', selectedAccountId, currentPage],
  queryFn: () => {
    if (!selectedAccountId.value) return null
    return api.get<TransactsPage>(
      `/accounts/${selectedAccountId.value}/transacts?page=${currentPage.value}`
    )
  },
  enabled: computed(() => isAuthenticated.value && selectedAccountId.value !== null),
})

// Watch for new transacts data and append to list
watch(transactsPage, (newPage) => {
  if (newPage && newPage.items) {
    if (currentPage.value === 1) {
      // First page - replace all
      allLoadedTransactions.value = newPage.items
    } else {
      // Subsequent pages - append
      allLoadedTransactions.value = [...allLoadedTransactions.value, ...newPage.items]
    }
  }
})

// Watch for account selection changes
watch(selectedAccountId, () => {
  // Reset pagination when account changes
  currentPage.value = 1
  allLoadedTransactions.value = []
})

// --- Computed Properties ---
const selectedAccount = computed(() => {
  if (!selectedAccountId.value || !accounts.value) return null
  return accounts.value.find(acc => acc.account_id === selectedAccountId.value)
})

const hasMoreTransactions = computed(() => {
  return transactsPage.value?.has_more ?? false
})

// --- Methods ---
const selectAccount = (accountId: number) => {
  selectedAccountId.value = selectedAccountId.value === accountId ? null : accountId
}

const loadMoreTransactions = () => {
  currentPage.value += 1
}

const formatCurrency = (amount: number, currency: string) => {
  // Balance is stored in base units (cents for USD, satoshis for BTC)
  const value = formatBaseUnitsToDisplay(amount, currency)
  const numValue = parseFloat(value)
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: currency === 'USD' ? 2 : 0,
    maximumFractionDigits: currency === 'USD' ? 2 : 8,
  }).format(numValue)
}

const formatAmount = (amountCents: number, currency: string) => {
  return formatAmountWithCurrency(amountCents, currency)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}

// method to open modal
const openTransactionModal = (transactionId: number) => {
  selectedTransactionId.value = transactionId
  isModalOpen.value = true
}

const closeTransactionModal = () => {
  isModalOpen.value = false
  selectedTransactionId.value = null
}

const handleTransactionUpdated = () => {
  // Modal will handle cache invalidation
  // List will automatically update via query invalidation
}

const handleTransactionDeleted = () => {
  // Modal will handle cache invalidation and close
  // List will automatically update via query invalidation
}

// --- Mutations ---
const queryClient = useQueryClient()

const createTransactionMutation = useMutation({
  mutationFn: async (data: { notes: string; amount_cents: number; direction: 'credit' | 'debit' }) => {
    return api.post<Transaction>(
      `/accounts/${selectedAccountId.value}/transacts`,
      data
    )
  },
  onMutate: async (newTransaction) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['transacts', selectedAccountId.value, currentPage.value] })
    
    // Snapshot the previous value
    const previousTransactions = allLoadedTransactions.value
    
    // Optimistically update to the new value
    const optimisticTransaction: Transaction = {
      trans_id: Date.now(), // temporary ID
      account_id: selectedAccountId.value!,
      occurred_at: new Date().toISOString(),
      amount_cents: newTransaction.amount_cents,
      direction: newTransaction.direction,
      trans_status: 'posted',
      notes: newTransaction.notes
    }
    
    // Add to top of list
    allLoadedTransactions.value = [optimisticTransaction, ...allLoadedTransactions.value]
    
    // Return context with previous value
    return { previousTransactions }
  },
  onError: (err, newTransaction, context) => {
    // Rollback on error
    if (context?.previousTransactions) {
      allLoadedTransactions.value = context.previousTransactions
    }
  },
  onSuccess: (createdTransaction) => {
    // Replace optimistic transaction with real one from server
    const optimisticIndex = allLoadedTransactions.value.findIndex(
      tx => tx.trans_id > 1000000000000 // Find optimistic transaction by temporary ID
    )
    
    if (optimisticIndex >= 0) {
      allLoadedTransactions.value[optimisticIndex] = createdTransaction
    }
    
    // Clear form
    newTransactionNotes.value = ''
    newTransactionAmount.value = ''
    newTransactionDirection.value = 'debit'
    
    // Invalidate queries to ensure consistency
    queryClient.invalidateQueries({ queryKey: ['transacts', selectedAccountId.value] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
  }
})

const submitNewTransaction = () => {
  if (!newTransactionNotes.value || !newTransactionAmount.value) {
    return
  }
  
  const currency = selectedAccount.value?.currency || 'USD'
  const validation = validateAmountPrecision(newTransactionAmount.value, currency)
  
  if (!validation.isValid) {
    newTransactionAmountError.value = validation.errorMessage || 'Invalid amount'
    return
  }
  
  newTransactionAmountError.value = ''
  
  createTransactionMutation.mutate({
    notes: newTransactionNotes.value,
    amount_cents: validation.valueInBaseUnits!,
    direction: newTransactionDirection.value
  })
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
          <!-- Add Transaction Form -->
          <div v-if="selectedAccountId" class="mb-4 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <form @submit.prevent="submitNewTransaction" class="flex items-center divide-x divide-gray-200">
              <!-- Notes Field -->
              <div class="flex-1 px-6 py-4">
                <input
                  v-model="newTransactionNotes"
                  type="text"
                  placeholder="Transact description..."
                  class="w-full text-sm text-gray-800 focus:outline-none"
                  :disabled="createTransactionMutation.isPending.value"
                />
              </div>
              
              <!-- Direction Select -->
              <div class="px-6 py-4">
                <select
                  v-model="newTransactionDirection"
                  class="text-sm text-gray-800 focus:outline-none cursor-pointer"
                  :disabled="createTransactionMutation.isPending.value"
                >
                  <option value="debit">Debit (-)</option>
                  <option value="credit">Credit (+)</option>
                </select>
              </div>
              
              <!-- Amount Field -->
              <div class="px-6 py-4">
                <input
                  v-model="newTransactionAmount"
                  type="number"
                  :step="getInputStep(selectedAccount?.currency || 'USD')"
                  min="0"
                  :placeholder="`Amount (${selectedAccount?.currency || 'USD'})`"
                  class="w-32 text-right font-mono text-sm text-gray-800 focus:outline-none"
                  :class="{ 'border-red-500': newTransactionAmountError }"
                  :disabled="createTransactionMutation.isPending.value"
                  @input="newTransactionAmountError = ''"
                />
              </div>
              
              <!-- Submit Button -->
              <div class="px-6 py-4">
                <button
                  type="submit"
                  :disabled="!newTransactionNotes || !newTransactionAmount || createTransactionMutation.isPending.value"
                  class="px-4 py-1 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors">
                  {{ createTransactionMutation.isPending.value ? 'Adding...' : 'Add' }}
                </button>
              </div>
            </form>
            <!-- Validation Error -->
            <div v-if="newTransactionAmountError" class="px-6 py-2 bg-red-50 border-l-4 border-red-500">
              <p class="text-sm text-red-700">{{ newTransactionAmountError }}</p>
            </div>
          </div>
          <div v-if="!selectedAccountId" class="text-center py-12 px-6 bg-white rounded-xl shadow-sm border border-gray-200">
            <p class="text-gray-500">Select an account to view transactions.</p>
          </div>
          <div v-else-if="areTransactsLoading && currentPage === 1" class="text-center py-12 px-6 bg-white rounded-xl shadow-sm border border-gray-200">
            <p class="text-gray-500">Loading transactions...</p>
          </div>
          <div v-else-if="allLoadedTransactions.length === 0" class="text-center py-12 px-6 bg-white rounded-xl shadow-sm border border-gray-200">
            <p class="text-gray-500">No transactions yet</p>
          </div>
          <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                  <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr 
                  v-for="tx in allLoadedTransactions" 
                  :key="tx.trans_id"
                  @click="openTransactionModal(tx.trans_id)"
                  class="cursor-pointer hover:bg-gray-100 hover:shadow-md transition-all duration-200"
                >
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ formatDate(tx.occurred_at) }}</td>
                  <td class="px-6 py-4 text-sm text-gray-800">{{ tx.notes }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-right font-mono text-sm">
                    <span :class="tx.direction === 'credit' ? 'text-green-600' : 'text-red-600'">
                      {{ tx.direction === 'credit' ? '+' : '-' }} {{ formatAmount(tx.amount_cents, selectedAccount?.currency || 'USD') }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="tx.trans_status === 'posted' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                      {{ tx.trans_status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-gray-400">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <!-- Load More Link -->
            <div v-if="hasMoreTransactions" class="p-4 text-center border-t border-gray-200">
              <a 
                @click="loadMoreTransactions" 
                class="text-blue-600 hover:text-blue-800 underline cursor-pointer"
              >
                Load more transactions
              </a>
            </div>
          </div>
        </section>
      </div>

    </div>
    <!-- Transaction Edit Modal -->
    <TransactionEditModal
      :is-open="isModalOpen"
      :transaction-id="selectedTransactionId"
      :account-id="selectedAccountId || 0"
      :currency="selectedAccount?.currency || 'USD'"
      @close="closeTransactionModal"
      @updated="handleTransactionUpdated"
      @deleted="handleTransactionDeleted"
    />
  </div>
</template>