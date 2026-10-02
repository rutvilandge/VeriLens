<script setup lang="ts">
const nodes = [
  {
    id: "claim",
    label: "CLAIM",
    title: "Unemployment fell in 2024",
    x: "50%",
    y: "50%",
    type: "claim",
  },
  {
    id: "support",
    label: "SUPPORTS",
    title: "Labor Market Review",
    x: "18%",
    y: "25%",
    type: "support",
  },
  {
    id: "source",
    label: "SOURCE",
    title: "National Statistics Office",
    x: "82%",
    y: "24%",
    type: "source",
  },
  {
    id: "contradict",
    label: "CONTRADICTS",
    title: "Employment Trends Report",
    x: "18%",
    y: "76%",
    type: "contradict",
  },
  {
    id: "context",
    label: "CONTEXT",
    title: "Economic Outlook",
    x: "82%",
    y: "76%",
    type: "context",
  },
]
</script>

<template>
  <section
    id="models"
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-28 sm:py-36"
  >
    <!-- Ambient glow -->
    <div
      class="pointer-events-none absolute left-1/2 top-1/2 h-[32rem] w-[32rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--vl-sage)]/5 blur-[130px]"
    />

    <div class="vl-container relative">
      <!-- Header -->
      <div class="grid gap-10 lg:grid-cols-[1fr_0.7fr] lg:items-end">
        <div>
          <p class="vl-eyebrow">
            Evidence graph
          </p>

          <h2
            class="mt-5 max-w-3xl text-4xl font-semibold leading-[0.98] tracking-[-0.06em] sm:text-5xl lg:text-7xl"
          >
            Truth is rarely
            <span class="vl-gradient-text">
              one-dimensional.
            </span>
          </h2>
        </div>

        <p
          class="max-w-xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8 lg:justify-self-end"
        >
          VeriLens maps claims, sources, evidence, and contradictions into
          a relationship graph — giving you a view of the information
          surrounding a prediction.
        </p>
      </div>

      <!-- Graph workspace -->
      <div
        class="relative mt-20 min-h-[650px] overflow-hidden rounded-[2rem] border border-[var(--vl-border)] bg-[rgba(250,248,242,0.52)] shadow-[0_35px_120px_rgba(32,35,31,0.08)] backdrop-blur-xl sm:min-h-[720px]"
      >
        <!-- Grid -->
        <div
          class="pointer-events-none absolute inset-0 opacity-[0.035]"
          style="
            background-image:
              linear-gradient(var(--vl-ink) 1px, transparent 1px),
              linear-gradient(90deg, var(--vl-ink) 1px, transparent 1px);
            background-size: 56px 56px;
          "
        />

        <!-- Workspace header -->
        <div
          class="absolute inset-x-0 top-0 z-30 flex flex-col gap-4 border-b border-[var(--vl-border)] bg-[rgba(250,248,242,0.65)] px-6 py-5 backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between sm:px-8"
        >
          <div>
            <p
              class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
            >
              Knowledge graph
            </p>

            <p class="mt-1 text-sm font-semibold">
              Claim relationship map
            </p>
          </div>

          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)]"
              />

              <span
                class="text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
              >
                Supporting
              </span>
            </div>

            <div class="flex items-center gap-2">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[var(--vl-terracotta)]"
              />

              <span
                class="text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
              >
                Contradicting
              </span>
            </div>
          </div>
        </div>

        <!-- SVG connections -->
        <svg
          class="pointer-events-none absolute inset-0 z-10 h-full w-full"
          viewBox="0 0 1000 720"
          preserveAspectRatio="none"
        >
          <!-- Support -->
          <path
            d="M180 190 C300 220 350 330 500 360"
            fill="none"
            stroke="rgba(113,129,107,0.38)"
            stroke-width="1.5"
            stroke-dasharray="5 8"
          />

          <!-- Source -->
          <path
            d="M820 180 C700 215 650 325 500 360"
            fill="none"
            stroke="rgba(113,129,107,0.32)"
            stroke-width="1.5"
            stroke-dasharray="5 8"
          />

          <!-- Contradiction -->
          <path
            d="M180 550 C300 520 350 420 500 360"
            fill="none"
            stroke="rgba(184,111,82,0.42)"
            stroke-width="1.5"
            stroke-dasharray="5 8"
          />

          <!-- Context -->
          <path
            d="M820 550 C700 520 650 420 500 360"
            fill="none"
            stroke="rgba(32,35,31,0.18)"
            stroke-width="1.5"
            stroke-dasharray="5 8"
          />

          <!-- Outer connections -->
          <path
            d="M180 190 C420 80 650 80 820 180"
            fill="none"
            stroke="rgba(32,35,31,0.08)"
            stroke-width="1"
            stroke-dasharray="2 12"
          />

          <path
            d="M180 550 C400 650 650 650 820 550"
            fill="none"
            stroke="rgba(32,35,31,0.08)"
            stroke-width="1"
            stroke-dasharray="2 12"
          />
        </svg>

        <!-- Animated signal points -->
        <span
          class="absolute left-[31%] top-[34%] z-20 h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)] shadow-[0_0_14px_rgba(113,129,107,0.7)]"
        />

        <span
          class="absolute left-[69%] top-[33%] z-20 h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)] shadow-[0_0_14px_rgba(113,129,107,0.7)]"
        />

        <span
          class="absolute left-[31%] top-[66%] z-20 h-1.5 w-1.5 rounded-full bg-[var(--vl-terracotta)] shadow-[0_0_14px_rgba(184,111,82,0.7)]"
        />

        <span
          class="absolute left-[69%] top-[66%] z-20 h-1.5 w-1.5 rounded-full bg-[var(--vl-ink)]/50"
        />

        <!-- Nodes -->
        <div
          v-for="node in nodes"
          :key="node.id"
          class="absolute z-20 -translate-x-1/2 -translate-y-1/2"
          :style="{
            left: node.x,
            top: node.y,
          }"
        >
          <!-- Claim node -->
          <div
            v-if="node.type === 'claim'"
            class="relative flex h-48 w-48 items-center justify-center rounded-full border border-[var(--vl-sage)]/25 bg-[rgba(250,248,242,0.78)] shadow-[0_25px_80px_rgba(32,35,31,0.12)] backdrop-blur-2xl sm:h-56 sm:w-56"
          >
            <div
              class="absolute inset-5 rounded-full border border-[var(--vl-sage)]/10"
            />

            <div
              class="absolute inset-10 rounded-full border border-[var(--vl-ink)]/8"
            />

            <div class="relative max-w-[130px] text-center">
              <p
                class="text-[8px] font-bold uppercase tracking-[0.2em] text-[var(--vl-sage-dark)]"
              >
                {{ node.label }}
              </p>

              <p
                class="mt-3 text-sm font-semibold leading-5 tracking-[-0.02em]"
              >
                {{ node.title }}
              </p>

              <div
                class="mx-auto mt-4 h-1 w-8 rounded-full bg-[var(--vl-sage)]"
              />
            </div>
          </div>

          <!-- Outer nodes -->
          <div
            v-else
            class="group w-44 rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.78)] p-4 shadow-[0_20px_60px_rgba(32,35,31,0.08)] backdrop-blur-xl transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_28px_70px_rgba(32,35,31,0.12)] sm:w-52"
          >
            <div class="flex items-center justify-between">
              <span
                class="h-2 w-2 rounded-full"
                :class="{
                  'bg-[var(--vl-sage)] shadow-[0_0_12px_rgba(113,129,107,0.6)]':
                    node.type === 'support',
                  'bg-[var(--vl-terracotta)] shadow-[0_0_12px_rgba(184,111,82,0.5)]':
                    node.type === 'contradict',
                  'bg-[var(--vl-ink)]/45':
                    node.type === 'source' || node.type === 'context',
                }"
              />

              <span
                class="text-[8px] font-bold uppercase tracking-[0.16em] text-[var(--vl-muted)]"
              >
                {{ node.label }}
              </span>
            </div>

            <p
              class="mt-5 text-xs font-semibold leading-5 tracking-[-0.01em]"
            >
              {{ node.title }}
            </p>

            <div
              class="mt-5 h-1 overflow-hidden rounded-full bg-[var(--vl-ink)]/6"
            >
              <div
                class="h-full rounded-full"
                :class="{
                  'w-[83%] bg-[var(--vl-sage)]':
                    node.type === 'support',
                  'w-[71%] bg-[var(--vl-terracotta)]':
                    node.type === 'contradict',
                  'w-[64%] bg-[var(--vl-ink)]/35':
                    node.type === 'source',
                  'w-[58%] bg-[var(--vl-ink)]/25':
                    node.type === 'context',
                }"
              />
            </div>
          </div>
        </div>

        <!-- Graph metadata -->
        <div
          class="absolute bottom-5 left-5 z-30 rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.72)] px-4 py-3 backdrop-blur-xl sm:bottom-7 sm:left-7"
        >
          <div class="flex items-center gap-5">
            <div>
              <p
                class="text-[8px] font-bold uppercase tracking-[0.15em] text-[var(--vl-muted)]"
              >
                Claims
              </p>

              <p class="mt-1 text-sm font-semibold">
                01
              </p>
            </div>

            <div>
              <p
                class="text-[8px] font-bold uppercase tracking-[0.15em] text-[var(--vl-muted)]"
              >
                Evidence
              </p>

              <p class="mt-1 text-sm font-semibold">
                04
              </p>
            </div>

            <div>
              <p
                class="text-[8px] font-bold uppercase tracking-[0.15em] text-[var(--vl-muted)]"
              >
                Relationships
              </p>

              <p class="mt-1 text-sm font-semibold">
                08
              </p>
            </div>
          </div>
        </div>

        <!-- Bottom explanation -->
        <div
          class="absolute bottom-5 right-5 z-30 hidden max-w-xs rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.72)] px-4 py-3 backdrop-blur-xl sm:block sm:bottom-7 sm:right-7"
        >
          <p
            class="text-[8px] font-bold uppercase tracking-[0.15em] text-[var(--vl-sage-dark)]"
          >
            Graph insight
          </p>

          <p
            class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
          >
            A claim can be supported by one source while another source
            introduces a contradiction.
          </p>
        </div>
      </div>

      <!-- Closing -->
      <div
        class="mt-12 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <p
          class="max-w-2xl text-sm leading-6 text-[var(--vl-muted)]"
        >
          The graph keeps the relationships visible instead of flattening
          everything into a single confidence number.
        </p>

        <span
          class="text-xs font-semibold text-[var(--vl-sage-dark)]"
        >
          Explore the evidence network →
        </span>
      </div>
    </div>
  </section>
</template>
