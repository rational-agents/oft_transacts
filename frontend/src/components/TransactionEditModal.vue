<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { api } from '../lib/api'

// Props & Emits
interface Props {
  isOpen: boolean
  transactionId: number | null
  accountId: number
  currency: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  updated: []
  deleted: []
}>()

// Types
type Transaction = {
  trans_id: number
  account_id: number
  occurred_at: string
  amount_cents: number
  direction: 'credit' | 'debit'
  trans_status: 'posted' | 'deleted'
  notes: string
}

// State
const editNotes = ref('')
const editAmount = ref('')
const editDirection = ref<'credit' | 'debit'>('debit')
const showConfirmSaveOnClose = ref(false)
const showConfirmSaveOnDelete = ref(false)
const successMessage = ref('')
const pendingAction = ref<'close' | 'delete' | null>(null)

// Query for transaction detail
const { data: transaction, isLoading } = useQuery({
  queryKey: computed(() => ['transactions:detail', props.transactionId]),
  queryFn: () => {
    if (!props.transactionId) return null
    return api.get<Transaction>(
      `/accounts/${props.accountId}/transacts/${props.transactionId}`
    )
  },
  enabled: computed(() => props.isOpen && props.transactionId !== null),
})

// Watch transaction data and populate form
watch(transaction, (newTransaction) => {
  if (newTransaction) {
    editNotes.value = newTransaction.notes
    editAmount.value = (newTransaction.amount_cents / 100).toFixed(2)
    editDirection.value = newTransaction.direction
  }
}, { immediate: true })

// Computed
const isDirty = computed(() => {
  if (!transaction.value) return false
  
  const currentAmountCents = Math.round(parseFloat(editAmount.value) * 100)
  
  return (
    editNotes.value !== transaction.value.notes ||
    currentAmountCents !== transaction.value.amount_cents ||
    editDirection.value !== transaction.value.direction
  )
})

const isDeleteButtonVisible = computed(() => {
  return transaction.value?.trans_status === 'posted'
})

const isFormValid = computed(() => {
  const amount = parseFloat(editAmount.value)
  return (
    editNotes.value.trim() !== '' &&
    !isNaN(amount) &&
    amount > 0 &&
    (editDirection.value === 'credit' || editDirection.value === 'debit')
  )
})

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

// Mutations
const queryClient = useQueryClient()

