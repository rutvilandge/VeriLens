<script setup lang="ts">
import {
  FileSearch,
  Image,
  Link,
  FileText,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Brain,
  CheckCircle2,
  Clock3,
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

type AnalysisListResponse = {
  success: boolean;
  analyses: Analysis[];
  message?: string;
};

type AnalysisContent = {
  id: string;
  analysisId: string;
  type: "TEXT" | "IMAGE" | "SOURCE";
  title: string | null;
  text: string | null;
  sourceUrl: string | null;
  fileUrl: string | null;
  fileName: string | null;
  mimeType: string | null;
  fileSize: number | null;
  createdAt: string;
  updatedAt: string;
};

type ContentsResponse = {
  success: boolean;
  contents: AnalysisContent[];
  message?: string;
};

type Prediction = {
  id: string;
  analysisId: string;
  contentId: string | null;
  prediction: string;
  confidence: number;
  signals?: Record<string, unknown> | null;
  metadata?: Record<string, unknown> | null;
  status:
    | "QUEUED"
    | "PROCESSING"
    | "COMPLETED"
    | "FAILED";
  createdAt: string;
  updatedAt: string;
};

type PredictionsResponse = {
  success: boolean;
  predictions: Prediction[];
  message?: string;
};

type EvidenceItem = AnalysisContent & {
  analysisTitle: string;
  prediction?: Prediction | null;
};

const config = useRuntimeConfig();

const apiBase =
  String(config.public.apiBase || "");

const loading = ref(true);
const error = ref("");

const evidence = ref<EvidenceItem[]>([]);

const searchQuery = ref("");

const selectedType = ref<
  "ALL" | "TEXT" | "IMAGE" | "SOURCE"
>("ALL");

/**
 * ---------------------------------------------------------
 * Fetch all user evidence
 * ---------------------------------------------------------
 */

const fetchEvidence = async () => {
  loading.value = true;
  error.value = "";

  try {
    /**
     * First fetch all investigations owned by the user.
     */
    const analysesResponse =
      await $fetch<AnalysisListResponse>(
        `${apiBase}/api/analyses`,
        {
          method: "GET",
          credentials: "include",
        },
      );

    if (
      !analysesResponse.success ||
      !analysesResponse.analyses
    ) {
      throw new Error(
        analysesResponse.message ||
          "Unable to load investigations.",
      );
    }

    const allEvidence: EvidenceItem[] = [];

    /**
     * Fetch evidence + predictions for every investigation.
     */
    await Promise.all(
      analysesResponse.analyses.map(
        async (analysis) => {
          try {
            /**
             * IMPORTANT:
             * Evidence uses the singular content route.
             */
            const contentsResponse =
              await $fetch<ContentsResponse>(
                `${apiBase}/api/analyses/${analysis.id}/content`,
                {
                  method: "GET",
                  credentials: "include",
                },
              );

            let predictions: Prediction[] = [];

            /**
             * Predictions are optional.
             * If prediction loading fails, evidence still appears.
             */
            try {
              const predictionsResponse =
                await $fetch<PredictionsResponse>(
                  `${apiBase}/api/analyses/${analysis.id}/predictions`,
                  {
                    method: "GET",
                    credentials: "include",
                  },
                );

              if (
                predictionsResponse.success &&
                predictionsResponse.predictions
              ) {
                predictions =
                  predictionsResponse.predictions;
              }
            } catch (predictionError) {
              console.warn(
                `Unable to load predictions for analysis ${analysis.id}:`,
                predictionError,
              );
            }

            if (
              contentsResponse.success &&
              contentsResponse.contents
            ) {
              for (const content of contentsResponse.contents) {
                const prediction =
                  predictions.find(
                    (item) =>
                      item.contentId === content.id,
                  ) || null;

                allEvidence.push({
                  ...content,
                  analysisTitle:
                    analysis.title,
                  prediction,
                });
              }
            }
          } catch (contentError) {
            console.error(
              `Unable to load evidence for analysis ${analysis.id}:`,
              contentError,
            );
          }
        },
      ),
    );

    /**
     * Newest evidence first.
     */
    allEvidence.sort(
      (a, b) =>
        new Date(b.createdAt).getTime() -
        new Date(a.createdAt).getTime(),
    );

    evidence.value = allEvidence;
  } catch (err: any) {
    console.error(
      "Evidence page error:",
      err,
    );

    error.value =
      err?.data?.message ||
      err?.message ||
      "Unable to load evidence.";
  } finally {
    loading.value = false;
  }
};

/**
 * ---------------------------------------------------------
 * Filtered evidence
 * ---------------------------------------------------------
 */

const filteredEvidence = computed(() => {
  const query =
    searchQuery.value.trim().toLowerCase();

  return evidence.value.filter((item) => {
    const matchesType =
      selectedType.value === "ALL" ||
      item.type === selectedType.value;

    if (!matchesType) {
      return false;
    }

    if (!query) {
      return true;
    }

    return Boolean(
      item.title
        ?.toLowerCase()
        .includes(query) ||
        item.text
          ?.toLowerCase()
          .includes(query) ||
        item.sourceUrl
          ?.toLowerCase()
          .includes(query) ||
        item.fileName
          ?.toLowerCase()
          .includes(query) ||
        item.analysisTitle
          .toLowerCase()
          .includes(query) ||
        item.prediction?.prediction
          ?.toLowerCase()
          .includes(query),
    );
  });
});

/**
 * ---------------------------------------------------------
 * Counts
 * ---------------------------------------------------------
 */

const textCount = computed(
  () =>
    evidence.value.filter(
      (item) => item.type === "TEXT",
    ).length,
);

const imageCount = computed(
  () =>
    evidence.value.filter(
      (item) => item.type === "IMAGE",
    ).length,
);

const sourceCount = computed(
  () =>
    evidence.value.filter(
      (item) => item.type === "SOURCE",
    ).length,
);

const predictedCount = computed(
  () =>
    evidence.value.filter(
      (item) =>
        item.prediction?.status === "COMPLETED",
    ).length,
);

/**
 * ---------------------------------------------------------
 * Helpers
 * ---------------------------------------------------------
 */

const formatDate = (date: string) => {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
};

const formatFileSize = (
  size: number | null,
) => {
  if (!size) {
    return "";
  }

  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};

const getImageUrl = (
  fileUrl: string | null,
) => {
  if (!fileUrl) {
    return "";
  }

  if (
    fileUrl.startsWith("http://") ||
    fileUrl.startsWith("https://")
  ) {
    return fileUrl;
  }

  return `${apiBase}${fileUrl}`;
};

const getTypeLabel = (
  type: AnalysisContent["type"],
) => {
  switch (type) {
    case "TEXT":
      return "Text";

    case "IMAGE":
      return "Image";

    case "SOURCE":
      return "Source";

    default:
      return type;
  }
};

const formatConfidence = (
  confidence: number,
) => {
  return `${Math.round(confidence * 100)}%`;
};

const getPredictionLabel = (
  prediction: Prediction | null | undefined,
) => {
  if (!prediction) {
    return "Not analyzed";
  }

  return prediction.prediction
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
};

/**
 * ---------------------------------------------------------
 * Initial load
 * ---------------------------------------------------------
 */

await fetchEvidence();
</script>

<template>
  <main class="dashboard-content">
    <div class="mb-6"><DashboardBackToDashboard /></div>
    <!-- Header -->
    <section class="mb-10">
      <div class="eyebrow">
        <FileSearch :size="13" />

        Evidence intelligence
      </div>

      <div
        class="mt-4 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"
      >
        <div>
          <h1
            class="text-4xl font-semibold tracking-[-0.045em] sm:text-5xl"
          >
            Evidence
          </h1>

          <p
            class="mt-4 max-w-2xl text-base leading-7 text-[var(--vl-muted)]"
          >
            Review all text, image, and source evidence
            collected across your investigations.
          </p>
        </div>

        <button
          type="button"
          class="inline-flex h-11 w-fit items-center gap-2 rounded-xl border border-[var(--vl-border)] bg-[var(--vl-surface)] px-4 text-sm font-semibold text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)] disabled:opacity-50"
          :disabled="loading"
          @click="fetchEvidence"
        >
          <RefreshCw
            :size="15"
            :class="loading ? 'animate-spin' : ''"
          />

          Refresh
        </button>
      </div>
    </section>

    <!-- Error -->
    <section
      v-if="error"
      class="rounded-[28px] border border-[var(--vl-terracotta)]/25 bg-[var(--vl-terracotta)]/5 p-8"
    >
      <h2 class="text-lg font-semibold">
        Unable to load evidence
      </h2>

      <p
        class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
      >
        {{ error }}
      </p>

      <button
        type="button"
        class="mt-6 inline-flex h-11 items-center gap-2 rounded-xl bg-[var(--vl-sage-dark)] px-5 text-sm font-semibold text-white"
        @click="fetchEvidence"
      >
        <RefreshCw :size="15" />

        Try again
      </button>
    </section>

    <template v-else>
      <!-- Stats -->
      <section
        class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        <!-- Total -->
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
          >
            <FileSearch :size="18" />
          </div>

          <p
            class="mt-5 text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
          >
            Total evidence
          </p>

          <p
            class="mt-1 text-3xl font-semibold tracking-[-0.03em]"
          >
            {{ evidence.length }}
          </p>
        </div>

        <!-- Text -->
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
          >
            <FileText :size="18" />
          </div>

          <p
            class="mt-5 text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
          >
            Text
          </p>

          <p
            class="mt-1 text-3xl font-semibold tracking-[-0.03em]"
          >
            {{ textCount }}
          </p>
        </div>

        <!-- Images -->
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]"
          >
            <Image :size="18" />
          </div>

          <p
            class="mt-5 text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
          >
            Images
          </p>

          <p
            class="mt-1 text-3xl font-semibold tracking-[-0.03em]"
          >
            {{ imageCount }}
          </p>
        </div>

        <!-- Sources -->
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
          >
            <Link :size="18" />
          </div>

          <p
            class="mt-5 text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
          >
            Sources
          </p>

          <p
            class="mt-1 text-3xl font-semibold tracking-[-0.03em]"
          >
            {{ sourceCount }}
          </p>
        </div>
      </section>

      <!-- Intelligence summary -->
      <section
        class="mt-6 rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6"
      >
        <div
          class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="flex items-start gap-4">
            <div
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
            >
              <Brain :size="19" />
            </div>

            <div>
              <p class="text-sm font-semibold">
                Evidence intelligence
              </p>

              <p
                class="mt-1 text-xs leading-5 text-[var(--vl-muted)]"
              >
                Predictions generated by the VeriLens
                analysis engine.
              </p>
            </div>
          </div>

          <div
            class="flex items-center gap-2 text-sm font-semibold text-[var(--vl-sage-dark)]"
          >
            <CheckCircle2 :size="16" />

            {{ predictedCount }} analyzed
          </div>
        </div>
      </section>

      <!-- Search / Filters -->
      <section
        class="mt-6 rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5 sm:p-6"
      >
        <div
          class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"
        >
          <div class="relative w-full lg:max-w-md">
            <FileSearch
              :size="17"
              class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[var(--vl-muted)]"
            />

            <input
              v-model="searchQuery"
              type="search"
              placeholder="Search evidence..."
              class="h-12 w-full rounded-xl border border-[var(--vl-border)] bg-white/70 pl-11 pr-4 text-sm outline-none transition focus:border-[var(--vl-sage-dark)]"
            />
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="rounded-xl px-4 py-2.5 text-xs font-semibold transition-colors"
              :class="
                selectedType === 'ALL'
                  ? 'bg-[var(--vl-sage-dark)] text-white'
                  : 'border border-[var(--vl-border)] bg-white/60 text-[var(--vl-muted)] hover:text-[var(--vl-ink)]'
              "
              @click="selectedType = 'ALL'"
            >
              All
            </button>

            <button
              type="button"
              class="rounded-xl px-4 py-2.5 text-xs font-semibold transition-colors"
              :class="
                selectedType === 'TEXT'
                  ? 'bg-[var(--vl-sage-dark)] text-white'
                  : 'border border-[var(--vl-border)] bg-white/60 text-[var(--vl-muted)] hover:text-[var(--vl-ink)]'
              "
              @click="selectedType = 'TEXT'"
            >
              Text
            </button>

            <button
              type="button"
              class="rounded-xl px-4 py-2.5 text-xs font-semibold transition-colors"
              :class="
                selectedType === 'IMAGE'
                  ? 'bg-[var(--vl-terracotta)] text-white'
                  : 'border border-[var(--vl-border)] bg-white/60 text-[var(--vl-muted)] hover:text-[var(--vl-ink)]'
              "
              @click="selectedType = 'IMAGE'"
            >
              Images
            </button>

            <button
              type="button"
              class="rounded-xl px-4 py-2.5 text-xs font-semibold transition-colors"
              :class="
                selectedType === 'SOURCE'
                  ? 'bg-[var(--vl-sage-dark)] text-white'
                  : 'border border-[var(--vl-border)] bg-white/60 text-[var(--vl-muted)] hover:text-[var(--vl-ink)]'
              "
              @click="selectedType = 'SOURCE'"
            >
              Sources
            </button>
          </div>
        </div>
      </section>

      <!-- Loading -->
      <section
        v-if="loading"
        class="mt-6 grid gap-4"
      >
        <div
          v-for="item in 3"
          :key="item"
          class="animate-pulse rounded-[24px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6"
        >
          <div
            class="h-4 w-20 rounded bg-black/5"
          />

          <div
            class="mt-5 h-5 w-2/3 rounded bg-black/5"
          />

          <div
            class="mt-3 h-4 w-full rounded bg-black/5"
          />

          <div
            class="mt-3 h-4 w-1/2 rounded bg-black/5"
          />
        </div>
      </section>

      <!-- Empty -->
      <section
        v-else-if="filteredEvidence.length === 0"
        class="mt-6 rounded-[28px] border border-dashed border-[var(--vl-border)] bg-[var(--vl-surface)] p-12 text-center"
      >
        <div
          class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
        >
          <FileSearch :size="24" />
        </div>

        <h2
          class="mt-5 text-lg font-semibold"
        >
          {{
            evidence.length === 0
              ? "No evidence yet"
              : "No matching evidence"
          }}
        </h2>

        <p
          class="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--vl-muted)]"
        >
          {{
            evidence.length === 0
              ? "Add text, images, or sources from an investigation workspace to start building your evidence base."
              : "Try changing your search or evidence type filter."
          }}
        </p>

        <NuxtLink
          to="/dashboard/analyses"
          class="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[var(--vl-sage-dark)]"
        >
          Open investigations

          <ArrowRight :size="15" />
        </NuxtLink>
      </section>

      <!-- Evidence -->
      <section
        v-else
        class="mt-6 space-y-4"
      >
        <article
          v-for="item in filteredEvidence"
          :key="item.id"
          class="overflow-hidden rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] transition-all hover:border-[var(--vl-sage-dark)]/25 hover:shadow-[0_14px_35px_rgba(32,35,31,0.06)]"
        >
          <div class="p-6">
            <div
              class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between"
            >
              <div class="min-w-0 flex-1">
                <!-- Type -->
                <div
                  class="flex flex-wrap items-center gap-2"
                >
                  <span
                    class="rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em]"
                    :class="
                      item.type === 'IMAGE'
                        ? 'bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]'
                        : 'bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]'
                    "
                  >
                    {{ getTypeLabel(item.type) }}
                  </span>

                  <span
                    class="text-xs text-[var(--vl-muted)]"
                  >
                    {{ formatDate(item.createdAt) }}
                  </span>
                </div>

                <!-- Title -->
                <h2
                  class="mt-4 text-lg font-semibold tracking-[-0.02em]"
                >
                  {{
                    item.title ||
                    item.fileName ||
                    "Untitled evidence"
                  }}
                </h2>

                <!-- Investigation -->
                <NuxtLink
                  :to="`/dashboard/analyses/${item.analysisId}`"
                  class="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--vl-sage-dark)] hover:underline"
                >
                  {{ item.analysisTitle }}

                  <ArrowRight :size="12" />
                </NuxtLink>

                <!-- Text -->
                <p
                  v-if="item.text"
                  class="mt-5 whitespace-pre-wrap text-sm leading-7 text-[var(--vl-muted)]"
                >
                  {{ item.text }}
                </p>

                <!-- Source -->
                <a
                  v-if="item.sourceUrl"
                  :href="item.sourceUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="mt-5 block break-all text-sm font-medium text-[var(--vl-sage-dark)] underline-offset-4 hover:underline"
                >
                  {{ item.sourceUrl }}
                </a>

                <!-- Image -->
                <div
                  v-if="
                    item.type === 'IMAGE' &&
                    item.fileUrl
                  "
                  class="mt-5 overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-black/5"
                >
                  <img
                    :src="getImageUrl(item.fileUrl)"
                    :alt="
                      item.title ||
                      item.fileName ||
                      'Evidence image'
                    "
                    class="max-h-[420px] w-full object-contain"
                    loading="lazy"
                  />

                  <div
                    class="flex items-center justify-between gap-3 border-t border-[var(--vl-border)] px-4 py-3"
                  >
                    <span
                      class="truncate text-xs text-[var(--vl-muted)]"
                    >
                      {{
                        item.fileName ||
                        "Uploaded image"
                      }}
                    </span>

                    <span
                      v-if="item.fileSize"
                      class="shrink-0 text-xs text-[var(--vl-muted)]"
                    >
                      {{
                        formatFileSize(
                          item.fileSize,
                        )
                      }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Intelligence -->
              <div
                class="shrink-0 rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-sage)]/5 p-4 lg:w-52"
              >
                <div
                  class="flex items-center justify-between"
                >
                  <div
                    class="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
                  >
                    <Sparkles :size="16" />
                  </div>

                  <CheckCircle2
                    v-if="
                      item.prediction?.status ===
                      'COMPLETED'
                    "
                    :size="16"
                    class="text-[var(--vl-sage-dark)]"
                  />

                  <Clock3
                    v-else
                    :size="16"
                    class="text-[var(--vl-muted)]"
                  />
                </div>

                <p
                  class="mt-3 text-xs font-semibold"
                >
                  Intelligence
                </p>

                <template
                  v-if="item.prediction"
                >
                  <p
                    class="mt-2 text-sm font-semibold leading-5"
                  >
                    {{
                      getPredictionLabel(
                        item.prediction,
                      )
                    }}
                  </p>

                  <div
                    class="mt-3 flex items-center justify-between text-[11px]"
                  >
                    <span
                      class="text-[var(--vl-muted)]"
                    >
                      Confidence
                    </span>

                    <span
                      class="font-semibold text-[var(--vl-sage-dark)]"
                    >
                      {{
                        formatConfidence(
                          item.prediction
                            .confidence,
                        )
                      }}
                    </span>
                  </div>

                  <div
                    class="mt-2 h-1.5 overflow-hidden rounded-full bg-black/5"
                  >
                    <div
                      class="h-full rounded-full bg-[var(--vl-sage-dark)] transition-all"
                      :style="{
                        width: `${Math.round(
                          item.prediction
                            .confidence * 100,
                        )}%`,
                      }"
                    />
                  </div>
                </template>

                <template v-else>
                  <p
                    class="mt-1 text-[11px] leading-5 text-[var(--vl-muted)]"
                  >
                    This evidence has not been
                    analyzed by the prediction engine
                    yet.
                  </p>
                </template>
              </div>
            </div>
          </div>
        </article>
      </section>
    </template>
  </main>
</template>


