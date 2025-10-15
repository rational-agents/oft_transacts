<template>
  <div class="min-h-screen flex flex-col">
    <NavBar />
    <main class="p-4 max-w-5xl mx-auto flex-grow">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import NavBar from './components/NavBar.vue'
import Footer from './components/Footer.vue'
</script>
