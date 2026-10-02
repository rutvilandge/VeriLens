<script setup lang="ts">
import { ref } from "vue"

const visual = ref<HTMLElement | null>(null)

const handlePointerMove = (event: PointerEvent) => {
  if (
    !visual.value ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    return
  }

  const rect = visual.value.getBoundingClientRect()

  const x = (event.clientX - rect.left) / rect.width - 0.5
  const y = (event.clientY - rect.top) / rect.height - 0.5

  visual.value.style.setProperty("--mouse-x", `${x * 12}px`)
  visual.value.style.setProperty("--mouse-y", `${y * 12}px`)
}

const resetPointer = () => {
  if (!visual.value) return

  visual.value.style.setProperty("--mouse-x", "0px")
  visual.value.style.setProperty("--mouse-y", "0px")
}
</script>

<template>
  <section class="relative min-h-screen overflow-hidden pt-32">
    <!-- Ambient atmosphere -->
    <div
      class="pointer-events-none absolute left-[15%] top-[20%] h-72 w-72 rounded-full bg-[var(--vl-sage)]/8 blur-[100px]"
    />

    <div
      class="pointer-events-none absolute right-[8%] top-[8%] h-96 w-96 rounded-full bg-[var(--vl-terracotta)]/6 blur-[120px]"
    />

    <div
      class="pointer-events-none absolute bottom-0 left-1/2 h-80 w-[40rem] -translate-x-1/2 rounded-full bg-white/50 blur-[100px]"
    />

    <!-- Fine editorial grid -->
    <div
      class="pointer-events-none absolute inset-0 opacity-[0.035]"
      style="
        background-image:
          linear-gradient(var(--vl-ink) 1px, transparent 1px),
          linear-gradient(90deg, var(--vl-ink) 1px, transparent 1px);
        background-size: 72px 72px;
      "
    />

    <div class="vl-container relative">
      <div
        class="grid min-h-[calc(100vh-8rem)] items-center gap-16 pb-24 lg:grid-cols-[0.9fr_1.1fr] lg:gap-8"
      >
        <!-- ================================================= -->
        <!-- LEFT -->
        <!-- ================================================= -->

        <div class="relative z-10 max-w-2xl">
          <!-- Eyebrow -->
          <div
            class="mb-7 inline-flex items-center gap-2 rounded-full border border-[var(--vl-border)] bg-white/50 px-3.5 py-2 shadow-sm backdrop-blur-xl"
          >
            <span
              class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)] shadow-[0_0_12px_rgba(113,129,107,0.6)]"
            />

            <span class="vl-eyebrow">
              Multimodal AI · Evidence Intelligence
            </span>
          </div>

          <!-- Heading -->
          <h1
            class="max-w-3xl text-[3.2rem] font-semibold leading-[0.94] tracking-[-0.065em] sm:text-6xl lg:text-7xl xl:text-[5.7rem]"
          >
            Don't just detect.
            <br />

            <span class="vl-gradient-text">
              Understand.
            </span>
          </h1>

          <!-- Description -->
          <p
            class="mt-8 max-w-xl text-base leading-7 text-[var(--vl-muted)] sm:text-lg sm:leading-8"
          >
            VeriLens brings text, images, models, sources, and evidence
            together to reveal what a piece of content actually means —
            and why.
          </p>

          <!-- CTA -->
          <div class="mt-9 flex flex-wrap items-center gap-4">
            <!-- Start an analysis → Login -->
            <NuxtLink
              to="/auth/login"
              class="group inline-flex items-center gap-3 rounded-full bg-[var(--vl-ink)] px-6 py-3.5 text-sm font-semibold text-white shadow-[0_18px_45px_rgba(32,35,31,0.14)] transition-all duration-500 hover:-translate-y-1 hover:bg-[var(--vl-sage-dark)]"
            >
              <span>Start an analysis</span>

              <span
                class="transition-transform duration-500 group-hover:translate-x-1.5"
                aria-hidden="true"
              >
                →
              </span>
            </NuxtLink>

            <!-- Explore the system → Workflow -->
            <a
              href="#workflow"
              class="group inline-flex items-center gap-2 rounded-full border border-[var(--vl-border)] bg-white/45 px-6 py-3.5 text-sm font-semibold text-[var(--vl-ink)] backdrop-blur-xl transition-all duration-300 hover:-translate-y-0.5 hover:bg-white/70"
            >
              Explore the system

              <span
                class="text-[var(--vl-muted)] transition-transform duration-300 group-hover:translate-y-0.5"
              >
                ↓
              </span>
            </a>
          </div>

          <!-- Capability strip -->
          <div
            class="mt-12 flex flex-wrap items-center gap-x-6 gap-y-3"
          >
            <div class="flex items-center gap-2">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage)]"
              />
              <span class="text-xs text-[var(--vl-muted)]">
                Text
              </span>
            </div>

            <span class="text-xs text-black/15">/</span>

            <div class="flex items-center gap-2">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[var(--vl-terracotta)]"
              />
              <span class="text-xs text-[var(--vl-muted)]">
                Vision
              </span>
            </div>

            <span class="text-xs text-black/15">/</span>

            <div class="flex items-center gap-2">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[var(--vl-sage-dark)]"
              />
              <span class="text-xs text-[var(--vl-muted)]">
                Evidence
              </span>
            </div>

            <span class="text-xs text-black/15">/</span>

            <div class="flex items-center gap-2">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[var(--vl-ink)]"
              />
              <span class="text-xs text-[var(--vl-muted)]">
                Explainability
              </span>
            </div>
          </div>
        </div>

        <!-- ================================================= -->
        <!-- RIGHT: CINEMATIC INTELLIGENCE OBJECT -->
        <!-- ================================================= -->

        <div
          ref="visual"
          class="relative mx-auto w-full max-w-[680px]"
          @pointermove="handlePointerMove"
          @pointerleave="resetPointer"
        >
          <!-- Outer aura -->
          <div
            class="pointer-events-none absolute inset-[10%] rounded-full bg-[var(--vl-sage)]/10 blur-[90px]"
          />

          <!-- Orbital ring -->
          <div
            class="pointer-events-none absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-ink)]/6 sm:h-[520px] sm:w-[520px]"
          />

          <div
            class="pointer-events-none absolute left-1/2 top-1/2 h-[330px] w-[330px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-sage)]/10 sm:h-[420px] sm:w-[420px]"
          />

          <!-- Main object -->
          <div
            class="relative min-h-[540px] transition-transform duration-700 ease-out"
            :style="{
              transform:
                'translate3d(var(--mouse-x, 0px), var(--mouse-y, 0px), 0)',
            }"
          >
            <!-- Floating content card -->
            <div
              class="absolute left-[3%] top-[17%] z-20 w-[235px] -rotate-[5deg] rounded-[1.5rem] border border-[var(--vl-border)] bg-[rgba(250,248,242,0.78)] p-5 shadow-[0_30px_80px_rgba(32,35,31,0.12)] backdrop-blur-xl transition-transform duration-700 hover:rotate-0"
            >
              <div class="flex items-center justify-between">
                <span
                  class="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--vl-muted)]"
                >
                  Content
                </span>

                <span
                  class="rounded-full bg-[var(--vl-sage)]/10 px-2 py-1 text-[8px] font-bold text-[var(--vl-sage-dark)]"
                >
                  INPUT
                </span>
              </div>

              <div
                class="mt-5 rounded-xl border border-black/5 bg-white/55 p-3"
              >
                <div class="space-y-2">
                  <div class="h-2 w-[82%] rounded-full bg-[var(--vl-ink)]/10" />
                  <div class="h-2 w-[94%] rounded-full bg-[var(--vl-ink)]/7" />
                  <div class="h-2 w-[67%] rounded-full bg-[var(--vl-ink)]/10" />
                  <div class="h-2 w-[76%] rounded-full bg-[var(--vl-ink)]/6" />
                </div>

                <div class="mt-4 flex items-center gap-2">
                  <div
                    class="h-7 w-7 rounded-lg bg-[var(--vl-sage)]/10"
                  />

                  <div class="flex-1">
                    <div class="h-1.5 w-16 rounded-full bg-[var(--vl-ink)]/10" />
                    <div class="mt-1.5 h-1.5 w-10 rounded-full bg-[var(--vl-ink)]/6" />
                  </div>
                </div>
              </div>

              <p
                class="mt-4 text-[10px] leading-4 text-[var(--vl-muted)]"
              >
                Text + image + source material entering the analysis system.
              </p>
            </div>

            <!-- Source card -->
            <div
              class="absolute right-[2%] top-[12%] z-20 w-[190px] rotate-[5deg] rounded-[1.5rem] border border-[var(--vl-border)] bg-white/65 p-4 shadow-[0_25px_65px_rgba(32,35,31,0.10)] backdrop-blur-xl"
            >
              <div class="flex items-center gap-2">
                <div
                  class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--vl-terracotta)]/10"
                >
                  <span class="text-xs text-[var(--vl-terracotta)]">
                    ↗
                  </span>
                </div>

                <div>
                  <p
                    class="text-[9px] font-bold uppercase tracking-wider text-[var(--vl-muted)]"
                  >
                    Source
                  </p>

                  <p class="text-[11px] font-semibold">
                    Reference signal
                  </p>
                </div>
              </div>

              <div
                class="mt-4 h-1.5 w-full rounded-full bg-[var(--vl-ink)]/7"
              />

              <div
                class="mt-2 h-1.5 w-[68%] rounded-full bg-[var(--vl-ink)]/5"
              />
            </div>

            <!-- Central lens -->
            <div
              class="absolute left-1/2 top-1/2 z-30 -translate-x-1/2 -translate-y-1/2"
            >
              <div
                class="relative flex h-40 w-40 items-center justify-center rounded-full border border-[var(--vl-ink)]/10 bg-[rgba(250,248,242,0.62)] shadow-[0_35px_100px_rgba(32,35,31,0.13)] backdrop-blur-2xl sm:h-48 sm:w-48"
              >
                <!-- Inner ring -->
                <div
                  class="absolute inset-5 rounded-full border border-[var(--vl-sage)]/20"
                />

                <div
                  class="absolute inset-10 rounded-full border border-[var(--vl-sage)]/25"
                />

                <!-- Lens -->
                <div
                  class="relative flex h-20 w-20 items-center justify-center rounded-full bg-[var(--vl-ink)] shadow-[0_0_60px_rgba(113,129,107,0.20)]"
                >
                  <div
                    class="absolute inset-2 rounded-full border border-white/10"
                  />

                  <div
                    class="h-7 w-7 rounded-full border border-[var(--vl-sage)]/50 bg-[var(--vl-sage)]/20"
                  />

                  <div
                    class="absolute h-2 w-2 rounded-full bg-[var(--vl-sage)] shadow-[0_0_18px_rgba(113,129,107,0.8)]"
                  />
                </div>

                <!-- Label -->
                <div
                  class="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap"
                >
                  <span
                    class="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--vl-muted)]"
                  >
                    VeriLens engine
                  </span>
                </div>
              </div>
            </div>

            <!-- NLP signal -->
            <div
              class="absolute bottom-[17%] left-[4%] z-20 rounded-2xl border border-[var(--vl-border)] bg-white/65 px-4 py-3 shadow-xl shadow-black/5 backdrop-blur-xl"
            >
              <div class="flex items-center gap-3">
                <span
                  class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--vl-sage)]/10 text-[10px] font-bold text-[var(--vl-sage-dark)]"
                >
                  NLP
                </span>

                <div>
                  <p
                    class="text-[9px] uppercase tracking-wider text-[var(--vl-muted)]"
                  >
                    Language
                  </p>

                  <p class="mt-0.5 text-xs font-semibold">
                    Claim signals
                  </p>
                </div>
              </div>
            </div>

            <!-- Vision signal -->
            <div
              class="absolute bottom-[11%] right-[4%] z-20 rounded-2xl border border-[var(--vl-border)] bg-white/65 px-4 py-3 shadow-xl shadow-black/5 backdrop-blur-xl"
            >
              <div class="flex items-center gap-3">
                <span
                  class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--vl-terracotta)]/10 text-[10px] font-bold text-[var(--vl-terracotta)]"
                >
                  VIS
                </span>

                <div>
                  <p
                    class="text-[9px] uppercase tracking-wider text-[var(--vl-muted)]"
                  >
                    Vision
                  </p>

                  <p class="mt-0.5 text-xs font-semibold">
                    Visual signals
                  </p>
                </div>
              </div>
            </div>

            <!-- Evidence node -->
            <div
              class="absolute bottom-[1%] left-1/2 z-20 -translate-x-1/2 rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.75)] px-5 py-3 shadow-xl shadow-black/5 backdrop-blur-xl"
            >
              <div class="flex items-center gap-3">
                <div class="relative flex h-8 w-8 items-center justify-center">
                  <span
                    class="absolute inset-0 animate-ping rounded-full bg-[var(--vl-sage)]/10"
                  />

                  <span
                    class="relative h-2 w-2 rounded-full bg-[var(--vl-sage)]"
                  />
                </div>

                <div>
                  <p
                    class="text-[9px] uppercase tracking-wider text-[var(--vl-muted)]"
                  >
                    Evidence
                  </p>

                  <p class="mt-0.5 text-xs font-semibold">
                    Connections forming
                  </p>
                </div>
              </div>
            </div>

            <!-- Connection paths -->
            <svg
              class="pointer-events-none absolute inset-0 z-10 h-full w-full overflow-visible"
              viewBox="0 0 680 540"
              preserveAspectRatio="none"
            >
              <path
                d="M155 170 C245 180 255 220 340 270"
                stroke="rgba(113,129,107,0.28)"
                stroke-width="1"
                stroke-dasharray="4 8"
                fill="none"
              />

              <path
                d="M520 155 C455 185 420 220 340 270"
                stroke="rgba(184,111,82,0.28)"
                stroke-width="1"
                stroke-dasharray="4 8"
                fill="none"
              />

              <path
                d="M140 430 C225 395 270 355 340 270"
                stroke="rgba(77,93,74,0.24)"
                stroke-width="1"
                stroke-dasharray="4 8"
                fill="none"
              />

              <path
                d="M540 430 C460 390 420 350 340 270"
                stroke="rgba(113,129,107,0.24)"
                stroke-width="1"
                stroke-dasharray="4 8"
                fill="none"
              />
            </svg>

            <!-- Floating evidence dots -->
            <span
              class="absolute left-[18%] top-[48%] h-2 w-2 rounded-full bg-[var(--vl-sage)] shadow-[0_0_16px_rgba(113,129,107,0.45)]"
            />

            <span
              class="absolute right-[18%] top-[49%] h-1.5 w-1.5 rounded-full bg-[var(--vl-terracotta)] shadow-[0_0_14px_rgba(184,111,82,0.4)]"
            />

            <span
              class="absolute left-[27%] top-[8%] h-1 w-1 rounded-full bg-[var(--vl-ink)]/30"
            />

            <span
              class="absolute right-[28%] bottom-[19%] h-1.5 w-1.5 rounded-full bg-[var(--vl-sage-dark)]/50"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll cue -->
    <div
      class="absolute bottom-8 left-1/2 hidden -translate-x-1/2 items-center gap-3 text-[9px] font-bold uppercase tracking-[0.25em] text-[var(--vl-muted)] md:flex"
    >
      <span>Scroll to investigate</span>

      <span class="h-8 w-px bg-[var(--vl-ink)]/15" />

      <span class="animate-bounce">
        ↓
      </span>
    </div>
  </section>
</template>



