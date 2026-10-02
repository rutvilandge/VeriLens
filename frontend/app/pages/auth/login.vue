<script setup lang="ts">
import { ref } from "vue";

import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  ShieldCheck,
} from "lucide-vue-next";

/* -------------------------------------------------------------------------- */
/* Form state                                                                 */
/* -------------------------------------------------------------------------- */

const showPassword = ref(false);

const email = ref("");
const password = ref("");

const { login, loading, error } = useVeriLensAuth();

/* -------------------------------------------------------------------------- */
/* Login                                                                      */
/* -------------------------------------------------------------------------- */

const handleLogin = async () => {
  if (loading.value) {
    return;
  }

  const trimmedEmail = email.value.trim().toLowerCase();

  if (!trimmedEmail || !password.value) {
    return;
  }

  await login(
    trimmedEmail,
    password.value,
  );
};
</script>

<template>
  <main
    class="min-h-screen overflow-hidden bg-[var(--vl-bg)] text-[var(--vl-ink)]"
  >
    <!-- Ambient background -->
    <div
      class="pointer-events-none fixed inset-0 overflow-hidden"
    >
      <div
        class="absolute -left-32 top-20 h-96 w-96 rounded-full bg-[var(--vl-sage)]/10 blur-3xl"
      />

      <div
        class="absolute -right-24 bottom-0 h-96 w-96 rounded-full bg-[var(--vl-terracotta)]/10 blur-3xl"
      />

      <div
        class="absolute inset-0 opacity-[0.035]"
        style="
          background-image:
            linear-gradient(rgba(32,35,31,0.8) 1px, transparent 1px),
            linear-gradient(90deg, rgba(32,35,31,0.8) 1px, transparent 1px);
          background-size: 48px 48px;
        "
      />
    </div>

    <!-- Top navigation -->
    <header
      class="relative z-10 px-6 py-6 sm:px-10 lg:px-14"
    >
      <NuxtLink
        to="/"
        class="group inline-flex items-center gap-3 transition-opacity hover:opacity-70"
      >
        <span
          class="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--vl-border)] bg-[var(--vl-surface)] shadow-sm"
        >
          <span
            class="h-3.5 w-3.5 rounded-full border-2 border-[var(--vl-sage-dark)]"
          />
        </span>

        <span
          class="text-[1.05rem] font-semibold tracking-[-0.03em]"
        >
          VeriLens
        </span>
      </NuxtLink>
    </header>

    <!-- Main -->
    <section
      class="relative z-10 mx-auto flex min-h-[calc(100vh-92px)] w-[min(1180px,calc(100%-32px))] items-center justify-center py-10 sm:w-[min(1180px,calc(100%-48px))] lg:py-16"
    >
      <div
        class="grid w-full max-w-5xl overflow-hidden rounded-[32px] border border-[var(--vl-border)] bg-[rgba(250,248,242,0.62)] shadow-[0_30px_100px_rgba(32,35,31,0.10)] backdrop-blur-2xl lg:grid-cols-[1.05fr_0.95fr]"
      >
        <!-- Visual side -->
        <div
          class="relative hidden min-h-[650px] overflow-hidden border-r border-[var(--vl-border)] lg:block"
        >
          <!-- subtle radial glows -->
          <div
            class="absolute left-12 top-20 h-56 w-56 rounded-full bg-[var(--vl-sage)]/10 blur-3xl"
          />

          <div
            class="absolute bottom-10 right-10 h-48 w-48 rounded-full bg-[var(--vl-terracotta)]/10 blur-3xl"
          />

          <div
            class="relative flex h-full flex-col justify-between p-12"
          >
            <div>
              <p class="vl-eyebrow">
                Evidence intelligence
              </p>

              <h1
                class="mt-6 max-w-lg text-5xl font-semibold leading-[0.98] tracking-[-0.055em]"
              >
                See beyond the
                <span class="vl-gradient-text">
                  prediction.
                </span>
              </h1>

              <p
                class="mt-6 max-w-md text-[0.98rem] leading-7 text-[var(--vl-muted)]"
              >
                Sign in to continue into VeriLens and
                turn content, signals, sources, and
                evidence into an explainable
                understanding.
              </p>
            </div>

            <!-- Lens visualization -->
            <div
              class="relative flex flex-1 items-center justify-center"
            >
              <div
                class="relative h-72 w-72"
              >
                <!-- outer ring -->
                <div
                  class="absolute inset-0 rounded-full border border-[var(--vl-sage-dark)]/20"
                />

                <div
                  class="absolute inset-7 rounded-full border border-[var(--vl-sage-dark)]/20"
                />

                <div
                  class="absolute inset-14 rounded-full border border-[var(--vl-sage-dark)]/30 bg-[rgba(113,129,107,0.06)] shadow-[0_20px_60px_rgba(113,129,107,0.12)] backdrop-blur-xl"
                />

                <!-- center -->
                <div
                  class="absolute left-1/2 top-1/2 flex h-24 w-24 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-[var(--vl-sage-dark)]/30 bg-[rgba(250,248,242,0.8)] shadow-xl"
                >
                  <div
                    class="h-10 w-10 rounded-full border-[3px] border-[var(--vl-sage-dark)]/70"
                  />
                </div>

                <!-- signal nodes -->
                <span
                  class="absolute left-1/2 top-0 h-2.5 w-2.5 -translate-x-1/2 rounded-full bg-[var(--vl-sage-dark)] shadow-[0_0_18px_rgba(113,129,107,0.35)]"
                />

                <span
                  class="absolute bottom-5 left-8 h-2.5 w-2.5 rounded-full bg-[var(--vl-terracotta)] shadow-[0_0_18px_rgba(184,111,82,0.3)]"
                />

                <span
                  class="absolute bottom-8 right-5 h-2.5 w-2.5 rounded-full bg-[var(--vl-sage-dark)] shadow-[0_0_18px_rgba(113,129,107,0.35)]"
                />

                <!-- labels -->
                <span
                  class="absolute -left-3 top-1/2 -translate-y-1/2 rounded-full border border-[var(--vl-border)] bg-[var(--vl-surface)] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
                >
                  NLP
                </span>

                <span
                  class="absolute -right-5 top-1/3 rounded-full border border-[var(--vl-border)] bg-[var(--vl-surface)] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
                >
                  Vision
                </span>

                <span
                  class="absolute bottom-0 left-1/2 -translate-x-1/2 rounded-full border border-[var(--vl-border)] bg-[var(--vl-surface)] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
                >
                  Evidence
                </span>
              </div>
            </div>

            <div
              class="flex items-center gap-3 text-xs text-[var(--vl-muted)]"
            >
              <ShieldCheck :size="15" />

              <span>
                Evidence-first intelligence
              </span>
            </div>
          </div>
        </div>

        <!-- Form side -->
        <div
          class="flex min-h-[650px] items-center p-7 sm:p-10 lg:p-14"
        >
          <div class="mx-auto w-full max-w-md">
            <!-- Back -->
            <NuxtLink
              to="/"
              class="mb-10 inline-flex items-center gap-2 text-sm text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)]"
            >
              <ArrowLeft :size="15" />

              Back to VeriLens
            </NuxtLink>

            <!-- Heading -->
            <div>
              <p class="vl-eyebrow">
                Welcome back
              </p>

              <h2
                class="mt-3 text-4xl font-semibold tracking-[-0.05em] sm:text-[2.8rem]"
              >
                Sign in.
              </h2>

              <p
                class="mt-4 text-sm leading-6 text-[var(--vl-muted)]"
              >
                Continue to your VeriLens workspace
                and your evidence intelligence.
              </p>
            </div>

            <!-- Form -->
            <form
              class="mt-9 space-y-5"
              @submit.prevent="handleLogin"
            >
              <!-- Error -->
              <div
                v-if="error"
                class="rounded-2xl border border-[var(--vl-terracotta)]/25 bg-[var(--vl-terracotta)]/8 px-4 py-3 text-sm leading-5 text-[var(--vl-terracotta)]"
              >
                {{ error }}
              </div>

              <!-- Email -->
              <div>
                <label
                  for="email"
                  class="mb-2 block text-sm font-medium"
                >
                  Email address
                </label>

                <input
                  id="email"
                  v-model="email"
                  type="email"
                  autocomplete="email"
                  placeholder="you@example.com"
                  required
                  :disabled="loading"
                  class="h-13 w-full rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.72)] px-4 text-sm outline-none transition-all placeholder:text-[var(--vl-muted)]/60 focus:border-[var(--vl-sage-dark)]/50 focus:bg-[var(--vl-surface)] focus:ring-4 focus:ring-[var(--vl-sage)]/8 disabled:cursor-not-allowed disabled:opacity-60"
                />
              </div>

              <!-- Password -->
              <div>
                <div
                  class="mb-2 flex items-center justify-between"
                >
                  <label
                    for="password"
                    class="block text-sm font-medium"
                  >
                    Password
                  </label>

                  <button
                    type="button"
                    :disabled="loading"
                    class="text-xs font-medium text-[var(--vl-sage-dark)] transition-opacity hover:opacity-60 disabled:opacity-40"
                  >
                    Forgot password?
                  </button>
                </div>

                <div class="relative">
                  <input
                    id="password"
                    v-model="password"
                    :type="
                      showPassword
                        ? 'text'
                        : 'password'
                    "
                    autocomplete="current-password"
                    placeholder="Enter your password"
                    required
                    :disabled="loading"
                    class="h-13 w-full rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.72)] px-4 pr-12 text-sm outline-none transition-all placeholder:text-[var(--vl-muted)]/60 focus:border-[var(--vl-sage-dark)]/50 focus:bg-[var(--vl-surface)] focus:ring-4 focus:ring-[var(--vl-sage)]/8 disabled:cursor-not-allowed disabled:opacity-60"
                  />

                  <button
                    type="button"
                    :disabled="loading"
                    :aria-label="
                      showPassword
                        ? 'Hide password'
                        : 'Show password'
                    "
                    class="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)] disabled:opacity-40"
                    @click="
                      showPassword = !showPassword
                    "
                  >
                    <EyeOff
                      v-if="showPassword"
                      :size="18"
                    />

                    <Eye
                      v-else
                      :size="18"
                    />
                  </button>
                </div>
              </div>

              <!-- Sign in -->
              <button
                type="submit"
                :disabled="loading"
                class="group flex h-13 w-full items-center justify-center gap-2 rounded-2xl bg-[var(--vl-sage-dark)] px-5 text-sm font-semibold text-white shadow-[0_12px_30px_rgba(77,93,74,0.18)] transition-all hover:-translate-y-0.5 hover:bg-[var(--vl-ink)] hover:shadow-[0_16px_35px_rgba(32,35,31,0.18)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              >
                <span>
                  {{
                    loading
                      ? "Signing in..."
                      : "Sign in"
                  }}
                </span>

                <ArrowRight
                  :size="16"
                  class="transition-transform group-hover:translate-x-1"
                />
              </button>
            </form>

            <!-- Divider -->
            <div class="my-8 flex items-center gap-4">
              <div
                class="h-px flex-1 bg-[var(--vl-border)]"
              />

              <span
                class="text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
              >
                or
              </span>

              <div
                class="h-px flex-1 bg-[var(--vl-border)]"
              />
            </div>

            <!-- Register -->
            <p
              class="text-center text-sm text-[var(--vl-muted)]"
            >
              Don't have an account?

              <NuxtLink
                to="/auth/register"
                class="font-semibold text-[var(--vl-sage-dark)] transition-opacity hover:opacity-60"
              >
                Create one
              </NuxtLink>
            </p>

            <!-- Footer -->
            <p
              class="mt-8 text-center text-[11px] leading-5 text-[var(--vl-muted)]/75"
            >
              By continuing, you agree to the VeriLens
              terms and acknowledge our privacy
              practices.
            </p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
