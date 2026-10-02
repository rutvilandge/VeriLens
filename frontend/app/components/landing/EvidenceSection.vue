<script setup lang="ts">
const evidence = [
  {
    type: "SUPPORTS",
    source: "National Statistics Office",
    title: "Annual Labor Market Review",
    score: "0.83",
    accent: "sage",
  },
  {
    type: "CONTRADICTS",
    source: "Independent Research Archive",
    title: "Employment Trends Report",
    score: "0.71",
    accent: "terracotta",
  },
  {
    type: "CONTEXT",
    source: "Economic Outlook",
    title: "Quarterly Market Analysis",
    score: "0.64",
    accent: "ink",
  },
]
</script>

<template>
  <section
    id="evidence"
    class="relative overflow-hidden border-t border-[var(--vl-border)] py-28 sm:py-36"
  >
    <div
      class="pointer-events-none absolute left-[-10rem] top-[25%] h-[30rem] w-[30rem] rounded-full bg-[var(--vl-sage)]/5 blur-[130px]"
    />

    <div
      class="pointer-events-none absolute right-[-8rem] bottom-[10%] h-[28rem] w-[28rem] rounded-full bg-[var(--vl-terracotta)]/5 blur-[120px]"
    />

    <div class="vl-container relative">
      <!-- Header -->
      <div class="grid gap-10 lg:grid-cols-[1fr_0.75fr] lg:items-end">
        <div>
          <p class="vl-eyebrow">
            Evidence intelligence
          </p>

          <h2
            class="mt-5 max-w-3xl text-4xl font-semibold leading-[0.98] tracking-[-0.06em] sm:text-5xl lg:text-7xl"
          >
            Don't hide the
            <span class="vl-gradient-text">
              reasoning.
            </span>
          </h2>
        </div>

        <p
          class="max-w-xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8 lg:justify-self-end"
        >
          Every important claim can be traced through sources, relationships,
          relevance, and confidence — turning a prediction into something
          you can actually investigate.
        </p>
      </div>

      <!-- Evidence workspace -->
      <div
        class="mt-20 overflow-hidden rounded-[2rem] border border-[var(--vl-border)] bg-white/40 shadow-[0_35px_110px_rgba(32,35,31,0.08)] backdrop-blur-xl"
      >
        <!-- Workspace header -->
        <div
          class="flex flex-col gap-5 border-b border-[var(--vl-border)] px-6 py-6 sm:px-8 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <div class="flex items-center gap-3">
              <span
                class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--vl-sage)]/10 text-[10px] font-bold text-[var(--vl-sage-dark)]"
              >
                E
              </span>

              <div>
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                >
                  Claim under investigation
                </p>

                <p class="mt-1 text-sm font-semibold">
                  “The unemployment rate fell significantly in 2024.”
                </p>
              </div>
            </div>
          </div>

          <div
            class="flex items-center gap-2 self-start rounded-full border border-[var(--vl-border)] bg-white/55 px-3 py-2"
          >
            <span
              class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)]"
            />

            <span
              class="text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-sage-dark)]"
            >
              Evidence mapped
            </span>
          </div>
        </div>

        <!-- Workspace -->
        <div
          class="grid lg:grid-cols-[0.72fr_1.28fr]"
        >
          <!-- Claim side -->
          <div
            class="relative border-b border-[var(--vl-border)] p-7 sm:p-9 lg:border-b-0 lg:border-r"
          >
            <p
              class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
            >
              Claim
            </p>

            <div
              class="mt-7 rounded-[1.5rem] border border-[var(--vl-border)] bg-[var(--vl-bg)]/70 p-6"
            >
              <div
                class="flex items-center justify-between"
              >
                <span
                  class="rounded-full bg-[var(--vl-terracotta)]/10 px-2.5 py-1 text-[8px] font-bold uppercase tracking-[0.14em] text-[var(--vl-terracotta)]"
                >
                  Claim signal
                </span>

                <span
                  class="text-[10px] font-semibold text-[var(--vl-muted)]"
                >
                  #001
                </span>
              </div>

              <p
                class="mt-6 text-lg font-medium leading-7 tracking-[-0.025em]"
              >
                “The unemployment rate fell significantly in 2024.”
              </p>

              <div class="mt-7 space-y-3">
                <div
                  class="flex items-center justify-between text-[10px]"
                >
                  <span class="text-[var(--vl-muted)]">
                    Temporal signal
                  </span>

                  <span class="font-semibold">
                    2024
                  </span>
                </div>

                <div
                  class="flex items-center justify-between text-[10px]"
                >
                  <span class="text-[var(--vl-muted)]">
                    Claim type
                  </span>

                  <span class="font-semibold">
                    Numeric
                  </span>
                </div>

                <div
                  class="flex items-center justify-between text-[10px]"
                >
                  <span class="text-[var(--vl-muted)]">
                    Evidence links
                  </span>

                  <span class="font-semibold">
                    3
                  </span>
                </div>
              </div>
            </div>

            <!-- Arrow -->
            <div
              class="mt-6 flex items-center gap-3 text-[9px] font-bold uppercase tracking-[0.16em] text-[var(--vl-muted)]"
            >
              <span
                class="h-px w-10 bg-[var(--vl-ink)]/15"
              />

              Evidence relationships

              <span
                class="text-[var(--vl-sage-dark)]"
              >
                →
              </span>
            </div>
          </div>

          <!-- Evidence side -->
          <div class="p-7 sm:p-9">
            <div
              class="mb-6 flex items-center justify-between"
            >
              <div>
                <p
                  class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
                >
                  Evidence network
                </p>

                <p class="mt-1 text-sm font-semibold">
                  Sources connected to the claim
                </p>
              </div>

              <span
                class="text-[9px] font-semibold text-[var(--vl-muted)]"
              >
                3 relationships
              </span>
            </div>

            <div class="space-y-3">
              <article
                v-for="item in evidence"
                :key="item.title"
                class="group relative overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-bg)]/55 p-4 transition-all duration-500 hover:-translate-y-1 hover:bg-white/65 hover:shadow-lg"
              >
                <div
                  class="flex items-center gap-4"
                >
                  <!-- Relation -->
                  <div
                    class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-[8px] font-bold uppercase tracking-[0.08em]"
                    :class="{
                      'bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]':
                        item.accent === 'sage',
                      'bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]':
                        item.accent === 'terracotta',
                      'bg-[var(--vl-ink)]/7 text-[var(--vl-ink)]':
                        item.accent === 'ink',
                    }"
                  >
                    {{ item.type }}
                  </div>

                  <!-- Source -->
                  <div class="min-w-0 flex-1">
                    <p
                      class="truncate text-[9px] font-bold uppercase tracking-[0.15em] text-[var(--vl-muted)]"
                    >
                      {{ item.source }}
                    </p>

                    <p
                      class="mt-1 truncate text-sm font-semibold tracking-[-0.02em]"
                    >
                      {{ item.title }}
                    </p>
                  </div>

                  <!-- Score -->
                  <div class="hidden shrink-0 text-right sm:block">
                    <p
                      class="text-[8px] font-bold uppercase tracking-[0.15em] text-[var(--vl-muted)]"
                    >
                      Strength
                    </p>

                    <p
                      class="mt-1 text-sm font-semibold"
                    >
                      {{ item.score }}
                    </p>
                  </div>
                </div>

                <!-- Strength bar -->
                <div
                  class="mt-4 h-1 overflow-hidden rounded-full bg-[var(--vl-ink)]/6"
                >
                  <div
                    class="h-full origin-left rounded-full transition-transform duration-700 group-hover:scale-x-105"
                    :class="{
                      'w-[83%] bg-[var(--vl-sage)]':
                        item.score === '0.83',
                      'w-[71%] bg-[var(--vl-terracotta)]':
                        item.score === '0.71',
                      'w-[64%] bg-[var(--vl-ink)]/45':
                        item.score === '0.64',
                    }"
                  />
                </div>
              </article>
            </div>

            <!-- Relationship legend -->
            <div
              class="mt-7 flex flex-wrap gap-x-6 gap-y-3 border-t border-[var(--vl-border)] pt-6"
            >
              <div class="flex items-center gap-2">
                <span
                  class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)]"
                />

                <span
                  class="text-[9px] font-semibold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
                >
                  Supporting
                </span>
              </div>

              <div class="flex items-center gap-2">
                <span
                  class="h-1.5 w-1.5 rounded-full bg-[var(--vl-terracotta)]"
                />

                <span
                  class="text-[9px] font-semibold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
                >
                  Contradicting
                </span>
              </div>

              <div class="flex items-center gap-2">
                <span
                  class="h-1.5 w-1.5 rounded-full bg-[var(--vl-ink)]/50"
                />

                <span
                  class="text-[9px] font-semibold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
                >
                  Context
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom insight -->
        <div
          class="border-t border-[var(--vl-border)] bg-[var(--vl-sage)]/[0.035] px-6 py-5 sm:px-8"
        >
          <div
            class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
          >
            <p
              class="text-sm leading-6 text-[var(--vl-muted)]"
            >
              Evidence strength combines relevance, source reliability,
              and relationship confidence.
            </p>

            <span
              class="shrink-0 text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              Claim → Source → Evidence
            </span>
          </div>
        </div>
      </div>

      <!-- Closing line -->
      <div
        class="mt-12 grid gap-6 sm:grid-cols-3"
      >
        <div>
          <p class="text-2xl font-semibold tracking-[-0.04em]">
            Traceable
          </p>

          <p class="mt-2 text-sm leading-6 text-[var(--vl-muted)]">
            Follow a prediction back to the evidence behind it.
          </p>
        </div>

        <div>
          <p class="text-2xl font-semibold tracking-[-0.04em]">
            Relational
          </p>

          <p class="mt-2 text-sm leading-6 text-[var(--vl-muted)]">
            Supporting and contradicting signals coexist in the graph.
          </p>
        </div>

        <div>
          <p class="text-2xl font-semibold tracking-[-0.04em]">
            Grounded
          </p>

          <p class="mt-2 text-sm leading-6 text-[var(--vl-muted)]">
            Explanations stay connected to retrieved evidence.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
