<script setup lang="ts">
const features = [
  {
    name: "Claim language",
    value: "0.82",
    width: "82%",
    accent: "sage",
  },
  {
    name: "Source consistency",
    value: "0.74",
    width: "74%",
    accent: "sage",
  },
  {
    name: "Visual signal",
    value: "0.61",
    width: "61%",
    accent: "terracotta",
  },
  {
    name: "Temporal mismatch",
    value: "0.43",
    width: "43%",
    accent: "terracotta",
  },
  {
    name: "Cross-modal alignment",
    value: "0.31",
    width: "31%",
    accent: "ink",
  },
]
</script>

<template>
  <section
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-28 sm:py-36"
  >
    <!-- Atmosphere -->
    <div
      class="pointer-events-none absolute left-[10%] top-[20%] h-[28rem] w-[28rem] rounded-full bg-[var(--vl-sage)]/5 blur-[130px]"
    />

    <div
      class="pointer-events-none absolute right-[-10rem] bottom-[5%] h-[30rem] w-[30rem] rounded-full bg-[var(--vl-terracotta)]/5 blur-[130px]"
    />

    <div class="vl-container relative">
      <!-- Header -->
      <div class="grid gap-10 lg:grid-cols-[1fr_0.75fr] lg:items-end">
        <div>
          <p class="vl-eyebrow">
            Explainable intelligence
          </p>

          <h2
            class="mt-5 max-w-3xl text-4xl font-semibold leading-[0.98] tracking-[-0.06em] sm:text-5xl lg:text-7xl"
          >
            Every prediction
            <span class="vl-gradient-text">
              has a reason.
            </span>
          </h2>
        </div>

        <p
          class="max-w-xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8 lg:justify-self-end"
        >
          VeriLens exposes the signals behind a model's decision — from
          important features to supporting evidence — so confidence never
          has to mean blind trust.
        </p>
      </div>

      <!-- Explainability workspace -->
      <div
        class="mt-20 overflow-hidden rounded-[2rem] border border-[var(--vl-border)] bg-white/40 shadow-[0_35px_110px_rgba(32,35,31,0.08)] backdrop-blur-xl"
      >
        <!-- Top bar -->
        <div
          class="flex flex-col gap-5 border-b border-[var(--vl-border)] px-6 py-6 sm:px-8 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <p
              class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
            >
              Model explanation
            </p>

            <p class="mt-1 text-sm font-semibold">
              Why this content received its prediction
            </p>
          </div>

          <div
            class="flex items-center gap-3 self-start"
          >
            <span
              class="rounded-full bg-[var(--vl-terracotta)]/10 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-terracotta)]"
            >
              High risk
            </span>

            <span
              class="text-xs font-semibold text-[var(--vl-ink)]"
            >
              78.4%
            </span>
          </div>
        </div>

        <div
          class="grid lg:grid-cols-[0.9fr_1.1fr]"
        >
          <!-- Prediction -->
          <div
            class="border-b border-[var(--vl-border)] p-7 sm:p-9 lg:border-b-0 lg:border-r"
          >
            <p
              class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
            >
              Model confidence
            </p>

            <!-- Gauge -->
            <div
              class="relative mx-auto mt-10 flex h-56 w-56 items-center justify-center rounded-full border border-[var(--vl-border)] bg-[var(--vl-bg)]/60"
            >
              <div
                class="absolute inset-4 rounded-full border border-[var(--vl-sage)]/10"
              />

              <div
                class="absolute inset-9 rounded-full border border-[var(--vl-terracotta)]/10"
              />

              <div
                class="absolute inset-[4.2rem] rounded-full bg-white/70 shadow-inner"
              />

              <div class="relative text-center">
                <p
                  class="text-4xl font-semibold tracking-[-0.06em]"
                >
                  78.4%
                </p>

                <p
                  class="mt-2 text-[8px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                >
                  AI-generated probability
                </p>
              </div>
            </div>

            <div
              class="mt-9 rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-bg)]/55 p-5"
            >
              <div
                class="flex items-center justify-between"
              >
                <span
                  class="text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-muted)]"
                >
                  Prediction
                </span>

                <span
                  class="text-[9px] font-semibold text-[var(--vl-terracotta)]"
                >
                  REVIEW
                </span>
              </div>

              <p
                class="mt-3 text-lg font-semibold tracking-[-0.03em]"
              >
                Requires further verification
              </p>

              <p
                class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
              >
                Evidence and model signals indicate elevated uncertainty.
              </p>
            </div>
          </div>

          <!-- Feature importance -->
          <div class="p-7 sm:p-9">
            <div
              class="flex items-center justify-between"
            >
              <div>
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
                >
                  Feature contribution
                </p>

                <p class="mt-1 text-sm font-semibold">
                  Signals influencing the prediction
                </p>
              </div>

              <span
                class="hidden text-[8px] font-bold uppercase tracking-[0.15em] text-[var(--vl-muted)] sm:block"
              >
                SHAP / importance
              </span>
            </div>

            <div class="mt-10 space-y-7">
              <div
                v-for="feature in features"
                :key="feature.name"
              >
                <div
                  class="flex items-center justify-between gap-4"
                >
                  <span
                    class="text-xs font-medium"
                  >
                    {{ feature.name }}
                  </span>

                  <span
                    class="text-[10px] font-semibold text-[var(--vl-muted)]"
                  >
                    {{ feature.value }}
                  </span>
                </div>

                <div
                  class="mt-3 h-2 overflow-hidden rounded-full bg-[var(--vl-ink)]/6"
                >
                  <div
                    class="h-full rounded-full transition-transform duration-700 hover:scale-x-105"
                    :class="{
                      'bg-[var(--vl-sage)]':
                        feature.accent === 'sage',
                      'bg-[var(--vl-terracotta)]':
                        feature.accent === 'terracotta',
                      'bg-[var(--vl-ink)]/40':
                        feature.accent === 'ink',
                    }"
                    :style="{
                      width: feature.width,
                    }"
                  />
                </div>
              </div>
            </div>

            <!-- Explanation -->
            <div
              class="mt-10 rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-sage)]/[0.035] p-5"
            >
              <div class="flex gap-3">
                <span
                  class="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--vl-sage)]/10 text-[9px] font-bold text-[var(--vl-sage-dark)]"
                >
                  AI
                </span>

                <div>
                  <p
                    class="text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-sage-dark)]"
                  >
                    Explanation
                  </p>

                  <p
                    class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
                  >
                    The prediction is primarily influenced by claim
                    language and source consistency, while visual and
                    temporal signals increase the overall risk.
                  </p>
                </div>
              </div>
            </div>

            <!-- Method chips -->
            <div
              class="mt-6 flex flex-wrap gap-2"
            >
              <span
                class="rounded-full border border-[var(--vl-border)] bg-white/50 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
              >
                SHAP
              </span>

              <span
                class="rounded-full border border-[var(--vl-border)] bg-white/50 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
              >
                Feature importance
              </span>

              <span
                class="rounded-full border border-[var(--vl-border)] bg-white/50 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
              >
                Confidence
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Principles -->
      <div
        class="mt-12 grid gap-4 sm:grid-cols-3"
      >
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Transparent
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            See which signals influenced the model.
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Inspectable
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Move from prediction back to evidence.
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Human-readable
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Turn technical model signals into understandable reasoning.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
