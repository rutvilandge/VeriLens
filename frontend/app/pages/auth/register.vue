<script setup lang="ts">
import { ref } from "vue";
import {
  ArrowRight,
  CheckCircle2,
  Eye,
  EyeOff,
  ShieldCheck,
  Sparkles,
} from "lucide-vue-next";

const config = useRuntimeConfig();

const apiBase =
  String(config.public.apiBase || "");

const name = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");

const showPassword = ref(false);
const showConfirmPassword = ref(false);

const loading = ref(false);
const error = ref("");
const success = ref("");

const handleRegister = async () => {
  error.value = "";
  success.value = "";

  const trimmedName = name.value.trim();
  const trimmedEmail = email.value.trim().toLowerCase();

  if (!trimmedName) {
    error.value = "Please enter your name.";
    return;
  }

  if (!trimmedEmail) {
    error.value = "Please enter your email.";
    return;
  }

  if (password.value.length < 8) {
    error.value =
      "Password must be at least 8 characters.";
    return;
  }

  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    const response = await $fetch<{
      success: boolean;
      message?: string;
      user?: {
        id: string;
        name: string;
        email: string;
      };
    }>(`${apiBase}/api/auth/register`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: {
        name: trimmedName,
        email: trimmedEmail,
        password: password.value,
      },

      credentials: "include",
    });

    if (!response.success) {
      throw new Error(
        response.message ||
          "Unable to create your account.",
      );
    }

    success.value =
      "Account created successfully. Redirecting...";

    setTimeout(() => {
      navigateTo("/auth/login");
    }, 700);
  } catch (err: any) {
    console.error("Registration error:", err);

    error.value =
      err?.data?.message ||
      err?.message ||
      "Unable to create your account.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="register-page">
    <!-- Background -->
    <div class="background-glow glow-one" />
    <div class="background-glow glow-two" />

    <!-- Header -->
    <header class="register-header">
      <NuxtLink
        to="/"
        class="brand"
      >
        <div class="brand-mark">
          <ShieldCheck :size="20" />
        </div>

        <div class="brand-copy">
          <span class="brand-name">
            VeriLens
          </span>

          <span class="brand-caption">
            Evidence Intelligence
          </span>
        </div>
      </NuxtLink>

      <div class="header-status">
        <span class="status-dot" />
        Intelligence platform
      </div>
    </header>

    <!-- Main -->
    <main class="register-main">
      <section class="register-card">
        <!-- Intro -->
        <div class="register-intro">
          <div class="eyebrow">
            <Sparkles :size="13" />
            Create workspace
          </div>

          <h1>
            Start your
            <span>investigation.</span>
          </h1>

          <p>
            Create your VeriLens account and build
            an evidence-driven intelligence workspace.
          </p>
        </div>

        <!-- Form -->
        <form
          class="register-form"
          @submit.prevent="handleRegister"
        >
          <!-- Name -->
          <div class="field">
            <label for="name">
              Full name
            </label>

            <input
              id="name"
              v-model="name"
              type="text"
              name="name"
              autocomplete="name"
              placeholder="Rutvi Landge"
              :disabled="loading"
            />
          </div>

          <!-- Email -->
          <div class="field">
            <label for="email">
              Email
            </label>

            <input
              id="email"
              v-model="email"
              type="email"
              name="email"
              autocomplete="email"
              placeholder="you@example.com"
              :disabled="loading"
            />
          </div>

          <!-- Password -->
          <div class="field">
            <label for="password">
              Password
            </label>

            <div class="password-wrapper">
              <input
                id="password"
                v-model="password"
                :type="
                  showPassword
                    ? 'text'
                    : 'password'
                "
                name="password"
                autocomplete="new-password"
                placeholder="At least 8 characters"
                :disabled="loading"
              />

              <button
                type="button"
                class="password-toggle"
                :aria-label="
                  showPassword
                    ? 'Hide password'
                    : 'Show password'
                "
                @click="
                  showPassword = !showPassword
                "
              >
                <EyeOff
                  v-if="showPassword"
                  :size="17"
                />

                <Eye
                  v-else
                  :size="17"
                />
              </button>
            </div>
          </div>

          <!-- Confirm password -->
          <div class="field">
            <label for="confirmPassword">
              Confirm password
            </label>

            <div class="password-wrapper">
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="
                  showConfirmPassword
                    ? 'text'
                    : 'password'
                "
                name="confirmPassword"
                autocomplete="new-password"
                placeholder="Repeat your password"
                :disabled="loading"
              />

              <button
                type="button"
                class="password-toggle"
                :aria-label="
                  showConfirmPassword
                    ? 'Hide password'
                    : 'Show password'
                "
                @click="
                  showConfirmPassword =
                    !showConfirmPassword
                "
              >
                <EyeOff
                  v-if="showConfirmPassword"
                  :size="17"
                />

                <Eye
                  v-else
                  :size="17"
                />
              </button>
            </div>
          </div>

          <!-- Error -->
          <div
            v-if="error"
            class="message message-error"
          >
            {{ error }}
          </div>

          <!-- Success -->
          <div
            v-if="success"
            class="message message-success"
          >
            <CheckCircle2 :size="17" />
            {{ success }}
          </div>

          <!-- Submit -->
          <button
            type="submit"
            class="register-button"
            :disabled="loading"
          >
            <span v-if="!loading">
              Create account
            </span>

            <span
              v-else
              class="loading-content"
            >
              <span class="spinner" />
              Creating workspace...
            </span>

            <ArrowRight
              v-if="!loading"
              :size="17"
            />
          </button>
        </form>

        <!-- Login -->
        <div class="login-prompt">
          Already have an account?

          <NuxtLink to="/auth/login">
            Sign in
          </NuxtLink>
        </div>

        <!-- Security note -->
        <div class="security-note">
          <ShieldCheck :size="15" />

          <span>
            Your password is securely hashed before
            being stored.
          </span>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.register-page {
  position: relative;

  min-height: 100vh;
  overflow: hidden;

  color: var(--vl-ink);
  background: var(--vl-bg);
}

.background-glow {
  position: absolute;

  pointer-events: none;

  border-radius: 50%;
  filter: blur(80px);

  opacity: 0.35;
}

.glow-one {
  top: -180px;
  left: -130px;

  width: 420px;
  height: 420px;

  background: rgba(113, 129, 107, 0.18);
}

.glow-two {
  right: -160px;
  bottom: -180px;

  width: 430px;
  height: 430px;

  background: rgba(181, 107, 79, 0.12);
}

/* Header */

.register-header {
  position: relative;
  z-index: 2;

  display: flex;
  align-items: center;
  justify-content: space-between;

  min-height: 76px;
  padding: 0 42px;

  border-bottom: 1px solid var(--vl-border);

  background: rgba(244, 241, 232, 0.68);

  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;

  color: inherit;
  text-decoration: none;
}

.brand-mark {
  display: grid;

  width: 40px;
  height: 40px;

  place-items: center;

  color: var(--vl-surface);

  background: var(--vl-sage-dark);
  border-radius: 12px;
}

.brand-copy {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 0.96rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.brand-caption {
  margin-top: 2px;

  color: var(--vl-muted);

  font-size: 0.62rem;
  font-weight: 650;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 7px;

  color: var(--vl-muted);

  font-size: 0.68rem;
  font-weight: 650;
}

.status-dot {
  width: 7px;
  height: 7px;

  background: #668568;
  border-radius: 50%;
}

/* Main */

.register-main {
  position: relative;
  z-index: 2;

  display: flex;

  min-height: calc(100vh - 76px);

  align-items: center;
  justify-content: center;

  padding: 50px 20px 70px;
}

.register-card {
  width: min(480px, 100%);

  padding: 34px;

  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.72),
      rgba(250, 248, 242, 0.6)
    );

  border: 1px solid rgba(32, 35, 31, 0.09);
  border-radius: 22px;

  box-shadow:
    0 30px 80px rgba(32, 35, 31, 0.08);

  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.register-intro {
  margin-bottom: 27px;
}

.eyebrow {
  display: flex;
  align-items: center;
  gap: 7px;

  margin-bottom: 12px;

  color: var(--vl-sage-dark);

  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.register-intro h1 {
  margin: 0;

  font-size: clamp(2rem, 5vw, 2.8rem);
  font-weight: 780;
  letter-spacing: -0.055em;
  line-height: 1;
}

.register-intro h1 span {
  color: var(--vl-sage-dark);
}

.register-intro p {
  margin: 14px 0 0;

  color: var(--vl-muted);

  font-size: 0.78rem;
  line-height: 1.65;
}

/* Form */

.register-form {
  display: flex;
  flex-direction: column;
  gap: 17px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.field label {
  color: var(--vl-ink);

  font-size: 0.69rem;
  font-weight: 750;
}

.field input {
  width: 100%;
  min-height: 46px;

  padding: 0 13px;

  color: var(--vl-ink);

  background: rgba(255, 255, 255, 0.54);

  border: 1px solid var(--vl-border);
  border-radius: 10px;

  outline: none;

  font-family: inherit;
  font-size: 0.76rem;

  transition:
    border-color 160ms ease,
    box-shadow 160ms ease,
    background 160ms ease;
}

.field input::placeholder {
  color: #999e96;
}

.field input:focus {
  background: rgba(255, 255, 255, 0.82);

  border-color: rgba(77, 93, 74, 0.38);

  box-shadow:
    0 0 0 3px rgba(113, 129, 107, 0.09);
}

.field input:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.password-wrapper {
  position: relative;
}

.password-wrapper input {
  padding-right: 46px;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 6px;

  display: grid;

  width: 34px;
  height: 34px;

  place-items: center;

  color: var(--vl-muted);

  background: transparent;
  border: 0;
  border-radius: 8px;

  transform: translateY(-50%);
}

.password-toggle:hover {
  color: var(--vl-ink);
  background: rgba(113, 129, 107, 0.08);
}

/* Messages */

.message {
  display: flex;
  align-items: center;
  gap: 8px;

  padding: 11px 12px;

  border-radius: 9px;

  font-size: 0.7rem;
  line-height: 1.45;
}

.message-error {
  color: #9a4f3c;

  background: rgba(181, 107, 79, 0.09);

  border: 1px solid rgba(181, 107, 79, 0.16);
}

.message-success {
  color: #52705a;

  background: rgba(102, 133, 104, 0.09);

  border: 1px solid rgba(102, 133, 104, 0.16);
}

/* Button */

.register-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;

  width: 100%;
  min-height: 47px;
  margin-top: 3px;

  color: var(--vl-surface);

  background: var(--vl-sage-dark);

  border: 0;
  border-radius: 10px;

  font-family: inherit;
  font-size: 0.77rem;
  font-weight: 750;

  cursor: pointer;

  box-shadow:
    0 12px 25px rgba(77, 93, 74, 0.16);

  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    opacity 160ms ease;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-1px);

  box-shadow:
    0 15px 30px rgba(77, 93, 74, 0.2);
}

.register-button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 9px;
}

.spinner {
  width: 14px;
  height: 14px;

  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: white;

  border-radius: 50%;

  animation: spin 700ms linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Footer */

.login-prompt {
  margin-top: 22px;

  color: var(--vl-muted);

  font-size: 0.7rem;

  text-align: center;
}

.login-prompt a {
  margin-left: 4px;

  color: var(--vl-sage-dark);

  font-weight: 750;
  text-decoration: none;
}

.login-prompt a:hover {
  text-decoration: underline;
}

.security-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;

  margin-top: 22px;
  padding-top: 18px;

  color: var(--vl-muted);

  border-top: 1px solid var(--vl-border);

  font-size: 0.61rem;

  text-align: center;
}

/* Responsive */

@media (max-width: 600px) {
  .register-header {
    padding: 0 18px;
  }

  .header-status {
    display: none;
  }

  .register-main {
    align-items: flex-start;

    padding: 30px 14px 45px;
  }

  .register-card {
    padding: 25px 20px;

    border-radius: 18px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .register-button,
  .field input {
    transition: none;
  }

  .spinner {
    animation: none;
  }
}
</style>

