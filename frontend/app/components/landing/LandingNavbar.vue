<script setup lang="ts">
import VeriLensLogo from "../branding/VeriLensLogo.vue"
</script>

<template>
  <header class="absolute inset-x-0 top-0 z-50">
    <div class="vl-container py-5">
      <div
        class="flex items-center justify-between rounded-2xl border border-[var(--vl-border)] bg-white/45 px-4 py-3 shadow-sm backdrop-blur-xl sm:px-5"
      >
        <!-- Brand -->
        <NuxtLink
          to="/"
          class="group flex items-center gap-3"
          aria-label="VeriLens home"
        >
          <div
            class="transition-transform duration-500 group-hover:-rotate-3 group-hover:scale-105"
          >
            <VeriLensLogo size="md" />
          </div>

          <div class="leading-none">
            <p
              class="text-[15px] font-bold tracking-[-0.03em] text-[var(--vl-ink)]"
            >
              VeriLens
            </p>

            <p
              class="mt-1 hidden text-[8px] font-semibold uppercase tracking-[0.2em] text-[var(--vl-muted)] sm:block"
            >
              Evidence Intelligence
            </p>
          </div>
        </NuxtLink>

        <!-- Desktop Navigation -->
        <nav
          class="hidden items-center gap-7 lg:flex"
          aria-label="Main navigation"
        >
          <a
            href="#intelligence"
            class="relative py-2 text-[13px] font-medium text-[var(--vl-muted)] transition-colors duration-300 hover:text-[var(--vl-ink)]"
          >
            Intelligence

            <span
              class="absolute inset-x-0 bottom-0 h-px origin-left scale-x-0 bg-[var(--vl-sage)] transition-transform duration-300 hover:scale-x-100"
            />
          </a>

          <a
            href="#evidence"
            class="relative py-2 text-[13px] font-medium text-[var(--vl-muted)] transition-colors duration-300 hover:text-[var(--vl-ink)]"
          >
            Evidence

            <span
              class="absolute inset-x-0 bottom-0 h-px origin-left scale-x-0 bg-[var(--vl-sage)] transition-transform duration-300 hover:scale-x-100"
            />
          </a>

          <a
            href="#models"
            class="relative py-2 text-[13px] font-medium text-[var(--vl-muted)] transition-colors duration-300 hover:text-[var(--vl-ink)]"
          >
            Models

            <span
              class="absolute inset-x-0 bottom-0 h-px origin-left scale-x-0 bg-[var(--vl-sage)] transition-transform duration-300 hover:scale-x-100"
            />
          </a>

          <a
            href="#workflow"
            class="relative py-2 text-[13px] font-medium text-[var(--vl-muted)] transition-colors duration-300 hover:text-[var(--vl-ink)]"
          >
            How it works

            <span
              class="absolute inset-x-0 bottom-0 h-px origin-left scale-x-0 bg-[var(--vl-sage)] transition-transform duration-300 hover:scale-x-100"
            />
          </a>
        </nav>

        <!-- Actions -->
        <div class="flex items-center gap-2">
          <!-- CTA -->
          <NuxtLink
            to="/auth/login"
            class="group inline-flex items-center gap-2 rounded-full bg-[var(--vl-ink)] px-4 py-2.5 text-[12px] font-semibold text-white shadow-[0_10px_30px_rgba(32,35,31,0.12)] transition-all duration-300 hover:-translate-y-0.5 hover:bg-[var(--vl-sage-dark)] hover:shadow-[0_14px_35px_rgba(32,35,31,0.16)] sm:px-5 sm:text-[13px]"
          >
            <span>Start analyzing</span>

            <span
              class="transition-transform duration-300 group-hover:translate-x-0.5"
              aria-hidden="true"
            >
              →
            </span>
          </NuxtLink>

          <!-- Mobile menu button -->
          <button
            type="button"
            aria-label="Open navigation menu"
            class="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--vl-border)] bg-white/50 text-[var(--vl-ink)] backdrop-blur-md lg:hidden"
          >
            <span class="flex flex-col gap-1.5">
              <span class="h-px w-4 bg-current" />
              <span class="h-px w-3 bg-current" />
            </span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
