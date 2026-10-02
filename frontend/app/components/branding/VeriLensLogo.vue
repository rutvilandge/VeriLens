<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: "sm" | "md" | "lg"
  }>(),
  {
    size: "md",
  },
)
</script>

<template>
  <div
    class="vl-logo"
    :class="`vl-logo--${size}`"
    aria-label="VeriLens"
    role="img"
  >
    <svg
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="h-full w-full"
    >
      <!-- Outer lens -->
      <circle
        cx="32"
        cy="32"
        r="27"
        class="vl-logo-ring"
      />

      <!-- Aperture / V geometry -->
      <path
        d="M17 19L28.5 45L32 37L35.5 45L47 19"
        class="vl-logo-mark"
      />

      <!-- Lens focus point -->
      <circle
        cx="32"
        cy="31"
        r="3.5"
        class="vl-logo-focus"
      />

      <!-- Tiny evidence signal -->
      <circle
        cx="49"
        cy="15"
        r="2"
        class="vl-logo-signal"
      />

      <path
        d="M46.5 17.5L43 21"
        class="vl-logo-signal-line"
      />
    </svg>
  </div>
</template>

<style scoped>
.vl-logo {
  flex-shrink: 0;
  transition:
    transform 400ms cubic-bezier(0.16, 1, 0.3, 1),
    filter 400ms ease;
}

.vl-logo--sm {
  width: 30px;
  height: 30px;
}

.vl-logo--md {
  width: 38px;
  height: 38px;
}

.vl-logo--lg {
  width: 56px;
  height: 56px;
}

.vl-logo-ring {
  stroke: var(--vl-ink);
  stroke-width: 1.5;
  opacity: 0.9;
}

.vl-logo-mark {
  stroke: var(--vl-ink);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.vl-logo-focus {
  fill: var(--vl-sage);
}

.vl-logo-signal {
  fill: var(--vl-terracotta);
}

.vl-logo-signal-line {
  stroke: var(--vl-terracotta);
  stroke-width: 1.5;
  stroke-linecap: round;
  opacity: 0.7;
}

.vl-logo:hover {
  transform: rotate(-3deg) scale(1.04);
  filter: drop-shadow(0 8px 20px rgba(113, 129, 107, 0.16));
}
</style>
