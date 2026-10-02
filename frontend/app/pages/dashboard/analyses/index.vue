<script setup lang="ts">
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  FileSearch,
  Loader2,
  Plus,
  Search,
  Trash2,
  XCircle,
} from "lucide-vue-next";

type AnalysisStatus =
  | "DRAFT"
  | "QUEUED"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED";

type Analysis = {
  id: string;
  title: string;
  status: AnalysisStatus;
  createdAt: string;
  updatedAt: string;
};

type AnalysesResponse = {
  success: boolean;
  analyses: Analysis[];
  message?: string;
};

const config = useRuntimeConfig();

const apiBase =
  String(config.public.apiBase || "");

const analyses = ref<Analysis[]>([]);

const loading = ref(true);

const error = ref("");

const searchQuery = ref("");

const route = useRoute();
const allowedStatuses: AnalysisStatus[] = ["DRAFT", "QUEUED", "PROCESSING", "COMPLETED", "FAILED"];
const activeStatus = ref<"ALL" | AnalysisStatus>(allowedStatuses.includes(route.query.status as AnalysisStatus) ? route.query.status as AnalysisStatus : "ALL");
watch(() => route.query.status, (value) => { activeStatus.value = allowedStatuses.includes(value as AnalysisStatus) ? value as AnalysisStatus : "ALL"; });

const deletingId = ref<string | null>(null);

const statusFilters = [
  {
    label: "All",
    value: "ALL" as const,
  },
  {
    label: "Draft",
    value: "DRAFT" as const,
  },
  {
    label: "Queued",
    value: "QUEUED" as const,
  },
  {
    label: "Processing",
    value: "PROCESSING" as const,
  },
  {
    label: "Completed",
    value: "COMPLETED" as const,
  },
  {
    label: "Failed",
    value: "FAILED" as const,
  },
];

const fetchAnalyses = async () => {
  loading.value = true;
  error.value = "";

  try {
    const response =
      await $fetch<AnalysesResponse>(
        `${apiBase}/api/analyses`,
        {
          method: "GET",
          credentials: "include",
        },
      );

    if (!response.success) {
      throw new Error(
        response.message ||
          "Unable to load investigations.",
      );
    }

    analyses.value = response.analyses;
  } catch (err: any) {
    console.error(
      "Investigation list error:",
      err,
    );

    error.value =
      err?.data?.message ||
      err?.message ||
      "Unable to load your investigations.";
  } finally {
    loading.value = false;
  }
};

const filteredAnalyses = computed(() => {
  const query =
    searchQuery.value.trim().toLowerCase();

  return analyses.value.filter((analysis) => {
    const matchesSearch =
      !query ||
      analysis.title
        .toLowerCase()
        .includes(query);

    const matchesStatus =
      activeStatus.value === "ALL" ||
      analysis.status === activeStatus.value;

    return matchesSearch && matchesStatus;
  });
});

const totalCount = computed(
  () => analyses.value.length,
);

const completedCount = computed(
  () =>
    analyses.value.filter(
      (analysis) =>
        analysis.status === "COMPLETED",
    ).length,
);

const processingCount = computed(
  () =>
    analyses.value.filter(
      (analysis) =>
        analysis.status === "PROCESSING",
    ).length,
);

const draftCount = computed(
  () =>
    analyses.value.filter(
      (analysis) =>
        analysis.status === "DRAFT",
    ).length,
);

const getStatusLabel = (
  status: AnalysisStatus,
) => {
  switch (status) {
    case "DRAFT":
      return "Draft";

    case "QUEUED":
      return "Queued";

    case "PROCESSING":
      return "Processing";

    case "COMPLETED":
      return "Completed";

    case "FAILED":
      return "Failed";

    default:
      return status;
  }
};

const getStatusClass = (
  status: AnalysisStatus,
) => {
  switch (status) {
    case "COMPLETED":
      return "bg-[var(--vl-sage)]/12 text-[var(--vl-sage-dark)]";

    case "PROCESSING":
      return "bg-blue-500/10 text-blue-700";

    case "QUEUED":
      return "bg-amber-500/10 text-amber-700";

    case "FAILED":
      return "bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]";

    case "DRAFT":
    default:
      return "bg-black/5 text-[var(--vl-muted)]";
  }
};

const getStatusIcon = (
  status: AnalysisStatus,
) => {
  switch (status) {
    case "COMPLETED":
      return CheckCircle2;

    case "PROCESSING":
      return Loader2;

    case "QUEUED":
      return Clock3;

    case "FAILED":
      return XCircle;

    case "DRAFT":
    default:
      return FileSearch;
  }
};

const formatDate = (date: string) => {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
};

const openAnalysis = async (
  id: string,
) => {
  await navigateTo(
    `/dashboard/analyses/${id}`,
  );
};

