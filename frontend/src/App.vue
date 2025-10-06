<template>
  <div>
    <NavBar />
    <main class="p-4 max-w-5xl mx-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import NavBar from './components/NavBar.vue'
</script>
