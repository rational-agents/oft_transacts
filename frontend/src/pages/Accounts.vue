<script setup lang="ts">
</script>

<template>
  <div class="p-4 sm:p-6 lg:p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">

      <!-- User Details Section -->
      <section class="mb-8 p-6 bg-white rounded-xl shadow-sm border border-gray-200">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">User Profile</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <div class="text-sm font-medium text-gray-500">Username</div>
            <div class="text-lg text-gray-900">john kelly</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">Email</div>
            <div class="text-lg text-gray-900">john.kelly@rational-agents.ai</div>
          </div>
        </div>
      </section>

      <!-- Accounts List Section -->
      <section>
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Accounts</h2>
        <ul class="space-y-3">
          <!-- Account Item 1 -->
          <li class="p-4 rounded-lg border bg-white hover:bg-gray-100 hover:shadow-md transition-all duration-200 cursor-pointer">
            <div class="flex justify-between items-center">
              <div class="font-semibold text-lg">chase checking</div>
              <div class="font-mono text-sm px-2 py-1 rounded bg-gray-100 text-gray-700">
                USD
              </div>
            </div>
            <div class="text-xl font-semibold mt-1">
              $500.00
            </div>
          </li>

          <!-- Account Item 2 -->
          <li class="p-4 rounded-lg border bg-white hover:bg-gray-100 hover:shadow-md transition-all duration-200 cursor-pointer">
            <div class="flex justify-between items-center">
              <div class="font-semibold text-lg">crypto</div>
              <div class="font-mono text-sm px-2 py-1 rounded bg-gray-100 text-gray-700">
                BTC
              </div>
            </div>
            <div class="text-xl font-semibold mt-1">
              1.00000000
            </div>
          </li>

        </ul>
      </section>

    </div>
  </div>
</template>
