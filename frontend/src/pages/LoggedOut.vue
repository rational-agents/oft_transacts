<!-- frontend/src/pages/LoggedOut.vue -->
<script setup lang="ts">
import { onMounted } from "vue";
import { removeLocalUser } from "../lib/oidc";

onMounted(async () => {
  try { await removeLocalUser(); } catch {}
  // Leave the origin to reduce likelihood of BFCache restoring a protected DOM
  window.location.replace("https://rational-agents.ai/");
});
</script>

<template>
  <div class="p-6 text-gray-600">Signing you out…</div>
</template>