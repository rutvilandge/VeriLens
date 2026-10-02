<script setup lang="ts">
import VeriLensLogo from "../branding/VeriLensLogo.vue"
</script>

<template>
  <section
    id="start"
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-28 sm:py-36"
  >
    <!-- Cinematic atmosphere -->
    <div
      class="pointer-events-none absolute left-1/2 top-1/2 h-[38rem] w-[38rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--vl-sage)]/7 blur-[150px]"
    />

    <div
      class="pointer-events-none absolute left-[12%] top-[30%] h-32 w-32 rounded-full bg-[var(--vl-terracotta)]/6 blur-[70px]"
    />

    <div class="vl-container relative">
      <div
        class="relative overflow-hidden rounded-[2.5rem] border border-[var(--vl-border)] bg-[rgba(250,248,242,0.58)] px-6 py-20 text-center shadow-[0_40px_130px_rgba(32,35,31,0.09)] backdrop-blur-2xl sm:px-10 sm:py-28"
      >
        <!-- Editorial grid -->
        <div
          class="pointer-events-none absolute inset-0 opacity-[0.035]"
          style="
            background-image:
              linear-gradient(var(--vl-ink) 1px, transparent 1px),
              linear-gradient(90deg, var(--vl-ink) 1px, transparent 1px);
            background-size: 56px 56px;
          "
        />

        <!-- Decorative orbit -->
        <div
          class="pointer-events-none absolute left-1/2 top-1/2 h-[25rem] w-[25rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-sage)]/10"
        />

        <div
          class="pointer-events-none absolute left-1/2 top-1/2 h-[18rem] w-[18rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-ink)]/7"
        />

        <!-- Floating signals -->
        <span
          class="pointer-events-none absolute left-[12%] top-[24%] h-2 w-2 rounded-full bg-[var(--vl-sage)] shadow-[0_0_20px_rgba(113,129,107,0.55)]"
        />

        <span
          class="pointer-events-none absolute right-[16%] top-[30%] h-1.5 w-1.5 rounded-full bg-[var(--vl-terracotta)] shadow-[0_0_18px_rgba(184,111,82,0.5)]"
        />

        <span
          class="pointer-events-none absolute bottom-[25%] left-[20%] h-1.5 w-1.5 rounded-full bg-[var(--vl-ink)]/30"
        />

        <span
          class="pointer-events-none absolute bottom-[20%] right-[22%] h-2 w-2 rounded-full bg-[var(--vl-sage)]/70"
        />

        <!-- Content -->
        <div class="relative z-10 mx-auto max-w-3xl">
          <div class="flex justify-center">
            <div
              class="rounded-full border border-[var(--vl-border)] bg-white/55 p-3 shadow-[0_15px_40px_rgba(32,35,31,0.07)] backdrop-blur-xl"
            >
              <VeriLensLogo size="lg" />
            </div>
          </div>

          <p class="mt-8 vl-eyebrow">
            Start with the evidence
          </p>

          <h2
            class="mt-5 text-4xl font-semibold leading-[0.98] tracking-[-0.065em] sm:text-6xl lg:text-7xl"
          >
            Don't just ask
            <span class="vl-gradient-text">
              if it's true.
            </span>
          </h2>

          <p
            class="mx-auto mt-7 max-w-2xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8"
          >
            Understand the content, inspect the signals, trace the evidence,
            and see why the model reached its conclusion.
          </p>

          <!-- CTA buttons -->
          <div
            class="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <!-- Start analyzing → Login -->
            <NuxtLink
              to="/auth/login"
              class="group inline-flex items-center justify-center gap-3 rounded-full bg-[var(--vl-ink)] px-7 py-3.5 text-sm font-semibold text-white shadow-[0_18px_45px_rgba(32,35,31,0.15)] transition-all duration-300 hover:-translate-y-1 hover:bg-[var(--vl-sage-dark)] hover:shadow-[0_22px_55px_rgba(32,35,31,0.2)]"
            >
              <span>Start analyzing</span>

              <span
                class="transition-transform duration-300 group-hover:translate-x-1"
                aria-hidden="true"
              >
                →
              </span>
            </NuxtLink>

            <!-- See how it works → Workflow -->
            <a
              href="#workflow"
              class="inline-flex items-center justify-center rounded-full border border-[var(--vl-border)] bg-white/50 px-7 py-3.5 text-sm font-semibold text-[var(--vl-ink)] backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:bg-white/75"
            >
              See how it works
            </a>
          </div>

          <!-- Product principles -->
          <div
            class="mx-auto mt-12 flex max-w-xl flex-wrap items-center justify-center gap-x-5 gap-y-3 text-[9px] font-bold uppercase tracking-[0.15em] text-[var(--vl-muted)]"
          >
            <span>Multimodal AI</span>

            <span class="text-[var(--vl-border)]">·</span>

            <span>Evidence Graph</span>

            <span class="text-[var(--vl-border)]">·</span>

            <span>Explainable ML</span>

            <span class="text-[var(--vl-border)]">·</span>

            <span>Model Monitoring</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
