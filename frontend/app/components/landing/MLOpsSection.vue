<script setup lang="ts">
const monitoringStats = [
  {
    label: "Predictions",
    value: "12,482",
    detail: "+8.4% this week",
  },
  {
    label: "Avg. latency",
    value: "184 ms",
    detail: "within target",
  },
  {
    label: "High-risk rate",
    value: "18.7%",
    detail: "stable",
  },
  {
    label: "Model version",
    value: "v0.4.2",
    detail: "production",
  },
]

const distribution = [
  { label: "Very low", value: "18%", width: "18%" },
  { label: "Low", value: "27%", width: "27%" },
  { label: "Medium", value: "31%", width: "31%" },
  { label: "High", value: "17%", width: "17%" },
  { label: "Critical", value: "7%", width: "7%" },
]
</script>

<template>
  <section
    id="mlops"
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-28 sm:py-36"
  >
    <!-- Atmosphere -->
    <div
      class="pointer-events-none absolute left-1/2 top-[15%] h-[30rem] w-[30rem] -translate-x-1/2 rounded-full bg-[var(--vl-sage)]/5 blur-[140px]"
    />

    <div class="vl-container relative">
      <!-- Header -->
      <div class="grid gap-10 lg:grid-cols-[1fr_0.75fr] lg:items-end">
        <div>
          <p class="vl-eyebrow">
            MLOps & monitoring
          </p>

          <h2
            class="mt-5 max-w-4xl text-4xl font-semibold leading-[0.98] tracking-[-0.06em] sm:text-5xl lg:text-7xl"
          >
            A model is never
            <span class="vl-gradient-text">
              finished.
            </span>
          </h2>
        </div>

        <p
          class="max-w-xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8 lg:justify-self-end"
        >
          VeriLens treats models as living systems — tracking predictions,
          latency, distributions, versions, and signals that can reveal
          when behavior starts to change.
        </p>
      </div>

      <!-- Monitoring workspace -->
      <div
        class="mt-20 overflow-hidden rounded-[2rem] border border-[var(--vl-border)] bg-white/40 shadow-[0_35px_120px_rgba(32,35,31,0.08)] backdrop-blur-xl"
      >
        <!-- Header -->
        <div
          class="flex flex-col gap-5 border-b border-[var(--vl-border)] px-6 py-6 sm:px-8 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <p
              class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
            >
              Production monitor
            </p>

            <p class="mt-1 text-sm font-semibold">
              VeriLens model health
            </p>
          </div>

          <div class="flex items-center gap-3">
            <span
              class="flex items-center gap-2 rounded-full bg-[var(--vl-sage)]/10 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-sage-dark)]"
            >
              <span
                class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)]"
              />

              Monitoring active
            </span>

            <span
              class="hidden text-[8px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)] sm:block"
            >
              Last 7 days
            </span>
          </div>
        </div>

        <!-- Stats -->
        <div
          class="grid border-b border-[var(--vl-border)] sm:grid-cols-2 lg:grid-cols-4"
        >
          <div
            v-for="(stat, index) in monitoringStats"
            :key="stat.label"
            class="p-6 sm:p-7"
            :class="
              index !== monitoringStats.length - 1
                ? 'border-b border-[var(--vl-border)] sm:border-r'
                : ''
            "
          >
            <p
              class="text-[8px] font-bold uppercase tracking-[0.16em] text-[var(--vl-muted)]"
            >
              {{ stat.label }}
            </p>

            <p
              class="mt-3 text-2xl font-semibold tracking-[-0.05em]"
            >
              {{ stat.value }}
            </p>

            <p
              class="mt-2 text-[9px] font-medium text-[var(--vl-sage-dark)]"
            >
              {{ stat.detail }}
            </p>
          </div>
        </div>

        <!-- Monitoring panels -->
        <div class="grid lg:grid-cols-[1.15fr_0.85fr]">
          <!-- Prediction distribution -->
          <div
            class="border-b border-[var(--vl-border)] p-6 sm:p-8 lg:border-b-0 lg:border-r"
          >
            <div
              class="flex items-start justify-between gap-5"
            >
              <div>
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                >
                  Prediction distribution
                </p>

                <p class="mt-1 text-sm font-semibold">
                  Risk scores across recent predictions
                </p>
              </div>

              <span
                class="rounded-full border border-[var(--vl-border)] bg-white/50 px-2.5 py-1 text-[7px] font-bold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
              >
                Live
              </span>
            </div>

            <div class="mt-10 space-y-5">
              <div
                v-for="item in distribution"
                :key="item.label"
              >
                <div
                  class="flex items-center justify-between"
                >
                  <span
                    class="text-xs font-medium"
                  >
                    {{ item.label }}
                  </span>

                  <span
                    class="text-[9px] font-semibold text-[var(--vl-muted)]"
                  >
                    {{ item.value }}
                  </span>
                </div>

                <div
                  class="mt-2 h-2 overflow-hidden rounded-full bg-[var(--vl-ink)]/6"
                >
                  <div
                    class="h-full rounded-full bg-[var(--vl-sage)] transition-all duration-700"
                    :style="{ width: item.width }"
                  />
                </div>
              </div>
            </div>

            <!-- Trend visualization -->
            <div class="mt-10">
              <div
                class="flex items-center justify-between"
              >
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-muted)]"
                >
                  Confidence trend
                </p>

                <span
                  class="text-[8px] font-semibold text-[var(--vl-sage-dark)]"
                >
                  Stable
                </span>
              </div>

              <div
                class="relative mt-4 h-28 overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-bg)]/45"
              >
                <div
                  class="absolute inset-x-0 top-1/2 border-t border-dashed border-[var(--vl-ink)]/10"
                />

                <svg
                  class="absolute inset-0 h-full w-full"
                  viewBox="0 0 600 120"
                  preserveAspectRatio="none"
                >
                  <path
                    d="M0 82 C40 76 62 88 95 70 C125 54 155 65 190 59 C225 53 244 72 278 64 C315 54 338 42 370 48 C405 54 426 39 458 44 C490 48 520 30 552 35 C570 38 585 26 600 28"
                    fill="none"
                    stroke="rgba(113,129,107,0.7)"
                    stroke-width="2"
                  />

                  <path
                    d="M0 82 C40 76 62 88 95 70 C125 54 155 65 190 59 C225 53 244 72 278 64 C315 54 338 42 370 48 C405 54 426 39 458 44 C490 48 520 30 552 35 C570 38 585 26 600 28 L600 120 L0 120 Z"
                    fill="rgba(113,129,107,0.05)"
                  />
                </svg>
              </div>
            </div>
          </div>

          <!-- Health panel -->
          <div class="p-6 sm:p-8">
            <div>
              <p
                class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
              >
                System health
              </p>

              <p class="mt-1 text-sm font-semibold">
                Signals worth watching
              </p>
            </div>

            <div class="mt-8 space-y-3">
              <div
                class="flex items-center justify-between rounded-2xl border border-[var(--vl-border)] bg-white/35 p-4"
              >
                <div class="flex items-center gap-3">
                  <span
                    class="h-2 w-2 rounded-full bg-[var(--vl-sage)]"
                  />

                  <div>
                    <p class="text-xs font-semibold">
                      Prediction latency
                    </p>

                    <p
                      class="mt-1 text-[9px] text-[var(--vl-muted)]"
                    >
                      184 ms average
                    </p>
                  </div>
                </div>

                <span
                  class="text-[8px] font-bold uppercase tracking-[0.12em] text-[var(--vl-sage-dark)]"
                >
                  Healthy
                </span>
              </div>

              <div
                class="flex items-center justify-between rounded-2xl border border-[var(--vl-border)] bg-white/35 p-4"
              >
                <div class="flex items-center gap-3">
                  <span
                    class="h-2 w-2 rounded-full bg-[var(--vl-sage)]"
                  />

                  <div>
                    <p class="text-xs font-semibold">
                      Input distribution
                    </p>

                    <p
                      class="mt-1 text-[9px] text-[var(--vl-muted)]"
                    >
                      No significant drift
                    </p>
                  </div>
                </div>

                <span
                  class="text-[8px] font-bold uppercase tracking-[0.12em] text-[var(--vl-sage-dark)]"
                >
                  Stable
                </span>
              </div>

              <div
                class="flex items-center justify-between rounded-2xl border border-[var(--vl-terracotta)]/20 bg-[var(--vl-terracotta)]/[0.035] p-4"
              >
                <div class="flex items-center gap-3">
                  <span
                    class="h-2 w-2 rounded-full bg-[var(--vl-terracotta)]"
                  />

                  <div>
                    <p class="text-xs font-semibold">
                      High-risk predictions
                    </p>

                    <p
                      class="mt-1 text-[9px] text-[var(--vl-muted)]"
                    >
                      18.7% of recent traffic
                    </p>
                  </div>
                </div>

                <span
                  class="text-[8px] font-bold uppercase tracking-[0.12em] text-[var(--vl-terracotta)]"
                >
                  Watch
                </span>
              </div>
            </div>

            <!-- Version -->
            <div
              class="mt-8 rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-sage)]/[0.035] p-5"
            >
              <div
                class="flex items-center justify-between"
              >
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-sage-dark)]"
                >
                  Model version
                </p>

                <span
                  class="rounded-full bg-[var(--vl-sage)]/10 px-2.5 py-1 text-[7px] font-bold uppercase tracking-[0.12em] text-[var(--vl-sage-dark)]"
                >
                  Production
                </span>
              </div>

              <p
                class="mt-3 text-xl font-semibold tracking-[-0.04em]"
              >
                vl-multimodal-v0.4.2
              </p>

              <div
                class="mt-4 flex items-center gap-2 text-[9px] text-[var(--vl-muted)]"
              >
                <span>
                  Dataset v0.4
                </span>

                <span>·</span>

                <span>
                  Evaluation tracked
                </span>

                <span>·</span>

                <span>
                  Logged
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom principles -->
      <div
        class="mt-12 grid gap-4 sm:grid-cols-3"
      >
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Versioned
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Keep datasets, models and experiments traceable.
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Observable
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Monitor latency, confidence and prediction behavior.
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Auditable
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Preserve the trail from model version to prediction.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
