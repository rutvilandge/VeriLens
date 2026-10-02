<script setup lang="ts">
import {
  ArrowLeft,
  CheckCircle2,
  Clock3,
  FileSearch,
  Image,
  Link,
  Loader2,
  MoreHorizontal,
  Sparkles,
  Zap,
} from "lucide-vue-next";

type AnalysisStatus =
  | "DRAFT"
  | "QUEUED"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED";

type PredictionStatus =
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

type AnalysisResponse = {
  success: boolean;
  analysis: Analysis;
  message?: string;
};

type ContentResponse = {
  success: boolean;
  message?: string;
  content?: unknown;
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
  modelId: string | null;
  modelVersionId: string | null;

  prediction: string;
  confidence: number;

  signals: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;

  status: PredictionStatus;

  createdAt: string;
  updatedAt: string;

  content?: AnalysisContent | null;

  model?: {
    id: string;
    name: string;
    slug: string;
    type: string;
  } | null;

  modelVersion?: {
    id: string;
    version: string;
    description: string | null;
  } | null;
};

type PredictionsResponse = {
  success: boolean;
  predictions: Prediction[];
  message?: string;
};

type PredictionResponse = {
  success: boolean;
  prediction?: Prediction;
  message?: string;
};

const route = useRoute();
const config = useRuntimeConfig();

const apiBase =
  String(config.public.apiBase || "");

const analysis = ref<Analysis | null>(null);

const loading = ref(true);

const error = ref("");

/**
 * ---------------------------------------------------------
 * Saved Evidence State
 * ---------------------------------------------------------
 */

const contents = ref<AnalysisContent[]>([]);

const contentsLoading = ref(true);

const contentsError = ref("");

/**
 * ---------------------------------------------------------
 * Prediction State
 * ---------------------------------------------------------
 */

const predictions = ref<Prediction[]>([]);

const predictionsLoading = ref(true);

const predictionsError = ref("");

const runningPrediction = ref<
  Record<string, boolean>
>({});

const predictionErrors = ref<Record<string, string>>({});
const runningAll = ref(false);

/**
 * ---------------------------------------------------------
 * Add Text State
 * ---------------------------------------------------------
 */

const showTextModal = ref(false);

const textTitle = ref("");

const textContent = ref("");

const savingText = ref(false);

const textError = ref("");

/**
 * ---------------------------------------------------------
 * Add Image State
 * ---------------------------------------------------------
 */

const showImageModal = ref(false);

const imageTitle = ref("");

const selectedImage = ref<File | null>(null);

const imagePreview = ref("");

const savingImage = ref(false);

const imageError = ref("");

const imageInput =
  ref<HTMLInputElement | null>(null);

/**
 * ---------------------------------------------------------
 * Add Source State
 * ---------------------------------------------------------
 */

const showSourceModal = ref(false);

const sourceTitle = ref("");

const sourceUrl = ref("");

const savingSource = ref(false);

const sourceError = ref("");

/**
 * ---------------------------------------------------------
 * Analysis Status
 * ---------------------------------------------------------
 */

const statusLabel = computed(() => {
  if (!analysis.value) {
    return "Loading";
  }

  switch (analysis.value.status) {
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
      return analysis.value.status;
  }
});

