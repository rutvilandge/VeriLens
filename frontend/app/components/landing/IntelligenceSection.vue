<script setup lang="ts">
const intelligence = [
  {
    index: "01",
    label: "LANGUAGE",
    title: "Read the claim.",
    description:
      "Extract claims, entities, numbers, temporal signals, and linguistic patterns from the content.",
    metric: "NLP",
    detail: "Claim extraction · TF-IDF · Transformers",
    accent: "sage",
  },
  {
    index: "02",
    label: "VISION",
    title: "Inspect the image.",
    description:
      "Visual features reveal patterns that text alone cannot see — from image structure to authenticity signals.",
    metric: "VISION",
    detail: "CNN · HOG · Vision models",
    accent: "terracotta",
  },
  {
    index: "03",
    label: "MULTIMODAL",
    title: "Connect the signals.",
    description:
      "Text and visual representations are compared to surface semantic consistency and contradictions.",
    metric: "FUSION",
    detail: "Embeddings · Similarity · Cross-modal signals",
    accent: "sage-dark",
  },
  {
    index: "04",
    label: "PREDICTION",
    title: "Measure uncertainty.",
    description:
      "Multiple model signals become interpretable predictions with confidence rather than unexplained labels.",
    metric: "ML",
    detail: "LR · Random Forest · XGBoost · Explainability",
    accent: "ink",
  },
]
</script>

