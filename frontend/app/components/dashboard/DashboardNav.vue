<script setup lang="ts">
const links = [
  ["Overview", "/dashboard"], ["Investigations", "/dashboard/analyses"], ["Evidence", "/dashboard/evidence"],
  ["Knowledge Graph", "/dashboard/knowledge-graph"], ["Model Lab", "/dashboard/model-lab"], ["AI Pipeline", "/dashboard/ai-pipeline"],
  ["Reports", "/dashboard/reports"], ["Activity", "/dashboard/activity"], ["Settings", "/dashboard/settings"],
] as const;
</script>
<template>
  <nav class="flex flex-wrap gap-2 border-b border-[var(--vl-border)] pb-4" aria-label="Dashboard">
    <NuxtLink v-for="[label, to] in links" :key="to" :to="to" class="rounded-full border border-[var(--vl-border)] bg-[var(--vl-surface)] px-3 py-2 text-xs font-semibold text-[var(--vl-muted)] transition hover:text-[var(--vl-ink)]">{{ label }}</NuxtLink>
  </nav>
</template>