const statusClass = computed(() => {
  if (!analysis.value) {
    return "";
  }

  switch (analysis.value.status) {
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
});

const formattedCreatedAt = computed(() => {
  if (!analysis.value) {
    return "";
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(
    new Date(analysis.value.createdAt),
  );
});

/**
 * ---------------------------------------------------------
 * Prediction Helpers
 * ---------------------------------------------------------
 */

const predictionMap = computed(() => {
  const map: Record<
    string,
    Prediction
  > = {};

  for (const prediction of predictions.value) {
    if (prediction.contentId) {
      map[prediction.contentId] =
        prediction;
    }
  }

  return map;
});

const getPredictionForContent = (
  contentId: string,
) => {
  return predictionMap.value[contentId] || null;
};

const hasPrediction = (
  contentId: string,
) => {
  return Boolean(
    getPredictionForContent(contentId),
  );
};

const isPredictionRunning = (
  contentId: string,
) => {
  return Boolean(
    runningPrediction.value[contentId],
  );
};

const getPredictionError = (
  contentId: string,
) => {
  return (
    predictionErrors.value[contentId] ||
    ""
  );
};

const formatConfidence = (
  confidence: number,
) => {
  return `${Math.round(
    confidence * 100,
  )}%`;
};

const predictionLabel = (
  prediction: string,
) => {
  return prediction
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase(),
    );
};

const signalExplanation = (key: string, value: unknown) => {
  if (key === "textLength" && typeof value === "number") return `Evidence contains ${value} characters.`;
  if (key === "hasSourceUrl" && value === true) return "A source URL was provided.";
  if (key === "hasFile" && value === true) return "An image file was provided.";
  if (key === "contentType") return `Evidence type: ${String(value)}.`;
  if (typeof value === "boolean") return `${key.replaceAll("_", " ")}: ${value ? "yes" : "no"}.`;
  return `${key.replaceAll("_", " ")}: ${String(value)}.`;
};

const predictionClass = (
  prediction: string,
) => {
  if (
    prediction.includes("REQUIRES_ANALYSIS")
  ) {
    return "bg-amber-500/10 text-amber-700";
  }

  if (prediction === "INCONCLUSIVE") {
    return "bg-black/5 text-[var(--vl-muted)]";
  }

  return "bg-[var(--vl-sage)]/12 text-[var(--vl-sage-dark)]";
};

const confidenceBarWidth = (
  confidence: number,
) => {
  return `${Math.max(
    0,
    Math.min(100, confidence * 100),
  )}%`;
};

/**
 * ---------------------------------------------------------
 * Fetch Analysis
 * ---------------------------------------------------------
 */

const fetchAnalysis = async () => {
  loading.value = true;
  error.value = "";

  try {
    const id = String(
      route.params.id || "",
    );

    if (!id) {
      throw new Error(
        "Analysis ID is missing.",
      );
    }

    const response =
      await $fetch<AnalysisResponse>(
        `${apiBase}/api/analyses/${id}`,
        {
          method: "GET",
          credentials: "include",
        },
      );

    if (
      !response.success ||
      !response.analysis
    ) {
      throw new Error(
        response.message ||
          "Unable to load analysis.",
      );
    }

    analysis.value =
      response.analysis;
  } catch (err: any) {
    console.error(
      "Analysis detail error:",
      err,
    );

    error.value =
      err?.data?.message ||
      err?.message ||
      "Unable to load this analysis.";
  } finally {
    loading.value = false;
  }
};

/**
 * ---------------------------------------------------------
 * Fetch Saved Evidence
 * ---------------------------------------------------------
 */

const fetchContents = async () => {
  contentsLoading.value = true;
  contentsError.value = "";

  try {
    const id = String(
      route.params.id || "",
    );

    if (!id) {
      throw new Error(
        "Analysis ID is missing.",
      );
    }

    const response =
      await $fetch<ContentsResponse>(
        `${apiBase}/api/analyses/${id}/content`,
        {
          method: "GET",
          credentials: "include",
        },
      );

    if (!response.success) {
      throw new Error(
        response.message ||
          "Unable to load evidence.",
      );
    }

    contents.value =
      response.contents || [];
  } catch (err: any) {
    console.error(
      "Analysis content list error:",
      err,
    );

    contentsError.value =
      err?.data?.message ||
      err?.message ||
      "Unable to load evidence.";
  } finally {
    contentsLoading.value = false;
  }
};

/**
 * ---------------------------------------------------------
 * Fetch Predictions
 * ---------------------------------------------------------
 */

const fetchPredictions = async () => {
  predictionsLoading.value = true;
  predictionsError.value = "";

  try {
    const id = String(
      route.params.id || "",
    );

    if (!id) {
      throw new Error(
        "Analysis ID is missing.",
      );
    }

    const response =
      await $fetch<PredictionsResponse>(
        `${apiBase}/api/analyses/${id}/predictions`,
        {
          method: "GET",
          credentials: "include",
        },
      );

    if (!response.success) {
      throw new Error(
        response.message ||
          "Unable to load predictions.",
      );
    }

    predictions.value =
      response.predictions || [];
  } catch (err: any) {
    console.error(
      "Prediction list error:",
      err,
    );

    predictionsError.value =
      err?.data?.message ||
      err?.message ||
      "Unable to load predictions.";
  } finally {
    predictionsLoading.value = false;
  }
};

/**
 * ---------------------------------------------------------
 * Run Prediction
 * ---------------------------------------------------------
 */

const runPredictionForContent =
  async (
    contentId: string,
  ) => {
    predictionErrors.value = {
      ...predictionErrors.value,
      [contentId]: "",
    };

    runningPrediction.value = {
      ...runningPrediction.value,
      [contentId]: true,
    };

    try {
      const analysisId = String(
        route.params.id || "",
      );

      if (!analysisId) {
        throw new Error(
          "Analysis ID is missing.",
        );
      }

      const response =
        await $fetch<PredictionResponse>(
          `${apiBase}/api/analyses/${analysisId}/predict/${contentId}`,
          {
            method: "POST",
            credentials: "include",
          },
        );

      if (
        !response.success ||
        !response.prediction
      ) {
        throw new Error(
          response.message ||
            "Unable to run prediction.",
        );
      }

      /**
       * Add the new prediction to
       * the local state immediately.
       */
      predictions.value = [
        response.prediction,
        ...predictions.value.filter(
          (item) =>
            item.contentId !==
            contentId,
        ),
      ];

      /**
       * Refresh analysis status.
       */
      await fetchAnalysis();
    } catch (err: any) {
      console.error(
        "Prediction error:",
        err,
      );

      predictionErrors.value = {
        ...predictionErrors.value,
        [contentId]:
          err?.data?.message ||
          err?.message ||
          "Unable to run prediction.",
      };

      await fetchAnalysis();
    } finally {
      runningPrediction.value = {
        ...runningPrediction.value,
        [contentId]: false,
      };
    }
  };

const runAllPredictions = async () => {
  if (runningAll.value) return;
  runningAll.value = true;
  const pending = contents.value.filter((item) => !predictions.value.some((prediction) => prediction.contentId === item.id && prediction.status === "COMPLETED"));
  for (const item of pending) await runPredictionForContent(item.id);
  await fetchPredictions();
  runningAll.value = false;
};
/**
 * ---------------------------------------------------------
 * Format Content Date
 * ---------------------------------------------------------
 */

const formatContentDate = (
  date: string,
) => {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
};

/**
 * ---------------------------------------------------------
 * Format File Size
 * ---------------------------------------------------------
 */

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
    return `${(
      size / 1024
    ).toFixed(1)} KB`;
  }

  return `${(
    size /
    (1024 * 1024)
  ).toFixed(1)} MB`;
};

/**
 * ---------------------------------------------------------
 * Image URL
 * ---------------------------------------------------------
 */

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

/**
 * ---------------------------------------------------------
 * Add Text Modal
 * ---------------------------------------------------------
 */

const openTextModal = () => {
  textTitle.value = "";
  textContent.value = "";
  textError.value = "";

  showTextModal.value = true;
};

const closeTextModal = () => {
  if (savingText.value) {
    return;
  }

  showTextModal.value = false;
};

const saveTextContent = async () => {
  textError.value = "";

  const content =
    textContent.value.trim();

  if (!content) {
    textError.value =
      "Please enter some text.";
    return;
  }

  savingText.value = true;

  try {
    const id = String(
      route.params.id || "",
    );

    if (!id) {
      throw new Error(
        "Analysis ID is missing.",
      );
    }

    const response =
      await $fetch<ContentResponse>(
        `${apiBase}/api/analyses/${id}/content/text`,
        {
          method: "POST",
          credentials: "include",

          body: {
            type: "TEXT",
            title:
              textTitle.value.trim() ||
              undefined,
            text: content,
          },
        },
      );

    if (!response.success) {
      throw new Error(
        response.message ||
          "Unable to save text.",
      );
    }

    showTextModal.value = false;

    textTitle.value = "";
    textContent.value = "";
    textError.value = "";

    await fetchContents();
    await fetchAnalysis();
  } catch (err: any) {
    console.error(
      "Text content save error:",
      err,
    );

    textError.value =
      err?.data?.message ||
      err?.message ||
      "Unable to save text.";
  } finally {
    savingText.value = false;
  }
};

/**
 * ---------------------------------------------------------
 * Add Image Modal
 * ---------------------------------------------------------
 */

const openImageModal = () => {
  imageTitle.value = "";
  selectedImage.value = null;
  imagePreview.value = "";
  imageError.value = "";

  showImageModal.value = true;
};

const closeImageModal = () => {
  if (savingImage.value) {
    return;
  }

  showImageModal.value = false;

  selectedImage.value = null;
  imagePreview.value = "";
  imageTitle.value = "";
  imageError.value = "";

  if (imageInput.value) {
    imageInput.value.value = "";
  }
};