<template>
  <section
    id="intelligence"
    class="relative overflow-hidden py-28 sm:py-36"
  >
    <!-- Atmosphere -->
    <div
      class="pointer-events-none absolute left-[30%] top-[8%] h-[30rem] w-[30rem] rounded-full bg-[var(--vl-sage)]/5 blur-[130px]"
    />

    <div
      class="pointer-events-none absolute right-[-8rem] top-[45%] h-[25rem] w-[25rem] rounded-full bg-[var(--vl-terracotta)]/5 blur-[120px]"
    />

    <div class="vl-container relative">
      <!-- Header -->
      <div class="max-w-3xl">
        <div
          class="inline-flex items-center gap-3"
        >
          <span
            class="h-px w-8 bg-[var(--vl-sage)]"
          />

          <p class="vl-eyebrow">
            Intelligence layers
          </p>
        </div>

        <h2
          class="mt-6 text-4xl font-semibold leading-[0.98] tracking-[-0.06em] sm:text-5xl lg:text-7xl"
        >
          One piece of content.
          <br />
          <span class="vl-gradient-text">
            Multiple ways to understand it.
          </span>
        </h2>

        <p
          class="mt-7 max-w-2xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8"
        >
          VeriLens combines language, vision, multimodal signals, and
          machine learning into one analysis system — so no single model
          has to tell the whole story.
        </p>
      </div>

      <!-- Intelligence visual -->
      <div
        class="relative mt-20 overflow-hidden rounded-[2rem] border border-[var(--vl-border)] bg-white/35 p-5 shadow-[0_30px_100px_rgba(32,35,31,0.07)] backdrop-blur-xl sm:p-8 lg:p-10"
      >
        <!-- Top metadata -->
        <div
          class="flex flex-col gap-4 border-b border-[var(--vl-border)] pb-7 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <p
              class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
            >
              VeriLens intelligence engine
            </p>

            <p
              class="mt-2 text-sm font-semibold tracking-[-0.02em]"
            >
              Signals are analyzed independently before they converge.
            </p>
          </div>

          <div
            class="inline-flex items-center gap-2 self-start rounded-full border border-[var(--vl-border)] bg-white/50 px-3 py-2 text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-sage-dark)]"
          >
            <span
              class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)] shadow-[0_0_12px_rgba(113,129,107,0.5)]"
            />

            Analysis active
          </div>
        </div>

        <!-- Main system -->
        <div
          class="relative mt-10 grid gap-10 lg:grid-cols-[1fr_180px_1fr]"
        >
          <!-- Left layers -->
          <div class="space-y-4">
            <article
              v-for="item in intelligence.slice(0, 2)"
              :key="item.index"
              class="group relative overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-bg)]/60 p-5 transition-all duration-500 hover:-translate-y-1 hover:bg-white/70 hover:shadow-xl"
            >
              <div class="flex items-start justify-between gap-5">
                <div class="flex items-center gap-4">
                  <div
                    class="flex h-10 w-10 items-center justify-center rounded-xl text-[10px] font-bold"
                    :class="{
                      'bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]':
                        item.accent === 'sage',
                      'bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]':
                        item.accent === 'terracotta',
                    }"
                  >
                    {{ item.metric }}
                  </div>

                  <div>
                    <p
                      class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                    >
                      {{ item.label }}
                    </p>

                    <h3
                      class="mt-1 text-base font-semibold tracking-[-0.025em]"
                    >
                      {{ item.title }}
                    </h3>
                  </div>
                </div>

                <span
                  class="text-[10px] font-bold tracking-[0.15em] text-[var(--vl-muted)]"
                >
                  {{ item.index }}
                </span>
              </div>

              <p
                class="mt-5 text-sm leading-6 text-[var(--vl-muted)]"
              >
                {{ item.description }}
              </p>

              <div
                class="mt-5 flex items-center gap-2 text-[9px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
              >
                <span
                  class="h-1 w-1 rounded-full"
                  :class="{
                    'bg-[var(--vl-sage)]': item.accent === 'sage',
                    'bg-[var(--vl-terracotta)]':
                      item.accent === 'terracotta',
                  }"
                />

                {{ item.detail }}
              </div>
            </article>
          </div>

          <!-- Central engine -->
          <div
            class="relative flex min-h-[250px] items-center justify-center"
          >
            <!-- Horizontal signal lines -->
            <div
              class="absolute left-0 right-0 top-1/2 h-px bg-[var(--vl-ink)]/8"
            />

            <div
              class="absolute left-1/2 top-1/2 h-[175px] w-[175px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-sage)]/15"
            />

            <div
              class="absolute left-1/2 top-1/2 h-[125px] w-[125px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-ink)]/10"
            />

            <div
              class="relative z-10 flex h-24 w-24 items-center justify-center rounded-full border border-white/10 bg-[var(--vl-ink)] shadow-[0_20px_60px_rgba(32,35,31,0.18)]"
            >
              <div
                class="absolute inset-3 rounded-full border border-[var(--vl-sage)]/25"
              />

              <div
                class="h-6 w-6 rounded-full border border-[var(--vl-sage)]/50 bg-[var(--vl-sage)]/20"
              />

              <span
                class="absolute h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)] shadow-[0_0_18px_rgba(113,129,107,0.9)]"
              />
            </div>

            <div
              class="absolute bottom-3 left-1/2 z-20 -translate-x-1/2 whitespace-nowrap rounded-full border border-[var(--vl-border)] bg-[rgba(250,248,242,0.82)] px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.16em] text-[var(--vl-muted)] backdrop-blur-xl"
            >
              Fusion engine
            </div>
          </div>

          <!-- Right layers -->
          <div class="space-y-4">
            <article
              v-for="item in intelligence.slice(2)"
              :key="item.index"
              class="group relative overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-bg)]/60 p-5 transition-all duration-500 hover:-translate-y-1 hover:bg-white/70 hover:shadow-xl"
            >
              <div class="flex items-start justify-between gap-5">
                <div class="flex items-center gap-4">
                  <div
                    class="flex h-10 w-10 items-center justify-center rounded-xl text-[10px] font-bold"
                    :class="{
                      'bg-[var(--vl-sage-dark)]/10 text-[var(--vl-sage-dark)]':
                        item.accent === 'sage-dark',
                      'bg-[var(--vl-ink)]/7 text-[var(--vl-ink)]':
                        item.accent === 'ink',
                    }"
                  >
                    {{ item.metric }}
                  </div>

                  <div>
                    <p
                      class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                    >
                      {{ item.label }}
                    </p>

                    <h3
                      class="mt-1 text-base font-semibold tracking-[-0.025em]"
                    >
                      {{ item.title }}
                    </h3>
                  </div>
                </div>

                <span
                  class="text-[10px] font-bold tracking-[0.15em] text-[var(--vl-muted)]"
                >
                  {{ item.index }}
                </span>
              </div>

              <p
                class="mt-5 text-sm leading-6 text-[var(--vl-muted)]"
              >
                {{ item.description }}
              </p>

              <div
                class="mt-5 flex items-center gap-2 text-[9px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
              >
                <span
                  class="h-1 w-1 rounded-full"
                  :class="{
                    'bg-[var(--vl-sage-dark)]':
                      item.accent === 'sage-dark',
                    'bg-[var(--vl-ink)]': item.accent === 'ink',
                  }"
                />

                {{ item.detail }}
              </div>
            </article>
          </div>
        </div>

        <!-- Bottom signal strip -->
        <div
          class="mt-10 grid gap-3 border-t border-[var(--vl-border)] pt-7 sm:grid-cols-3"
        >
          <div
            class="rounded-xl bg-[var(--vl-ink)]/[0.035] px-4 py-3"
          >
            <p
              class="text-[8px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
            >
              Signal
            </p>

            <p class="mt-1 text-xs font-semibold">
              Linguistic evidence
            </p>
          </div>

          <div
            class="rounded-xl bg-[var(--vl-ink)]/[0.035] px-4 py-3"
          >
            <p
              class="text-[8px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
            >
              Signal
            </p>

            <p class="mt-1 text-xs font-semibold">
              Visual evidence
            </p>
          </div>

          <div
            class="rounded-xl bg-[var(--vl-sage)]/7 px-4 py-3"
          >
            <p
              class="text-[8px] font-bold uppercase tracking-[0.18em] text-[var(--vl-sage-dark)]"
            >
              Output
            </p>

            <p class="mt-1 text-xs font-semibold">
              Interpretable confidence
            </p>
          </div>
        </div>
      </div>

      <!-- Closing statement -->
      <div
        class="mt-12 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <p
          class="max-w-2xl text-sm leading-6 text-[var(--vl-muted)]"
        >
          Different models see different things. VeriLens brings those
          perspectives together instead of hiding them behind one score.
        </p>

        <span
          class="text-xs font-semibold text-[var(--vl-sage-dark)]"
        >
          Multiple signals → one understanding
        </span>
      </div>
    </div>
  </section>
</template>