const deleteAnalysis = async (
  analysis: Analysis,
) => {
  if (deletingId.value) {
    return;
  }

  const confirmed = window.confirm(
    `Delete "${analysis.title}"? This action cannot be undone.`,
  );

  if (!confirmed) {
    return;
  }

  deletingId.value = analysis.id;

  try {
    await $fetch(
      `${apiBase}/api/analyses/${analysis.id}`,
      {
        method: "DELETE",
        credentials: "include",
      },
    );

    analyses.value = analyses.value.filter(
      (item) => item.id !== analysis.id,
    );
  } catch (err: any) {
    console.error(
      "Delete analysis error:",
      err,
    );

    window.alert(
      err?.data?.message ||
        "Unable to delete this investigation.",
    );
  } finally {
    deletingId.value = null;
  }
};

await fetchAnalyses();
</script>

<template>
  <main class="dashboard-content">
    <div class="mb-6"><DashboardBackToDashboard /></div>
    <!-- Header -->
    <section class="mb-10">
      <div
        class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between"
      >
        <div>
          <div class="eyebrow">
            <FileSearch :size="13" />
            Investigation management
          </div>

          <h1
            class="mt-4 text-4xl font-semibold tracking-[-0.045em] sm:text-5xl"
          >
            Investigations.
          </h1>

          <p
            class="mt-4 max-w-2xl text-base leading-7 text-[var(--vl-muted)]"
          >
            Review, search, and manage every
            investigation in your VeriLens workspace.
          </p>
        </div>

        <NuxtLink
          to="/dashboard/analyses/new"
          class="inline-flex h-12 shrink-0 items-center justify-center gap-2 rounded-xl bg-[var(--vl-sage-dark)] px-6 text-sm font-semibold text-white shadow-[0_12px_28px_rgba(77,93,74,0.18)] transition-all hover:-translate-y-0.5 hover:bg-[var(--vl-ink)]"
        >
          <Plus :size="17" />
          Start Analysis
        </NuxtLink>
      </div>
    </section>

    <!-- Stats -->
    <section
      class="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
    >
      <div
        class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
      >
        <p
          class="text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
        >
          Total
        </p>

        <p
          class="mt-3 text-3xl font-semibold tracking-[-0.04em]"
        >
          {{ totalCount }}
        </p>

        <p
          class="mt-1 text-xs text-[var(--vl-muted)]"
        >
          All investigations
        </p>
      </div>

      <div
        class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
      >
        <p
          class="text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
        >
          Completed
        </p>

        <p
          class="mt-3 text-3xl font-semibold tracking-[-0.04em]"
        >
          {{ completedCount }}
        </p>

        <p
          class="mt-1 text-xs text-[var(--vl-muted)]"
        >
          Finished analyses
        </p>
      </div>

      <div
        class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
      >
        <p
          class="text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
        >
          Processing
        </p>

        <p
          class="mt-3 text-3xl font-semibold tracking-[-0.04em]"
        >
          {{ processingCount }}
        </p>

        <p
          class="mt-1 text-xs text-[var(--vl-muted)]"
        >
          Active pipelines
        </p>
      </div>

      <div
        class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
      >
        <p
          class="text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
        >
          Drafts
        </p>

        <p
          class="mt-3 text-3xl font-semibold tracking-[-0.04em]"
        >
          {{ draftCount }}
        </p>

        <p
          class="mt-1 text-xs text-[var(--vl-muted)]"
        >
          Investigations in progress
        </p>
      </div>
    </section>

    <!-- Main -->
    <section
      class="rounded-[28px] border border-[var(--vl-border)] bg-[rgba(250,248,242,0.72)] p-5 shadow-[0_20px_70px_rgba(32,35,31,0.07)] backdrop-blur-xl sm:p-7"
    >
      <!-- Toolbar -->
      <div
        class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between"
      >
        <!-- Search -->
        <div class="relative w-full xl:max-w-md">
          <Search
            :size="17"
            class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[var(--vl-muted)]"
          />

          <input
            v-model="searchQuery"
            type="search"
            placeholder="Search investigations..."
            class="h-12 w-full rounded-xl border border-[var(--vl-border)] bg-[var(--vl-surface)] pl-11 pr-4 text-sm text-[var(--vl-ink)] outline-none transition-all placeholder:text-[var(--vl-muted)]/60 focus:border-[var(--vl-sage-dark)]/50 focus:ring-4 focus:ring-[var(--vl-sage)]/10"
          />
        </div>

        <!-- Filters -->
        <div
          class="flex flex-wrap gap-2"
        >
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            type="button"
            class="rounded-xl px-4 py-2.5 text-xs font-semibold transition-all"
            :class="
              activeStatus === filter.value
                ? 'bg-[var(--vl-sage-dark)] text-white shadow-sm'
                : 'border border-[var(--vl-border)] bg-[var(--vl-surface)] text-[var(--vl-muted)] hover:text-[var(--vl-ink)]'
            "
            @click="activeStatus = filter.value"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div
        v-if="loading"
        class="mt-8 space-y-3"
      >
        <div
          v-for="index in 4"
          :key="index"
          class="h-24 animate-pulse rounded-2xl bg-black/5"
        />
      </div>

      <!-- Error -->
      <div
        v-else-if="error"
        class="mt-8 rounded-2xl border border-[var(--vl-terracotta)]/25 bg-[var(--vl-terracotta)]/5 p-6"
      >
        <h2 class="text-base font-semibold">
          Unable to load investigations
        </h2>

        <p
          class="mt-2 text-sm text-[var(--vl-muted)]"
        >
          {{ error }}
        </p>

        <button
          type="button"
          class="mt-5 inline-flex h-10 items-center justify-center rounded-xl bg-[var(--vl-sage-dark)] px-4 text-sm font-semibold text-white"
          @click="fetchAnalyses"
        >
          Try again
        </button>
      </div>

      <!-- Empty -->
      <div
        v-else-if="filteredAnalyses.length === 0"
        class="mt-8 rounded-2xl border border-dashed border-[var(--vl-border)] bg-[var(--vl-surface)] p-10 text-center"
      >
        <div
          class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
        >
          <FileSearch :size="21" />
        </div>

        <h2
          class="mt-5 text-lg font-semibold"
        >
          {{
            searchQuery ||
            activeStatus !== "ALL"
              ? "No matching investigations"
              : "No investigations yet"
          }}
        </h2>

        <p
          class="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--vl-muted)]"
        >
          {{
            searchQuery ||
            activeStatus !== "ALL"
              ? "Try another search or status filter."
              : "Create your first investigation to begin working with VeriLens."
          }}
        </p>

        <NuxtLink
          v-if="
            !searchQuery &&
            activeStatus === 'ALL'
          "
          to="/dashboard/analyses/new"
          class="mt-6 inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-[var(--vl-sage-dark)] px-5 text-sm font-semibold text-white"
        >
          <Plus :size="16" />
          Create Analysis
        </NuxtLink>
      </div>

      <!-- List -->
      <div
        v-else
        class="mt-8 overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)]"
      >
        <div
          v-for="(analysis, index) in filteredAnalyses"
          :key="analysis.id"
          class="group flex flex-col gap-5 p-5 transition-colors hover:bg-[var(--vl-sage)]/4 sm:flex-row sm:items-center sm:justify-between"
          :class="
            index !== filteredAnalyses.length - 1
              ? 'border-b border-[var(--vl-border)]'
              : ''
          "
        >
          <button
            type="button"
            class="min-w-0 flex-1 text-left"
            @click="openAnalysis(analysis.id)"
          >
            <div
              class="flex items-start gap-4"
            >
              <div
                class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
              >
                <FileSearch :size="18" />
              </div>

              <div class="min-w-0">
                <div
                  class="flex flex-wrap items-center gap-2"
                >
                  <h2
                    class="truncate text-sm font-semibold transition-colors group-hover:text-[var(--vl-sage-dark)]"
                  >
                    {{ analysis.title }}
                  </h2>

                  <span
                    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-semibold"
                    :class="
                      getStatusClass(
                        analysis.status,
                      )
                    "
                  >
                    <component
                      :is="
                        getStatusIcon(
                          analysis.status,
                        )
                      "
                      :size="11"
                      :class="
                        analysis.status ===
                        'PROCESSING'
                          ? 'animate-spin'
                          : ''
                      "
                    />

                    {{
                      getStatusLabel(
                        analysis.status,
                      )
                    }}
                  </span>
                </div>

                <p
                  class="mt-1 text-xs text-[var(--vl-muted)]"
                >
                  Created
                  {{ formatDate(analysis.createdAt) }}
                </p>
              </div>
            </div>
          </button>

          <div
            class="flex shrink-0 items-center gap-2 sm:pl-4"
          >
            <button
              type="button"
              class="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-[var(--vl-border)] px-4 text-xs font-semibold text-[var(--vl-muted)] transition-colors hover:border-[var(--vl-sage-dark)]/30 hover:text-[var(--vl-ink)]"
              @click="openAnalysis(analysis.id)"
            >
              Open
              <ArrowRight :size="14" />
            </button>

            <button
              type="button"
              :disabled="
                deletingId === analysis.id
              "
              class="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--vl-border)] text-[var(--vl-muted)] transition-colors hover:border-[var(--vl-terracotta)]/30 hover:text-[var(--vl-terracotta)] disabled:cursor-not-allowed disabled:opacity-50"
              title="Delete investigation"
              @click="deleteAnalysis(analysis)"
            >
              <Loader2
                v-if="
                  deletingId === analysis.id
                "
                :size="15"
                class="animate-spin"
              />

              <Trash2
                v-else
                :size="15"
              />
            </button>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>


