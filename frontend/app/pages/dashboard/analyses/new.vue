<script setup lang="ts">
import {
  ArrowLeft,
  FileText,
  Image,
  Link,
  Sparkles,
} from "lucide-vue-next";

const config = useRuntimeConfig();

const apiBase =
  String(config.public.apiBase || "");

const title = ref("");

const loading = ref(false);

const error = ref("");

const createAnalysis = async () => {
  if (loading.value) {
    return;
  }

  error.value = "";

  const trimmedTitle = title.value.trim();

  if (!trimmedTitle) {
    error.value = "Please enter an analysis title.";
    return;
  }

  loading.value = true;

  try {
    const response = await $fetch<{
      success: boolean;
      message: string;
      analysis: {
        id: string;
        title: string;
        status: string;
      };
    }>(`${apiBase}/api/analyses`, {
      method: "POST",

      credentials: "include",

      body: {
        title: trimmedTitle,
      },
    });

    if (!response.success || !response.analysis) {
      throw new Error(
        response.message ||
          "Unable to create analysis",
      );
    }

    await navigateTo(
      `/dashboard/analyses/${response.analysis.id}`,
    );
  } catch (err: any) {
    console.error(
      "Create analysis error:",
      err,
    );

    error.value =
      err?.data?.message ||
      err?.message ||
      "Unable to create analysis. Please try again.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <main class="dashboard-content">
    <!-- Header -->
    <section class="mb-10">
      <NuxtLink
        to="/dashboard"
        class="mb-6 inline-flex items-center gap-2 text-sm text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)]"
      >
        <ArrowLeft :size="16" />

        Back to dashboard
      </NuxtLink>

      <div class="eyebrow">
        <Sparkles :size="13" />

        New investigation
      </div>

      <h1
        class="mt-4 text-4xl font-semibold tracking-[-0.045em] sm:text-5xl"
      >
        Start an analysis.
      </h1>

      <p
        class="mt-4 max-w-2xl text-base leading-7 text-[var(--vl-muted)]"
      >
        Create an investigation and bring content
        into VeriLens for multimodal analysis,
        evidence retrieval, and explainable
        intelligence.
      </p>
    </section>

    <!-- Main card -->
    <section
      class="max-w-4xl rounded-[28px] border border-[var(--vl-border)] bg-[rgba(250,248,242,0.72)] p-6 shadow-[0_20px_70px_rgba(32,35,31,0.07)] backdrop-blur-xl sm:p-8"
    >
      <!-- Title -->
      <div>
        <label
          for="analysis-title"
          class="mb-2 block text-sm font-semibold"
        >
          Analysis title
        </label>

        <p
          class="mb-4 text-sm leading-6 text-[var(--vl-muted)]"
        >
          Give this investigation a clear name so you
          can find it later.
        </p>

        <input
          id="analysis-title"
          v-model="title"
          type="text"
          maxlength="200"
          placeholder="e.g. Viral claim investigation"
          :disabled="loading"
          class="h-14 w-full rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] px-5 text-sm text-[var(--vl-ink)] outline-none transition-all placeholder:text-[var(--vl-muted)]/60 focus:border-[var(--vl-sage-dark)]/50 focus:ring-4 focus:ring-[var(--vl-sage)]/10 disabled:cursor-not-allowed disabled:opacity-60"
          @keydown.enter="createAnalysis"
        />
      </div>

      <!-- Error -->
      <div
        v-if="error"
        class="mt-5 rounded-2xl border border-[var(--vl-terracotta)]/25 bg-[var(--vl-terracotta)]/8 px-4 py-3 text-sm text-[var(--vl-terracotta)]"
      >
        {{ error }}
      </div>

      <!-- Content sources -->
      <div class="mt-10">
        <p
          class="text-sm font-semibold"
        >
          What will you investigate?
        </p>

        <p
          class="mt-1 text-sm text-[var(--vl-muted)]"
        >
          Content ingestion will be connected in the
          next workspace phase.
        </p>

        <div
          class="mt-5 grid gap-4 sm:grid-cols-3"
        >
          <div
            class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
          >
            <div
              class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
            >
              <FileText :size="19" />
            </div>

            <h3 class="mt-4 text-sm font-semibold">
              Text
            </h3>

            <p
              class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
            >
              Articles, claims, documents, and written
              content.
            </p>
          </div>

          <div
            class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
          >
            <div
              class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]"
            >
              <Image :size="19" />
            </div>

            <h3 class="mt-4 text-sm font-semibold">
              Images
            </h3>

            <p
              class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
            >
              Visual content for computer vision and
              authenticity analysis.
            </p>
          </div>

          <div
            class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
          >
            <div
              class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
            >
              <Link :size="19" />
            </div>

            <h3 class="mt-4 text-sm font-semibold">
              Sources
            </h3>

            <p
              class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
            >
              Web sources and evidence for claim
              verification.
            </p>
          </div>
        </div>
      </div>

      <!-- Action -->
      <div
        class="mt-10 flex flex-col-reverse gap-3 border-t border-[var(--vl-border)] pt-6 sm:flex-row sm:items-center sm:justify-end"
      >
        <NuxtLink
          to="/dashboard"
          class="inline-flex h-12 items-center justify-center rounded-xl px-5 text-sm font-medium text-[var(--vl-muted)] transition-colors hover:bg-[var(--vl-sage)]/8 hover:text-[var(--vl-ink)]"
        >
          Cancel
        </NuxtLink>

        <button
          type="button"
          :disabled="loading"
          class="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-[var(--vl-sage-dark)] px-6 text-sm font-semibold text-white shadow-[0_12px_28px_rgba(77,93,74,0.18)] transition-all hover:-translate-y-0.5 hover:bg-[var(--vl-ink)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
          @click="createAnalysis"
        >
          <Sparkles :size="17" />

          {{
            loading
              ? "Creating..."
              : "Create Analysis"
          }}
        </button>
      </div>
    </section>
  </main>
</template>

