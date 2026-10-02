<script setup lang="ts">
import { ArrowLeft } from "lucide-vue-next";
</script>

<template>
  <NuxtLink
    to="/dashboard"
    class="group inline-flex min-h-10 items-center gap-2 rounded-xl border border-[var(--vl-border)] bg-[var(--vl-surface)] px-4 py-2 text-sm font-semibold text-[var(--vl-sage-dark)] shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-[var(--vl-sage-dark)]/30 hover:bg-[var(--vl-sage)]/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--vl-sage-dark)]"
  >
    <ArrowLeft :size="16" aria-hidden="true" class="transition-transform duration-200 group-hover:-translate-x-0.5" />
    <span>Back to Dashboard</span>
  </NuxtLink>
</template>
