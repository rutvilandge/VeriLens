<script setup lang="ts">
const models = [
  {
    name: "Logistic Regression",
    type: "Text",
    accuracy: "33.5%",
    f1: "26.9%",
    auc: "0.62",
    active: true,
  },
  {
    name: "Random Forest",
    type: "Text",
    accuracy: "31.9%",
    f1: "28.1%",
    auc: "0.61",
    active: false,
  },
  {
    name: "DistilBERT",
    type: "Text",
    accuracy: "29.8%",
    f1: "29.2%",
    auc: "0.60",
    active: false,
  },
  {
    name: "HOG + Logistic Regression",
    type: "Vision",
    accuracy: "72.9%",
    f1: "72.9%",
    auc: "0.80",
    active: false,
  },
]

const metrics = [
  {
    label: "Accuracy",
    value: "72.9%",
    width: "73%",
  },
  {
    label: "Macro F1",
    value: "72.9%",
    width: "73%",
  },
  {
    label: "ROC-AUC",
    value: "0.80",
    width: "80%",
  },
]
</script>

<template>
  <section
    id="model-lab"
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-28 sm:py-36"
  >
    <!-- Background atmosphere -->
    <div
      class="pointer-events-none absolute right-[5%] top-[10%] h-[30rem] w-[30rem] rounded-full bg-[var(--vl-sage)]/5 blur-[140px]"
    />

    <div
      class="pointer-events-none absolute bottom-[-10rem] left-[-8rem] h-[28rem] w-[28rem] rounded-full bg-[var(--vl-terracotta)]/5 blur-[140px]"
    />

    <div class="vl-container relative">
      <!-- Header -->
      <div class="grid gap-10 lg:grid-cols-[1fr_0.75fr] lg:items-end">
        <div>
          <p class="vl-eyebrow">
            Model lab
          </p>

          <h2
            class="mt-5 max-w-4xl text-4xl font-semibold leading-[0.98] tracking-[-0.06em] sm:text-5xl lg:text-7xl"
          >
            Don't just use a model.
            <span class="vl-gradient-text">
              understand it.
            </span>
          </h2>
        </div>

        <p
          class="max-w-xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8 lg:justify-self-end"
        >
          Compare experiments, inspect evaluation metrics, and understand
          why a model was selected before it ever reaches a prediction.
        </p>
      </div>

      <!-- Lab workspace -->
      <div
        class="mt-20 overflow-hidden rounded-[2rem] border border-[var(--vl-border)] bg-white/40 shadow-[0_35px_120px_rgba(32,35,31,0.08)] backdrop-blur-xl"
      >
        <!-- Toolbar -->
        <div
          class="flex flex-col gap-5 border-b border-[var(--vl-border)] px-6 py-6 sm:px-8 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <p
              class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
            >
              Experiment workspace
            </p>

            <p class="mt-1 text-sm font-semibold">
              Model comparison
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <span
              class="rounded-full border border-[var(--vl-border)] bg-white/50 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
            >
              LIAR2
            </span>

            <span
              class="rounded-full border border-[var(--vl-border)] bg-white/50 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
            >
              Evaluation
            </span>

            <span
              class="rounded-full bg-[var(--vl-sage)]/10 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-sage-dark)]"
            >
              Experiment complete
            </span>
          </div>
        </div>

        <div class="grid lg:grid-cols-[0.85fr_1.15fr]">
          <!-- Model list -->
          <div
            class="border-b border-[var(--vl-border)] p-6 sm:p-8 lg:border-b-0 lg:border-r"
          >
            <div
              class="flex items-center justify-between"
            >
              <div>
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                >
                  Candidates
                </p>

                <p class="mt-1 text-sm font-semibold">
                  Trained models
                </p>
              </div>

              <span
                class="text-[9px] font-semibold text-[var(--vl-muted)]"
              >
                04
              </span>
            </div>

            <div class="mt-7 space-y-3">
              <div
                v-for="model in models"
                :key="model.name"
                class="rounded-2xl border p-4 transition-all duration-300"
                :class="
                  model.active
                    ? 'border-[var(--vl-sage)]/30 bg-[var(--vl-sage)]/[0.06] shadow-[0_12px_35px_rgba(113,129,107,0.08)]'
                    : 'border-[var(--vl-border)] bg-white/30 hover:-translate-y-0.5 hover:bg-white/50'
                "
              >
                <div
                  class="flex items-start justify-between gap-4"
                >
                  <div>
                    <div class="flex items-center gap-2">
                      <span
                        class="h-1.5 w-1.5 rounded-full"
                        :class="
                          model.active
                            ? 'bg-[var(--vl-sage)]'
                            : 'bg-[var(--vl-ink)]/20'
                        "
                      />

                      <p
                        class="text-xs font-semibold"
                      >
                        {{ model.name }}
                      </p>
                    </div>

                    <p
                      class="mt-2 text-[9px] uppercase tracking-[0.14em] text-[var(--vl-muted)]"
                    >
                      {{ model.type }} model
                    </p>
                  </div>

                  <span
                    v-if="model.active"
                    class="rounded-full bg-[var(--vl-sage)]/10 px-2 py-1 text-[7px] font-bold uppercase tracking-[0.12em] text-[var(--vl-sage-dark)]"
                  >
                    Selected
                  </span>
                </div>

                <div
                  class="mt-5 grid grid-cols-3 gap-2"
                >
                  <div>
                    <p
                      class="text-[8px] uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                    >
                      Acc
                    </p>

                    <p
                      class="mt-1 text-xs font-semibold"
                    >
                      {{ model.accuracy }}
                    </p>
                  </div>

                  <div>
                    <p
                      class="text-[8px] uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                    >
                      F1
                    </p>

                    <p
                      class="mt-1 text-xs font-semibold"
                    >
                      {{ model.f1 }}
                    </p>
                  </div>

                  <div>
                    <p
                      class="text-[8px] uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                    >
                      AUC
                    </p>

                    <p
                      class="mt-1 text-xs font-semibold"
                    >
                      {{ model.auc }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Metrics -->
          <div class="p-6 sm:p-8">
            <div
              class="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between"
            >
              <div>
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                >
                  Selected experiment
                </p>

                <p
                  class="mt-1 text-lg font-semibold tracking-[-0.03em]"
                >
                  HOG + Logistic Regression
                </p>

                <p
                  class="mt-2 max-w-md text-xs leading-5 text-[var(--vl-muted)]"
                >
                  Lightweight vision baseline evaluated on the CIFAKE
                  dataset.
                </p>
              </div>

              <span
                class="self-start rounded-full bg-[var(--vl-terracotta)]/10 px-3 py-1.5 text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-terracotta)]"
              >
                Vision
              </span>
            </div>

            <!-- Metric cards -->
            <div
              class="mt-9 grid gap-3 sm:grid-cols-3"
            >
              <div
                v-for="metric in metrics"
                :key="metric.label"
                class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-bg)]/55 p-4"
              >
                <p
                  class="text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
                >
                  {{ metric.label }}
                </p>

                <p
                  class="mt-3 text-2xl font-semibold tracking-[-0.05em]"
                >
                  {{ metric.value }}
                </p>

                <div
                  class="mt-4 h-1.5 overflow-hidden rounded-full bg-[var(--vl-ink)]/6"
                >
                  <div
                    class="h-full rounded-full bg-[var(--vl-sage)]"
                    :style="{ width: metric.width }"
                  />
                </div>
              </div>
            </div>

            <!-- Confusion matrix -->
            <div class="mt-9">
              <div
                class="flex items-center justify-between"
              >
                <div>
                  <p
                    class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                  >
                    Evaluation
                  </p>

                  <p class="mt-1 text-sm font-semibold">
                    Confusion matrix
                  </p>
                </div>

                <span
                  class="text-[8px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
                >
                  Test split
                </span>
              </div>

              <div
                class="mt-5 grid max-w-md grid-cols-3 overflow-hidden rounded-2xl border border-[var(--vl-border)]"
              >
                <div />

                <div
                  class="border-b border-l border-[var(--vl-border)] bg-[var(--vl-bg)]/50 p-3 text-center text-[8px] font-bold uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                >
                  Pred. Real
                </div>

                <div
                  class="border-b border-l border-[var(--vl-border)] bg-[var(--vl-bg)]/50 p-3 text-center text-[8px] font-bold uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                >
                  Pred. Fake
                </div>

                <div
                  class="border-t border-[var(--vl-border)] bg-[var(--vl-bg)]/50 p-3 text-[8px] font-bold uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                >
                  Actual Real
                </div>

                <div
                  class="border-l border-t border-[var(--vl-border)] bg-[var(--vl-sage)]/10 p-5 text-center text-sm font-semibold"
                >
                  724
                </div>

                <div
                  class="border-l border-t border-[var(--vl-border)] bg-[var(--vl-terracotta)]/8 p-5 text-center text-sm font-semibold"
                >
                  276
                </div>

                <div
                  class="border-t border-[var(--vl-border)] bg-[var(--vl-terracotta)]/8 p-5 text-center text-sm font-semibold"
                >
                  271
                </div>

                <div
                  class="border-l border-t border-[var(--vl-border)] bg-[var(--vl-sage)]/10 p-5 text-center text-sm font-semibold"
                >
                  729
                </div>
              </div>
            </div>

            <!-- Selection rationale -->
            <div
              class="mt-8 rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-sage)]/[0.035] p-5"
            >
              <p
                class="text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-sage-dark)]"
              >
                Model selection
              </p>

              <p
                class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
              >
                The selected model provides a lightweight vision baseline
                with measurable performance and interpretable features.
                Model choice should be driven by the evaluation context,
                not accuracy alone.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Lab capabilities -->
      <div
        class="mt-12 grid gap-4 sm:grid-cols-3"
      >
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Train
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Feature engineering, preprocessing and model training.
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Evaluate
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Accuracy, precision, recall, F1, ROC-AUC and confusion matrices.
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-white/35 p-5 backdrop-blur-xl"
        >
          <p class="text-sm font-semibold">
            Compare
          </p>

          <p
            class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
          >
            Compare experiments before selecting a production candidate.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
