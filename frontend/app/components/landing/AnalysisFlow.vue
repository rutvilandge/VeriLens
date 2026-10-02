<script setup lang="ts">
const steps = [
  {
    number: "01",
    eyebrow: "INPUT",
    title: "Bring the content.",
    description:
      "Text, images, claims, and source material enter one unified analysis pipeline.",
    tag: "Text + Vision + Sources",
    accent: "sage",
  },
  {
    number: "02",
    eyebrow: "ANALYZE",
    title: "Read every signal.",
    description:
      "Language, visual patterns, metadata, and semantic relationships are analyzed together.",
    tag: "Multimodal Intelligence",
    accent: "terracotta",
  },
  {
    number: "03",
    eyebrow: "VERIFY",
    title: "Find the evidence.",
    description:
      "Claims are connected to supporting, contradicting, and contextual evidence.",
    tag: "Evidence Retrieval",
    accent: "sage-dark",
  },
  {
    number: "04",
    eyebrow: "UNDERSTAND",
    title: "See why it matters.",
    description:
      "Models, confidence, sources, explanations, and relationships become one interpretable result.",
    tag: "Explainable Verdict",
    accent: "ink",
  },
]
</script>

<template>
  <section
    id="workflow"
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-28 sm:py-36"
  >
    <!-- Ambient atmosphere -->
    <div
      class="pointer-events-none absolute left-[-12rem] top-[20%] h-[32rem] w-[32rem] rounded-full bg-[var(--vl-sage)]/6 blur-[120px]"
    />

    <div
      class="pointer-events-none absolute right-[-10rem] bottom-[5%] h-[28rem] w-[28rem] rounded-full bg-[var(--vl-terracotta)]/5 blur-[120px]"
    />

    <div class="vl-container relative">
      <!-- Section intro -->
      <div class="grid gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:items-end">
        <div>
          <p class="vl-eyebrow">
            How VeriLens thinks
          </p>

          <h2
            class="mt-5 max-w-xl text-4xl font-semibold leading-[1] tracking-[-0.055em] sm:text-5xl lg:text-6xl"
          >
            From raw content
            <span class="vl-gradient-text">
              to understanding.
            </span>
          </h2>
        </div>

        <div class="max-w-xl lg:justify-self-end">
          <p
            class="text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8"
          >
            VeriLens does not stop at a prediction. It follows the signal
            through models, sources, evidence, and relationships until the
            result becomes understandable.
          </p>
        </div>
      </div>

      <!-- Flow visualization -->
      <div class="relative mt-20">
        <!-- Connecting line -->
        <div
          class="pointer-events-none absolute left-0 right-0 top-[5.75rem] hidden h-px bg-gradient-to-r from-transparent via-[var(--vl-ink)]/10 to-transparent lg:block"
        />

        <div
          class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4"
        >
          <article
            v-for="step in steps"
            :key="step.number"
            class="group relative"
          >
            <!-- Step number -->
            <div class="relative z-10 mb-8 flex items-center justify-between">
              <div
                class="flex h-12 w-12 items-center justify-center rounded-full border border-[var(--vl-border)] bg-[rgba(250,248,242,0.8)] text-xs font-bold tracking-[0.12em] text-[var(--vl-ink)] shadow-sm backdrop-blur-xl transition-all duration-500 group-hover:-translate-y-1 group-hover:shadow-lg"
              >
                {{ step.number }}
              </div>

              <span
                class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
              >
                {{ step.eyebrow }}
              </span>
            </div>

            <!-- Main card -->
            <div
              class="relative min-h-[285px] overflow-hidden rounded-[1.75rem] border border-[var(--vl-border)] bg-white/45 p-6 shadow-[0_24px_70px_rgba(32,35,31,0.06)] backdrop-blur-xl transition-all duration-500 group-hover:-translate-y-2 group-hover:bg-white/60 group-hover:shadow-[0_30px_80px_rgba(32,35,31,0.1)]"
            >
              <!-- Decorative number -->
              <span
                class="pointer-events-none absolute -right-3 -top-7 select-none text-[7rem] font-semibold leading-none tracking-[-0.08em] text-[var(--vl-ink)]/[0.035]"
              >
                {{ step.number }}
              </span>

              <!-- Signal visualization -->
              <div class="relative mb-10 h-16">
                <div
                  class="absolute left-0 top-1/2 h-px w-full -translate-y-1/2 bg-[var(--vl-ink)]/8"
                />

                <div
                  class="absolute left-[12%] top-1/2 h-2 w-2 -translate-y-1/2 rounded-full"
                  :class="{
                    'bg-[var(--vl-sage)] shadow-[0_0_16px_rgba(113,129,107,0.5)]':
                      step.accent === 'sage',
                    'bg-[var(--vl-terracotta)] shadow-[0_0_16px_rgba(184,111,82,0.45)]':
                      step.accent === 'terracotta',
                    'bg-[var(--vl-sage-dark)] shadow-[0_0_16px_rgba(77,93,74,0.45)]':
                      step.accent === 'sage-dark',
                    'bg-[var(--vl-ink)] shadow-[0_0_14px_rgba(32,35,31,0.3)]':
                      step.accent === 'ink',
                  }"
                />

                <div
                  class="absolute left-[48%] top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-border)] bg-[var(--vl-bg)] transition-transform duration-500 group-hover:scale-125"
                />

                <div
                  class="absolute right-[12%] top-1/2 h-2 w-2 -translate-y-1/2 rounded-full"
                  :class="{
                    'bg-[var(--vl-sage)]':
                      step.accent === 'sage',
                    'bg-[var(--vl-terracotta)]':
                      step.accent === 'terracotta',
                    'bg-[var(--vl-sage-dark)]':
                      step.accent === 'sage-dark',
                    'bg-[var(--vl-ink)]':
                      step.accent === 'ink',
                  }"
                />

                <!-- Vertical signal -->
                <div
                  class="absolute left-[48%] top-1/2 h-9 w-px -translate-x-1/2 -translate-y-1/2 bg-[var(--vl-ink)]/10 transition-all duration-500 group-hover:h-12"
                />
              </div>

              <p
                class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
              >
                {{ step.tag }}
              </p>

              <h3
                class="mt-3 text-xl font-semibold tracking-[-0.035em] text-[var(--vl-ink)]"
              >
                {{ step.title }}
              </h3>

              <p
                class="mt-3 text-sm leading-6 text-[var(--vl-muted)]"
              >
                {{ step.description }}
              </p>

              <!-- Bottom accent -->
              <div
                class="absolute bottom-0 left-6 right-6 h-px origin-left scale-x-0 transition-transform duration-500 group-hover:scale-x-100"
                :class="{
                  'bg-[var(--vl-sage)]': step.accent === 'sage',
                  'bg-[var(--vl-terracotta)]': step.accent === 'terracotta',
                  'bg-[var(--vl-sage-dark)]': step.accent === 'sage-dark',
                  'bg-[var(--vl-ink)]': step.accent === 'ink',
                }"
              />
            </div>

            <!-- Arrow between cards -->
            <div
              v-if="step.number !== '04'"
              class="absolute -right-4 top-[5.5rem] z-20 hidden h-8 w-8 items-center justify-center rounded-full border border-[var(--vl-border)] bg-[var(--vl-bg)] text-xs text-[var(--vl-muted)] lg:flex"
            >
              →
            </div>
          </article>
        </div>
      </div>

      <!-- Closing statement -->
      <div
        class="mt-16 flex flex-col gap-5 border-t border-[var(--vl-border)] pt-8 sm:flex-row sm:items-center sm:justify-between"
      >
        <p class="max-w-2xl text-sm leading-6 text-[var(--vl-muted)]">
          Every stage leaves a trace — so the final result is not just a
          label, but an explanation you can inspect.
        </p>

        <div
          class="inline-flex shrink-0 items-center gap-2 text-xs font-semibold text-[var(--vl-sage-dark)]"
        >
          <span
            class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)]"
          />
          Traceable by design
        </div>
      </div>
    </div>
  </section>
</template>