const handleImageSelect = (
  event: Event,
) => {
  imageError.value = "";

  const target =
    event.target as HTMLInputElement;

  const file =
    target.files?.[0];

  if (!file) {
    return;
  }

  const allowedTypes = [
    "image/jpeg",
    "image/png",
    "image/webp",
  ];

  if (!allowedTypes.includes(file.type)) {
    imageError.value =
      "Only JPG, JPEG, PNG, and WEBP images are allowed.";

    target.value = "";

    return;
  }

  const maxSize =
    10 * 1024 * 1024;

  if (file.size > maxSize) {
    imageError.value =
      "Image size must be 10 MB or smaller.";

    target.value = "";

    return;
  }

  selectedImage.value = file;

  imageTitle.value =
    imageTitle.value.trim() ||
    file.name.replace(
      /\.[^/.]+$/,
      "",
    );

  if (imagePreview.value) {
    URL.revokeObjectURL(
      imagePreview.value,
    );
  }

  imagePreview.value =
    URL.createObjectURL(file);
};

const removeSelectedImage = () => {
  if (imagePreview.value) {
    URL.revokeObjectURL(
      imagePreview.value,
    );
  }

  selectedImage.value = null;
  imagePreview.value = "";
  imageTitle.value = "";

  if (imageInput.value) {
    imageInput.value.value = "";
  }
};

const saveImageContent = async () => {
  imageError.value = "";

  if (!selectedImage.value) {
    imageError.value =
      "Please select an image.";
    return;
  }

  savingImage.value = true;

  try {
    const id = String(
      route.params.id || "",
    );

    if (!id) {
      throw new Error(
        "Analysis ID is missing.",
      );
    }

    const formData =
      new FormData();

    formData.append(
      "image",
      selectedImage.value,
    );

    const title =
      imageTitle.value.trim();

    if (title) {
      formData.append(
        "title",
        title,
      );
    }

    const response =
      await $fetch<ContentResponse>(
        `${apiBase}/api/analyses/${id}/content/image`,
        {
          method: "POST",
          credentials: "include",
          body: formData,
        },
      );

    if (!response.success) {
      throw new Error(
        response.message ||
          "Unable to upload image.",
      );
    }

    closeImageModal();

    await fetchContents();
    await fetchAnalysis();
  } catch (err: any) {
    console.error(
      "Image upload error:",
      err,
    );

    imageError.value =
      err?.data?.message ||
      err?.message ||
      "Unable to upload image.";
  } finally {
    savingImage.value = false;
  }
};

/**
 * ---------------------------------------------------------
 * Add Source Modal
 * ---------------------------------------------------------
 */

const openSourceModal = () => {
  sourceTitle.value = "";
  sourceUrl.value = "";
  sourceError.value = "";

  showSourceModal.value = true;
};

const closeSourceModal = () => {
  if (savingSource.value) {
    return;
  }

  showSourceModal.value = false;

  sourceTitle.value = "";
  sourceUrl.value = "";
  sourceError.value = "";
};

const saveSourceContent = async () => {
  sourceError.value = "";

  const url =
    sourceUrl.value.trim();

  if (!url) {
    sourceError.value =
      "Please enter a source URL.";

    return;
  }

  try {
    new URL(url);
  } catch {
    sourceError.value =
      "Please enter a valid URL, including https://.";

    return;
  }

  savingSource.value = true;

  try {
    const id = String(
      route.params.id || "",
    );

    if (!id) {
      throw new Error(
        "Analysis ID is missing.",
      );
    }

    const response =
      await $fetch<ContentResponse>(
        `${apiBase}/api/analyses/${id}/content/source`,
        {
          method: "POST",
          credentials: "include",

          body: {
            title:
              sourceTitle.value.trim() ||
              undefined,
            sourceUrl: url,
          },
        },
      );

    if (!response.success) {
      throw new Error(
        response.message ||
          "Unable to save source.",
      );
    }

    closeSourceModal();

    await fetchContents();
    await fetchAnalysis();
  } catch (err: any) {
    console.error(
      "Source save error:",
      err,
    );

    sourceError.value =
      err?.data?.message ||
      err?.message ||
      "Unable to save source.";
  } finally {
    savingSource.value = false;
  }
};

/**
 * ---------------------------------------------------------
 * Cleanup
 * ---------------------------------------------------------
 */

onBeforeUnmount(() => {
  if (imagePreview.value) {
    URL.revokeObjectURL(
      imagePreview.value,
    );
  }
});

/**
 * ---------------------------------------------------------
 * Initial Load
 * ---------------------------------------------------------
 */

