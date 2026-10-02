```vue
<script setup lang="ts">
import VeriLensLogo from "../branding/VeriLensLogo.vue"
</script>

<template>
  <footer
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-16 sm:py-20"
  >
    <div
      class="pointer-events-none absolute left-1/2 top-0 h-72 w-72 -translate-x-1/2 rounded-full bg-[var(--vl-sage)]/5 blur-[120px]"
    />

    <div class="vl-container relative">
      <div
        class="grid gap-12 lg:grid-cols-[1fr_auto] lg:items-end"
      >
        <!-- Brand -->
        <div>
          <NuxtLink
            to="/"
            class="inline-flex items-center gap-3"
            aria-label="VeriLens home"
          >
            <VeriLensLogo size="md" />

            <div class="leading-none">
              <p
                class="text-base font-bold tracking-[-0.03em] text-[var(--vl-ink)]"
              >
                VeriLens
              </p>

              <p
                class="mt-1 text-[8px] font-semibold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
              >
                Evidence Intelligence
              </p>
            </div>
          </NuxtLink>

          <p
            class="mt-6 max-w-md text-sm leading-6 text-[var(--vl-muted)]"
          >
            A multimodal AI authenticity and evidence intelligence
            platform built to make predictions more transparent,
            traceable, and understandable.
          </p>

          <p
            class="mt-5 text-xs font-medium text-[var(--vl-muted)]"
          >
            Built with AI · ML · NLP · Computer Vision · Evidence Graphs
          </p>
        </div>

        <!-- Contact -->
        <div>
          <p class="vl-eyebrow">
            Connect
          </p>

          <div class="mt-5 flex flex-col gap-3">
            <a
              href="mailto:rutvilandge@gmail.com"
              class="group inline-flex items-center gap-3 text-sm font-medium text-[var(--vl-ink)] transition-colors duration-300 hover:text-[var(--vl-sage-dark)]"
            >
              <span
                class="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--vl-border)] bg-white/40 text-[10px] transition-all duration-300 group-hover:-translate-y-0.5 group-hover:bg-[var(--vl-sage)]/10"
              >
                @
              </span>

              <span>
                rutvilandge@gmail.com
              </span>
            </a>

            <a
              href="https://github.com/rutvilandge"
              target="_blank"
              rel="noopener noreferrer"
              class="group inline-flex items-center gap-3 text-sm font-medium text-[var(--vl-ink)] transition-colors duration-300 hover:text-[var(--vl-sage-dark)]"
            >
              <span
                class="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--vl-border)] bg-white/40 text-[10px] font-bold transition-all duration-300 group-hover:-translate-y-0.5 group-hover:bg-[var(--vl-sage)]/10"
              >
                GH
              </span>

              <span>
                github.com/rutvilandge
              </span>

              <span
                class="text-[var(--vl-muted)] transition-transform duration-300 group-hover:translate-x-1"
              >
                ↗
              </span>
            </a>

            <a
              href="https://www.linkedin.com/in/rutvi-landge-9988413b0"
              target="_blank"
              rel="noopener noreferrer"
              class="group inline-flex items-center gap-3 text-sm font-medium text-[var(--vl-ink)] transition-colors duration-300 hover:text-[var(--vl-sage-dark)]"
            >
              <span
                class="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--vl-border)] bg-white/40 text-[10px] font-bold transition-all duration-300 group-hover:-translate-y-0.5 group-hover:bg-[var(--vl-sage)]/10"
              >
                in
              </span>

              <span>
                linkedin.com/in/rutvi-landge-9988413b0
              </span>

              <span
                class="text-[var(--vl-muted)] transition-transform duration-300 group-hover:translate-x-1"
              >
                ↗
              </span>
            </a>
          </div>
        </div>
      </div>

      <!-- Bottom -->
      <div
        class="mt-14 flex flex-col gap-4 border-t border-[var(--vl-border)] pt-6 sm:flex-row sm:items-center sm:justify-between"
      >
        <p
          class="text-[10px] font-medium text-[var(--vl-muted)]"
        >
          © {{ new Date().getFullYear() }} Rutvi Landge. Built with purpose.
        </p>

        <div
          class="flex items-center gap-3 text-[9px] font-semibold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
        >
          <span>VeriLens</span>

          <span>·</span>

          <span>AI Authenticity</span>

          <span>·</span>

          <span>Evidence Intelligence</span>
        </div>
      </div>
    </div>
  </footer>
</template>
```