const updateMutation = useMutation({
  mutationFn: async (data: { notes: string; amount_cents: number; direction: 'credit' | 'debit' }) => {
    return api.patch<Transaction>(
      `/accounts/${props.accountId}/transacts/${props.transactionId}`,
      data
    )
  },
  onSuccess: (updatedTransaction) => {
    // Invalidate caches
    queryClient.invalidateQueries({ queryKey: ['transacts', props.accountId] })
    queryClient.invalidateQueries({ queryKey: ['transactions:detail', props.transactionId] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
    
    // Show success message
    successMessage.value = 'Transaction updated successfully!'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
    emit('updated')
    
    // Handle pending actions
    if (pendingAction.value === 'close') {
      pendingAction.value = null
      handleClose(true)
    } else if (pendingAction.value === 'delete') {
      pendingAction.value = null
      executeSoftDelete()
    }
  }
})

const deleteMutation = useMutation({
  mutationFn: async () => {
    return api.patch<Transaction>(
      `/accounts/${props.accountId}/transacts/${props.transactionId}`,
      { trans_status: 'deleted' }
    )
  },
  onSuccess: () => {
    // Invalidate caches
    queryClient.invalidateQueries({ queryKey: ['transacts', props.accountId] })
    queryClient.invalidateQueries({ queryKey: ['transactions:detail', props.transactionId] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
    
    emit('deleted')
    handleClose(true)
  }
})

// Methods
const handleSave = () => {
  if (!isFormValid.value) return
  
  const amountInCents = Math.round(parseFloat(editAmount.value) * 100)
  
  updateMutation.mutate({
    notes: editNotes.value,
    amount_cents: amountInCents,
    direction: editDirection.value
  })
}

const handleDelete = () => {
  if (isDirty.value) {
    showConfirmSaveOnDelete.value = true
  } else {
    executeSoftDelete()
  }
}

const executeSoftDelete = () => {
  showConfirmSaveOnDelete.value = false
  deleteMutation.mutate()
}

const handleDeleteWithSave = () => {
  showConfirmSaveOnDelete.value = false
  pendingAction.value = 'delete'
  handleSave()
}

const handleDeleteWithoutSave = () => {
  showConfirmSaveOnDelete.value = false
  executeSoftDelete()
}

const handleClose = (force = false) => {
  if (!force && isDirty.value) {
    showConfirmSaveOnClose.value = true
  } else {
    showConfirmSaveOnClose.value = false
    showConfirmSaveOnDelete.value = false
    successMessage.value = ''
    pendingAction.value = null
    emit('close')
  }
}

const handleCloseWithSave = () => {
  showConfirmSaveOnClose.value = false
  pendingAction.value = 'close'
  handleSave()
}

const handleCloseWithoutSave = () => {
  handleClose(true)
}
</script>

<template>
  <!-- Backdrop -->
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="handleClose()">
    <!-- Modal -->
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 class="text-xl font-bold text-gray-800">Edit Transaction</h3>
      </div>

      <!-- Body -->
      <div v-if="isLoading" class="px-6 py-12 text-center text-gray-500">
        Loading transaction...
      </div>
      <div v-else-if="transaction" class="px-6 py-6 space-y-6">
        <!-- Success Message -->
        <div v-if="successMessage" class="p-4 bg-green-100 text-green-800 rounded-lg border border-green-200">
          {{ successMessage }}
        </div>

        <!-- Confirm Save on Close Dialog -->
        <div v-if="showConfirmSaveOnClose" class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-yellow-800 mb-4">You have unsaved changes. Do you want to save before closing?</p>
          <div class="flex gap-3">
            <button @click="handleCloseWithSave" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium">
              Yes, Save
            </button>
            <button @click="handleCloseWithoutSave" class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 text-sm font-medium">
              No, Discard
            </button>
          </div>
        </div>

        <!-- Confirm Save on Delete Dialog -->
        <div v-if="showConfirmSaveOnDelete" class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-yellow-800 mb-4">You have unsaved changes. Do you want to save before deleting?</p>
          <div class="flex gap-3">
            <button @click="handleDeleteWithSave" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium">
              Yes, Save Then Delete
            </button>
            <button @click="handleDeleteWithoutSave" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium">
              No, Just Delete
            </button>
          </div>
        </div>

        <!-- Read-only Fields -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Date</label>
            <div class="px-3 py-2 bg-gray-100 rounded text-sm text-gray-700">
              {{ formatDate(transaction.occurred_at) }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Currency</label>
            <div class="px-3 py-2 bg-gray-100 rounded text-sm text-gray-700 font-mono">
              {{ currency }}
            </div>
          </div>
        </div>

        <!-- Editable Fields -->
        <div>
          <label for="edit-notes" class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
          <input
            id="edit-notes"
            v-model="editNotes"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="updateMutation.isPending.value || deleteMutation.isPending.value"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="edit-amount" class="block text-sm font-medium text-gray-700 mb-1">Amount</label>
            <input
              id="edit-amount"
              v-model="editAmount"
              type="number"
              step="0.01"
              min="0.01"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
              :disabled="updateMutation.isPending.value || deleteMutation.isPending.value"
            />
          </div>
          <div>
            <label for="edit-direction" class="block text-sm font-medium text-gray-700 mb-1">Direction</label>
            <select
              id="edit-direction"
              v-model="editDirection"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="updateMutation.isPending.value || deleteMutation.isPending.value"
            >
              <option value="debit">Debit (-)</option>
              <option value="credit">Credit (+)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-between">
        <div>
          <button
            v-if="isDeleteButtonVisible"
            @click="handleDelete"
            :disabled="updateMutation.isPending.value || deleteMutation.isPending.value"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium transition-colors"
          >
            {{ deleteMutation.isPending.value ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
        <div class="flex gap-3">
          <button
            @click="handleClose()"
            :disabled="updateMutation.isPending.value || deleteMutation.isPending.value"
            class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 disabled:bg-gray-200 disabled:cursor-not-allowed text-sm font-medium transition-colors"
          >
            Close
          </button>
          <button
            @click="handleSave"
            :disabled="!isFormValid || !isDirty || updateMutation.isPending.value || deleteMutation.isPending.value"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium transition-colors"
          >
            {{ updateMutation.isPending.value ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>