await Promise.all([
  fetchAnalysis(),
  fetchContents(),
  fetchPredictions(),
]);
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

      <div
        v-if="loading"
        class="space-y-4"
      >
        <div
          class="h-4 w-36 animate-pulse rounded-full bg-black/5"
        />

        <div
          class="h-12 w-full max-w-2xl animate-pulse rounded-2xl bg-black/5"
        />
      </div>

      <template
        v-else-if="analysis"
      >
        <div class="eyebrow">
          <Sparkles :size="13" />

          Investigation workspace
        </div>

        <div
          class="mt-4 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"
        >
          <div>
            <h1
              class="text-4xl font-semibold tracking-[-0.045em] sm:text-5xl"
            >
              {{ analysis.title }}
            </h1>

            <p
              class="mt-4 max-w-2xl text-base leading-7 text-[var(--vl-muted)]"
            >
              Build an evidence-backed investigation
              from text, images, and external sources.
            </p>
          </div>

          <div
            class="flex items-center gap-3"
          >
            <span
              class="inline-flex items-center rounded-full px-3 py-1.5 text-xs font-semibold"
              :class="statusClass"
            >
              {{ statusLabel }}
            </span>

            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--vl-border)] bg-[var(--vl-surface)] text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)]"
              aria-label="More analysis actions"
            >
              <MoreHorizontal :size="18" />
            </button>
          </div>
        </div>
      </template>
    </section>

    <!-- Error -->
    <section
      v-if="error"
      class="rounded-[28px] border border-[var(--vl-terracotta)]/25 bg-[var(--vl-terracotta)]/5 p-8"
    >
      <h2 class="text-lg font-semibold">
        Unable to load analysis
      </h2>

      <p
        class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
      >
        {{ error }}
      </p>

      <button
        type="button"
        class="mt-6 inline-flex h-11 items-center justify-center rounded-xl bg-[var(--vl-sage-dark)] px-5 text-sm font-semibold text-white"
        @click="fetchAnalysis"
      >
        Try again
      </button>
    </section>

    <!-- Workspace -->
    <template
      v-else-if="analysis"
    >
      <!-- Metadata -->
      <section
        class="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
          >
            <Clock3 :size="18" />
          </div>

          <p
            class="mt-4 text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
          >
            Created
          </p>

          <p
            class="mt-1 text-sm font-semibold"
          >
            {{ formattedCreatedAt }}
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]"
          >
            <FileSearch :size="18" />
          </div>

          <p
            class="mt-4 text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
          >
            Investigation
          </p>

          <p
            class="mt-1 text-sm font-semibold"
          >
            {{ statusLabel }}
          </p>
        </div>

        <div
          class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
          >
            <Sparkles :size="18" />
          </div>

          <p
            class="mt-4 text-xs font-medium uppercase tracking-[0.12em] text-[var(--vl-muted)]"
          >
            Intelligence
          </p>

          <p
            class="mt-1 text-sm font-semibold"
          >
            {{
              predictions.length
                ? `${predictions.length} prediction${
                    predictions.length === 1
                      ? ""
                      : "s"
                  }`
                : "Ready for analysis"
            }}
          </p>
        </div>
      </section>

      <!-- Ingestion -->
      <section
        class="rounded-[28px] border border-[var(--vl-border)] bg-[rgba(250,248,242,0.72)] p-6 shadow-[0_20px_70px_rgba(32,35,31,0.07)] backdrop-blur-xl sm:p-8"
      >
        <div>
          <div class="eyebrow">
            <Sparkles :size="13" />

            Evidence ingestion
          </div>

          <h2
            class="mt-4 text-2xl font-semibold tracking-[-0.03em]"
          >
            Bring evidence into this investigation.
          </h2>

          <p
            class="mt-3 max-w-2xl text-sm leading-6 text-[var(--vl-muted)]"
          >
            Add text, images, and external sources.
            Each evidence item can then be sent through
            the VeriLens prediction engine.
          </p>
        </div>

        <div
          class="mt-8 grid gap-4 md:grid-cols-3"
        >
          <!-- Text -->
          <button
            type="button"
            class="group rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5 text-left transition-all hover:-translate-y-0.5 hover:border-[var(--vl-sage-dark)]/30 hover:shadow-[0_14px_35px_rgba(32,35,31,0.06)]"
            @click="openTextModal"
          >
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
            >
              <FileSearch :size="19" />
            </div>

            <h3
              class="mt-5 text-sm font-semibold"
            >
              Add text
            </h3>

            <p
              class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
            >
              Add an article, claim, document, or text
              snippet for analysis.
            </p>

            <span
              class="mt-5 inline-flex text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              Add text Ã¢â€ â€™
            </span>
          </button>

          <!-- Image -->
          <button
            type="button"
            class="group rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5 text-left transition-all hover:-translate-y-0.5 hover:border-[var(--vl-terracotta)]/30 hover:shadow-[0_14px_35px_rgba(32,35,31,0.06)]"
            @click="openImageModal"
          >
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--vl-terracotta)]/10 text-[var(--vl-terracotta)]"
            >
              <Image :size="19" />
            </div>

            <h3
              class="mt-5 text-sm font-semibold"
            >
              Add image
            </h3>

            <p
              class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
            >
              Add visual evidence for computer vision
              and authenticity analysis.
            </p>

            <span
              class="mt-5 inline-flex text-xs font-semibold text-[var(--vl-terracotta)]"
            >
              Upload image Ã¢â€ â€™
            </span>
          </button>

          <!-- Source -->
          <button
            type="button"
            class="group rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-5 text-left transition-all hover:-translate-y-0.5 hover:border-[var(--vl-sage-dark)]/30 hover:shadow-[0_14px_35px_rgba(32,35,31,0.06)]"
            @click="openSourceModal"
          >
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
            >
              <Link :size="19" />
            </div>

            <h3
              class="mt-5 text-sm font-semibold"
            >
              Add source
            </h3>

            <p
              class="mt-2 text-xs leading-5 text-[var(--vl-muted)]"
            >
              Connect external sources and evidence for
              claim verification.
            </p>

            <span
              class="mt-5 inline-flex text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              Add source Ã¢â€ â€™
            </span>
          </button>
        </div>
      </section>

      <!-- Saved Evidence -->
      <section
        class="mt-6 rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6 sm:p-8"
      >
        <div
          class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <div class="eyebrow">
              <FileSearch :size="13" />

              Investigation evidence
            </div>

            <h2
              class="mt-4 text-2xl font-semibold tracking-[-0.03em]"
            >
              Saved evidence
            </h2>

            <p
              class="mt-2 max-w-2xl text-sm leading-6 text-[var(--vl-muted)]"
            >
              Run the deterministic MVP engine on one item or all pending evidence.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-3">
          <button type="button" class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-[var(--vl-sage-dark)] px-4 text-xs font-semibold text-white disabled:opacity-50" :disabled="runningAll || contents.length === 0" @click="runAllPredictions"><Loader2 v-if="runningAll" :size="14" class="animate-spin"/><Sparkles v-else :size="14"/>{{ runningAll ? "Running analysisâ€¦" : "Run analysis" }}</button>
          <span
            class="inline-flex w-fit rounded-full bg-black/5 px-3 py-1.5 text-xs font-semibold text-[var(--vl-muted)]"
          >
            {{ contents.length }}
            {{
              contents.length === 1
                ? "item"
                : "items"
            }}
          </span>
          </div>
        </div>

        <!-- Loading -->
        <div
          v-if="contentsLoading"
          class="mt-8 grid gap-4"
        >
          <div
            v-for="item in 2"
            :key="item"
            class="animate-pulse rounded-2xl border border-[var(--vl-border)] p-5"
          >
            <div
              class="h-4 w-32 rounded bg-black/5"
            />

            <div
              class="mt-4 h-4 w-3/4 rounded bg-black/5"
            />

            <div
              class="mt-3 h-4 w-full rounded bg-black/5"
            />
          </div>
        </div>

        <!-- Error -->
        <div
          v-else-if="contentsError"
          class="mt-8 rounded-2xl border border-[var(--vl-terracotta)]/20 bg-[var(--vl-terracotta)]/5 p-5"
        >
          <p class="text-sm font-semibold">
            Unable to load evidence
          </p>

          <p
            class="mt-2 text-sm text-[var(--vl-muted)]"
          >
            {{ contentsError }}
          </p>

          <button
            type="button"
            class="mt-4 text-sm font-semibold text-[var(--vl-sage-dark)]"
            @click="fetchContents"
          >
            Try again Ã¢â€ â€™
          </button>
        </div>

        <!-- Empty -->
        <div
          v-else-if="contents.length === 0"
          class="mt-8 rounded-2xl border border-dashed border-[var(--vl-border)] p-8 text-center"
        >
          <FileSearch
            :size="24"
            class="mx-auto text-[var(--vl-muted)]"
          />

          <h3
            class="mt-4 text-sm font-semibold"
          >
            No evidence yet
          </h3>

          <p
            class="mx-auto mt-2 max-w-md text-xs leading-5 text-[var(--vl-muted)]"
          >
            Add text, images, or external sources to begin
            building this investigation.
          </p>
        </div>

        <!-- Evidence Cards -->
        <div
          v-else
          class="mt-8 grid gap-4"
        >
          <article
            v-for="content in contents"
            :key="content.id"
            class="rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.55)] p-5 transition-all hover:border-[var(--vl-sage-dark)]/25 hover:shadow-[0_12px_30px_rgba(32,35,31,0.05)]"
          >
            <div
              class="flex flex-col gap-5"
            >
              <!-- Evidence Header -->
              <div
                class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"
              >
                <div class="min-w-0 flex-1">
                  <div
                    class="flex flex-wrap items-center gap-2"
                  >
                    <span
                      class="rounded-full bg-[var(--vl-sage)]/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--vl-sage-dark)]"
                    >
                      {{ content.type }}
                    </span>

                    <span
                      class="text-xs text-[var(--vl-muted)]"
                    >
                      {{
                        formatContentDate(
                          content.createdAt,
                        )
                      }}
                    </span>
                  </div>

                  <h3
                    v-if="content.title"
                    class="mt-4 text-base font-semibold"
                  >
                    {{ content.title }}
                  </h3>

                  <!-- Text -->
                  <p
                    v-if="content.text"
                    class="mt-3 whitespace-pre-wrap text-sm leading-7 text-[var(--vl-muted)]"
                  >
                    {{ content.text }}
                  </p>

                  <!-- Source -->
                  <a
                    v-if="content.sourceUrl"
                    :href="content.sourceUrl"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="mt-3 block break-all text-sm font-medium text-[var(--vl-sage-dark)] underline-offset-4 hover:underline"
                  >
                    {{ content.sourceUrl }}
                  </a>

                  <!-- Image -->
                  <div
                    v-if="
                      content.type ===
                        'IMAGE' &&
                      content.fileUrl
                    "
                    class="mt-5 overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-black/5"
                  >
                    <img
                      :src="
                        getImageUrl(
                          content.fileUrl,
                        )
                      "
                      :alt="
                        content.title ||
                        content.fileName ||
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
                          content.fileName ||
                          "Uploaded image"
                        }}
                      </span>

                      <span
                        v-if="content.fileSize"
                        class="shrink-0 text-xs text-[var(--vl-muted)]"
                      >
                        {{
                          formatFileSize(
                            content.fileSize,
                          )
                        }}
                      </span>
                    </div>
                  </div>
                </div>

                <span
                  v-if="content.text"
                  class="shrink-0 text-xs text-[var(--vl-muted)]"
                >
                  {{ content.text.length }}
                  characters
                </span>
              </div>

              <!-- Prediction Action -->
              <div
                class="border-t border-[var(--vl-border)] pt-5"
              >
                <div
                  class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p
                      class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
                    >
                      Intelligence
                    </p>

                    <p
                      class="mt-1 text-sm text-[var(--vl-muted)]"
                    >
                      Run the current VeriLens prediction
                      engine on this evidence.
                    </p>
                  </div>

                  <button
                    type="button"
                    class="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-xl bg-[var(--vl-sage-dark)] px-5 text-sm font-semibold text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                    :disabled="
                      isPredictionRunning(
                        content.id,
                      )
                    "
                    @click="
                      runPredictionForContent(
                        content.id,
                      )
                    "
                  >
                    <Loader2
                      v-if="
                        isPredictionRunning(
                          content.id,
                        )
                      "
                      :size="15"
                      class="animate-spin"
                    />

                    <Zap
                      v-else
                      :size="15"
                    />

                    {{
                      isPredictionRunning(
                        content.id,
                      )
                        ? "Analyzing..."
                        : hasPrediction(
                              content.id,
                            )
                          ? "Run again"
                          : "Run prediction"
                    }}
                  </button>
                </div>

                <!-- Prediction Error -->
                <div
                  v-if="
                    getPredictionError(
                      content.id,
                    )
                  "
                  class="mt-4 rounded-xl border border-[var(--vl-terracotta)]/20 bg-[var(--vl-terracotta)]/5 px-4 py-3"
                >
                  <p
                    class="text-sm text-[var(--vl-terracotta)]"
                  >
                    {{
                      getPredictionError(
                        content.id,
                      )
                    }}
                  </p>
                </div>

                <!-- Prediction Result -->
                <div
                  v-if="
                    getPredictionForContent(
                      content.id,
                    )
                  "
                  class="mt-5 rounded-2xl border border-[var(--vl-sage-dark)]/15 bg-[var(--vl-sage)]/5 p-5"
                >
                  <div
                    class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"
                  >
                    <div>
                      <div
                        class="flex items-center gap-2"
                      >
                        <CheckCircle2
                          :size="17"
                          class="text-[var(--vl-sage-dark)]"
                        />

                        <p
                          class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--vl-sage-dark)]"
                        >
                          Prediction result
                        </p>
                      </div>

                      <p
                        class="mt-3 text-xl font-semibold tracking-[-0.02em]"
                      >
                        {{
                          predictionLabel(
                            getPredictionForContent(
                              content.id,
                            )!.prediction,
                          )
                        }}
                      </p>
                    </div>

                    <span
                      class="inline-flex w-fit rounded-full px-3 py-1.5 text-xs font-semibold"
                      :class="
                        predictionClass(
                          getPredictionForContent(
                            content.id,
                          )!.prediction,
                        )
                      "
                    >
                      {{
                        formatConfidence(
                          getPredictionForContent(
                            content.id,
                          )!.confidence,
                        )
                      }}
                      confidence
                    </span>
                  </div>

                  <!-- Confidence -->
                  <div class="mt-5">
                    <div
                      class="flex items-center justify-between text-xs"
                    >
                      <span
                        class="font-medium text-[var(--vl-muted)]"
                      >
                        Confidence
                      </span>

                      <span
                        class="font-semibold text-[var(--vl-ink)]"
                      >
                        {{
                          formatConfidence(
                            getPredictionForContent(
                              content.id,
                            )!.confidence,
                          )
                        }}
                      </span>
                    </div>

                    <div
                      class="mt-2 h-2 overflow-hidden rounded-full bg-black/5"
                    >
                      <div
                        class="h-full rounded-full bg-[var(--vl-sage-dark)] transition-all duration-500"
                        :style="{
                          width:
                            confidenceBarWidth(
                              getPredictionForContent(
                                content.id,
                              )!.confidence,
                            ),
                        }"
                      />
                    </div>
                  </div>

                  <!-- Signals -->
                  <div
                    v-if="
                      getPredictionForContent(
                        content.id,
                      )?.signals
                    "
                    class="mt-6"
                  >
                    <p
                      class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--vl-muted)]"
                    >
                      Evidence signals
                    </p>

                    <div
                      class="mt-3 grid gap-2 sm:grid-cols-2"
                    >
                      <div
                        v-for="(
                          value,
                          key
                        ) in getPredictionForContent(
                          content.id,
                        )!.signals"
                        :key="key"
                        class="flex items-center justify-between gap-3 rounded-xl border border-[var(--vl-border)] bg-[var(--vl-surface)] px-3 py-2.5"
                      >
                        <span
                          class="text-xs font-medium text-[var(--vl-muted)]"
                        >
                          {{
                            String(
                              key,
                            )
                              .replaceAll(
                                "_",
                                " ",
                              )
                              .replace(
                                /\b\w/g,
                                (char) =>
                                  char.toUpperCase(),
                              )
                          }}
                        </span>

                        <span
                          class="max-w-[55%] truncate text-right text-xs font-semibold text-[var(--vl-ink)]"
                        >
                          {{ signalExplanation(String(key), value) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Metadata -->
                  <div
                    v-if="
                      getPredictionForContent(
                        content.id,
                      )?.metadata
                    "
                    class="mt-5 flex flex-wrap gap-2"
                  >
                    <span
                      v-if="
                        getPredictionForContent(
                          content.id,
                        )?.metadata
                          ?.engine
                      "
                      class="rounded-full bg-black/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                    >
                      Engine:
                      {{
                        String(
                          getPredictionForContent(
                            content.id,
                          )?.metadata
                            ?.engine,
                        )
                      }}
                    </span>

                    <span
                      v-if="
                        getPredictionForContent(
                          content.id,
                        )?.metadata
                          ?.version
                      "
                      class="rounded-full bg-black/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                    >
                      Version:
                      {{
                        String(
                          getPredictionForContent(
                            content.id,
                          )?.metadata
                            ?.version,
                        )
                      }}
                    </span>

                    <span
                      v-if="
                        getPredictionForContent(
                          content.id,
                        )?.metadata
                          ?.mode
                      "
                      class="rounded-full bg-black/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--vl-muted)]"
                    >
                      Mode:
                      {{
                        String(
                          getPredictionForContent(
                            content.id,
                          )?.metadata
                            ?.mode,
                        )
                      }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Prediction Summary -->
      <section
        class="mt-6 rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6 sm:p-8"
      >
        <div
          class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <div class="eyebrow">
              <Sparkles :size="13" />

              Prediction intelligence
            </div>

            <h2
              class="mt-4 text-2xl font-semibold tracking-[-0.03em]"
            >
              Current prediction activity
            </h2>

            <p
              class="mt-2 max-w-2xl text-sm leading-6 text-[var(--vl-muted)]"
            >
              Predictions generated for evidence in this
              investigation.
            </p>
          </div>

          <span
            class="inline-flex w-fit rounded-full bg-[var(--vl-sage)]/10 px-3 py-1.5 text-xs font-semibold text-[var(--vl-sage-dark)]"
          >
            {{ predictions.length }}
            {{
              predictions.length === 1
                ? "prediction"
                : "predictions"
            }}
          </span>
        </div>

        <div
          v-if="predictionsLoading"
          class="mt-6 flex items-center gap-3 text-sm text-[var(--vl-muted)]"
        >
          <Loader2
            :size="16"
            class="animate-spin"
          />

          Loading prediction history...
        </div>

        <div
          v-else-if="predictionsError"
          class="mt-6 rounded-2xl border border-[var(--vl-terracotta)]/20 bg-[var(--vl-terracotta)]/5 p-5"
        >
          <p
            class="text-sm text-[var(--vl-terracotta)]"
          >
            {{ predictionsError }}
          </p>

          <button
            type="button"
            class="mt-3 text-sm font-semibold text-[var(--vl-sage-dark)]"
            @click="fetchPredictions"
          >
            Try again Ã¢â€ â€™
          </button>
        </div>

        <div
          v-else-if="predictions.length === 0"
          class="mt-6 rounded-2xl border border-dashed border-[var(--vl-border)] p-6 text-center"
        >
          <Sparkles
            :size="22"
            class="mx-auto text-[var(--vl-muted)]"
          />

          <p
            class="mt-3 text-sm font-semibold"
          >
            No predictions yet
          </p>

          <p
            class="mt-1 text-xs text-[var(--vl-muted)]"
          >
            Run a prediction on an evidence item above.
          </p>
        </div>

        <div
          v-else
          class="mt-6 grid gap-3"
        >
          <div
            v-for="prediction in predictions"
            :key="prediction.id"
            class="flex flex-col gap-3 rounded-2xl border border-[var(--vl-border)] bg-[rgba(250,248,242,0.55)] p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div
              class="flex items-center gap-3"
            >
              <div
                class="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--vl-sage)]/10 text-[var(--vl-sage-dark)]"
              >
                <Sparkles :size="16" />
              </div>

              <div>
                <p
                  class="text-sm font-semibold"
                >
                  {{
                    predictionLabel(
                      prediction.prediction,
                    )
                  }}
                </p>

                <p
                  class="mt-1 text-xs text-[var(--vl-muted)]"
                >
                  {{
                    formatContentDate(
                      prediction.createdAt,
                    )
                  }}
                </p>
              </div>
            </div>

            <span
              class="inline-flex w-fit rounded-full px-3 py-1.5 text-xs font-semibold"
              :class="
                predictionClass(
                  prediction.prediction,
                )
              "
            >
              {{
                formatConfidence(
                  prediction.confidence,
                )
              }}
              confidence
            </span>
          </div>
        </div>
      </section>

      <!-- Add Text Modal -->
      <Teleport to="body">
        <div
          v-if="showTextModal"
          class="fixed inset-0 z-[100] flex items-center justify-center bg-black/30 p-4 backdrop-blur-sm"
          @click.self="closeTextModal"
        >
          <div
            class="w-full max-w-2xl rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6 shadow-[0_30px_100px_rgba(32,35,31,0.18)] sm:p-8"
          >
            <div
              class="flex items-start justify-between gap-4"
            >
              <div>
                <div class="eyebrow">
                  <FileSearch :size="13" />

                  Text evidence
                </div>

                <h2
                  class="mt-3 text-2xl font-semibold tracking-[-0.03em]"
                >
                  Add text to this investigation
                </h2>

                <p
                  class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
                >
                  Add a claim, article, document, or text
                  snippet that VeriLens should investigate.
                </p>
              </div>

              <button
                type="button"
                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[var(--vl-border)] text-xl text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)]"
                aria-label="Close"
                :disabled="savingText"
                @click="closeTextModal"
              >
                Ãƒâ€”
              </button>
            </div>

            <div class="mt-7 space-y-5">
              <div>
                <label
                  for="text-title"
                  class="text-sm font-semibold"
                >
                  Title
                </label>

                <input
                  id="text-title"
                  v-model="textTitle"
                  type="text"
                  maxlength="200"
                  placeholder="e.g. Viral claim"
                  class="mt-2 h-12 w-full rounded-xl border border-[var(--vl-border)] bg-white/70 px-4 text-sm outline-none transition focus:border-[var(--vl-sage-dark)]"
                  :disabled="savingText"
                />
              </div>

              <div>
                <label
                  for="text-content"
                  class="text-sm font-semibold"
                >
                  Content
                </label>

                <textarea
                  id="text-content"
                  v-model="textContent"
                  rows="9"
                  maxlength="50000"
                  placeholder="Paste the claim, article, document text, or evidence here..."
                  class="mt-2 w-full resize-none rounded-xl border border-[var(--vl-border)] bg-white/70 p-4 text-sm leading-6 outline-none transition focus:border-[var(--vl-sage-dark)]"
                  :disabled="savingText"
                />
              </div>

              <p
                v-if="textError"
                class="rounded-xl border border-[var(--vl-terracotta)]/20 bg-[var(--vl-terracotta)]/5 px-4 py-3 text-sm text-[var(--vl-terracotta)]"
              >
                {{ textError }}
              </p>
            </div>

            <div
              class="mt-7 flex justify-end gap-3"
            >
              <button
                type="button"
                class="h-11 rounded-xl border border-[var(--vl-border)] px-5 text-sm font-semibold text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)] disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="savingText"
                @click="closeTextModal"
              >
                Cancel
              </button>

              <button
                type="button"
                class="inline-flex h-11 items-center justify-center rounded-xl bg-[var(--vl-sage-dark)] px-6 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="savingText"
                @click="saveTextContent"
              >
                {{
                  savingText
                    ? "Saving..."
                    : "Save text"
                }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Add Image Modal -->
      <Teleport to="body">
        <div
          v-if="showImageModal"
          class="fixed inset-0 z-[100] flex items-center justify-center bg-black/30 p-4 backdrop-blur-sm"
          @click.self="closeImageModal"
        >
          <div
            class="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6 shadow-[0_30px_100px_rgba(32,35,31,0.18)] sm:p-8"
          >
            <div
              class="flex items-start justify-between gap-4"
            >
              <div>
                <div class="eyebrow">
                  <Image :size="13" />

                  Visual evidence
                </div>

                <h2
                  class="mt-3 text-2xl font-semibold tracking-[-0.03em]"
                >
                  Add image to this investigation
                </h2>

                <p
                  class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
                >
                  Upload visual evidence for the computer
                  vision and authenticity pipeline.
                </p>
              </div>

              <button
                type="button"
                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[var(--vl-border)] text-xl text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)]"
                aria-label="Close"
                :disabled="savingImage"
                @click="closeImageModal"
              >
                Ãƒâ€”
              </button>
            </div>

            <div class="mt-7 space-y-5">
              <div>
                <label
                  for="image-file"
                  class="text-sm font-semibold"
                >
                  Image
                </label>

                <input
                  id="image-file"
                  ref="imageInput"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  class="mt-2 block w-full cursor-pointer rounded-xl border border-[var(--vl-border)] bg-white/70 px-4 py-3 text-sm"
                  :disabled="savingImage"
                  @change="handleImageSelect"
                />

                <p
                  class="mt-2 text-xs text-[var(--vl-muted)]"
                >
                  JPG, PNG, or WEBP Ã‚Â· Maximum 10 MB
                </p>
              </div>

              <div
                v-if="imagePreview"
                class="overflow-hidden rounded-2xl border border-[var(--vl-border)] bg-black/5"
              >
                <img
                  :src="imagePreview"
                  alt="Selected image preview"
                  class="max-h-[360px] w-full object-contain"
                />

                <div
                  class="flex items-center justify-between gap-3 border-t border-[var(--vl-border)] px-4 py-3"
                >
                  <span
                    class="truncate text-xs text-[var(--vl-muted)]"
                  >
                    {{
                      selectedImage?.name
                    }}
                  </span>

                  <button
                    type="button"
                    class="shrink-0 text-xs font-semibold text-[var(--vl-terracotta)] hover:underline"
                    :disabled="savingImage"
                    @click="removeSelectedImage"
                  >
                    Remove
                  </button>
                </div>
              </div>

              <div>
                <label
                  for="image-title"
                  class="text-sm font-semibold"
                >
                  Title
                </label>

                <input
                  id="image-title"
                  v-model="imageTitle"
                  type="text"
                  maxlength="200"
                  placeholder="e.g. Screenshot of viral post"
                  class="mt-2 h-12 w-full rounded-xl border border-[var(--vl-border)] bg-white/70 px-4 text-sm outline-none transition focus:border-[var(--vl-terracotta)]"
                  :disabled="savingImage"
                />
              </div>

              <p
                v-if="imageError"
                class="rounded-xl border border-[var(--vl-terracotta)]/20 bg-[var(--vl-terracotta)]/5 px-4 py-3 text-sm text-[var(--vl-terracotta)]"
              >
                {{ imageError }}
              </p>
            </div>

            <div
              class="mt-7 flex justify-end gap-3"
            >
              <button
                type="button"
                class="h-11 rounded-xl border border-[var(--vl-border)] px-5 text-sm font-semibold text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)] disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="savingImage"
                @click="closeImageModal"
              >
                Cancel
              </button>

              <button
                type="button"
                class="inline-flex h-11 items-center justify-center rounded-xl bg-[var(--vl-terracotta)] px-6 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="savingImage"
                @click="saveImageContent"
              >
                {{
                  savingImage
                    ? "Uploading..."
                    : "Upload image"
                }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Add Source Modal -->
      <Teleport to="body">
        <div
          v-if="showSourceModal"
          class="fixed inset-0 z-[100] flex items-center justify-center bg-black/30 p-4 backdrop-blur-sm"
          @click.self="closeSourceModal"
        >
          <div
            class="w-full max-w-2xl rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6 shadow-[0_30px_100px_rgba(32,35,31,0.18)] sm:p-8"
          >
            <div
              class="flex items-start justify-between gap-4"
            >
              <div>
                <div class="eyebrow">
                  <Link :size="13" />

                  External source
                </div>

                <h2
                  class="mt-3 text-2xl font-semibold tracking-[-0.03em]"
                >
                  Add source to this investigation
                </h2>

                <p
                  class="mt-2 text-sm leading-6 text-[var(--vl-muted)]"
                >
                  Connect an external article, webpage, or
                  reference for claim verification.
                </p>
              </div>

              <button
                type="button"
                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[var(--vl-border)] text-xl text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)]"
                aria-label="Close"
                :disabled="savingSource"
                @click="closeSourceModal"
              >
                Ãƒâ€”
              </button>
            </div>

            <div class="mt-7 space-y-5">
              <div>
                <label
                  for="source-title"
                  class="text-sm font-semibold"
                >
                  Title
                </label>

                <input
                  id="source-title"
                  v-model="sourceTitle"
                  type="text"
                  maxlength="200"
                  placeholder="e.g. Original news article"
                  class="mt-2 h-12 w-full rounded-xl border border-[var(--vl-border)] bg-white/70 px-4 text-sm outline-none transition focus:border-[var(--vl-sage-dark)]"
                  :disabled="savingSource"
                />
              </div>

              <div>
                <label
                  for="source-url"
                  class="text-sm font-semibold"
                >
                  Source URL
                </label>

                <input
                  id="source-url"
                  v-model="sourceUrl"
                  type="url"
                  placeholder="https://example.com/article"
                  class="mt-2 h-12 w-full rounded-xl border border-[var(--vl-border)] bg-white/70 px-4 text-sm outline-none transition focus:border-[var(--vl-sage-dark)]"
                  :disabled="savingSource"
                  @keyup.enter="saveSourceContent"
                />

                <p
                  class="mt-2 text-xs text-[var(--vl-muted)]"
                >
                  Include the full URL beginning with
                  https://
                </p>
              </div>

              <p
                v-if="sourceError"
                class="rounded-xl border border-[var(--vl-terracotta)]/20 bg-[var(--vl-terracotta)]/5 px-4 py-3 text-sm text-[var(--vl-terracotta)]"
              >
                {{ sourceError }}
              </p>
            </div>

            <div
              class="mt-7 flex justify-end gap-3"
            >
              <button
                type="button"
                class="h-11 rounded-xl border border-[var(--vl-border)] px-5 text-sm font-semibold text-[var(--vl-muted)] transition-colors hover:text-[var(--vl-ink)] disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="savingSource"
                @click="closeSourceModal"
              >
                Cancel
              </button>

              <button
                type="button"
                class="inline-flex h-11 items-center justify-center rounded-xl bg-[var(--vl-sage-dark)] px-6 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="savingSource"
                @click="saveSourceContent"
              >
                {{
                  savingSource
                    ? "Saving..."
                    : "Save source"
                }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Pipeline -->
      <section
        class="mt-6 rounded-[28px] border border-[var(--vl-border)] bg-[var(--vl-surface)] p-6 sm:p-8"
      >
        <div
          class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--vl-muted)]"
            >
              Intelligence pipeline
            </p>

            <h2
              class="mt-2 text-lg font-semibold"
            >
              Investigation pipeline
            </h2>
          </div>

          <span
            class="text-xs text-[var(--vl-muted)]"
          >
            Stage 19 Ã‚Â· Prediction Engine
          </span>
        </div>

        <div
          class="mt-8 grid gap-3 md:grid-cols-5"
        >
          <!-- Content -->
          <div
            class="rounded-2xl border border-[var(--vl-sage-dark)]/20 bg-[var(--vl-sage)]/6 p-4"
          >
            <span
              class="text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              01
            </span>

            <p
              class="mt-3 text-sm font-semibold"
            >
              Content
            </p>

            <p
              class="mt-1 text-xs text-[var(--vl-muted)]"
            >
              Ingestion
            </p>
          </div>

          <!-- Models -->
          <div
            class="rounded-2xl border border-[var(--vl-sage-dark)]/20 bg-[var(--vl-sage)]/6 p-4"
          >
            <span
              class="text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              02
            </span>

            <p
              class="mt-3 text-sm font-semibold"
            >
              Models
            </p>

            <p
              class="mt-1 text-xs text-[var(--vl-muted)]"
            >
              Prediction
            </p>
          </div>

          <!-- Evidence -->
          <div
            class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-4"
          >
            <span
              class="text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              03
            </span>

            <p
              class="mt-3 text-sm font-semibold"
            >
              Evidence
            </p>

            <p
              class="mt-1 text-xs text-[var(--vl-muted)]"
            >
              Retrieval
            </p>
          </div>

          <!-- Explain -->
          <div
            class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-4"
          >
            <span
              class="text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              04
            </span>

            <p
              class="mt-3 text-sm font-semibold"
            >
              Explain
            </p>

            <p
              class="mt-1 text-xs text-[var(--vl-muted)]"
            >
              Reasoning
            </p>
          </div>

          <!-- Verdict -->
          <div
            class="rounded-2xl border border-[var(--vl-border)] bg-[var(--vl-surface)] p-4"
          >
            <span
              class="text-xs font-semibold text-[var(--vl-sage-dark)]"
            >
              05
            </span>

            <p
              class="mt-3 text-sm font-semibold"
            >
              Verdict
            </p>

            <p
              class="mt-1 text-xs text-[var(--vl-muted)]"
            >
              Intelligence
            </p>
          </div>
        </div>
      </section>
    </template>
  </main>
</template>






