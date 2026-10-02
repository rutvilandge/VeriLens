<script setup lang="ts">
const config = useRuntimeConfig(); const apiBase = String(config.public.apiBase || "");

type ModelType =
  | "TEXT_AUTHENTICITY"
  | "AI_GENERATED_TEXT"
  | "IMAGE_AUTHENTICITY"
  | "MULTIMODAL";

interface ModelVersion {
  id: string;
  version: string;
  description: string | null;
  status: string;
  framework: string | null;
  createdAt: string;
}

interface AIModel {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  type: ModelType;
  status: string;
  provider: string | null;
  task: string | null;
  versions: ModelVersion[];
  _count?: {
    experiments: number;
  };
}

interface ModelsResponse {
  success: boolean;
  models: AIModel[];
  message?: string;
}

const models = ref<AIModel[]>([]);
const loading = ref(true);
const error = ref("");

const selectedModel = ref<AIModel | null>(null);
const showDetails = ref(false);

const typeLabels: Record<ModelType, string> = {
  TEXT_AUTHENTICITY: "Text Authenticity",
  AI_GENERATED_TEXT: "AI-Generated Text",
  IMAGE_AUTHENTICITY: "Image Authenticity",
  MULTIMODAL: "Multimodal",
};

const typeDescriptions: Record<ModelType, string> = {
  TEXT_AUTHENTICITY:
    "Evaluates linguistic signals and authenticity patterns in written evidence.",
  AI_GENERATED_TEXT:
    "Identifies patterns associated with synthetic or AI-generated language.",
  IMAGE_AUTHENTICITY:
    "Examines visual evidence for manipulation and synthetic-content signals.",
  MULTIMODAL:
    "Combines multiple evidence types for cross-modal authenticity analysis.",
};

const typeIcons: Record<ModelType, string> = {
  TEXT_AUTHENTICITY: "T",
  AI_GENERATED_TEXT: "AI",
  IMAGE_AUTHENTICITY: "IMG",
  MULTIMODAL: "MM",
};

const typeAccent: Record<ModelType, string> = {
  TEXT_AUTHENTICITY: "text-[#71805b] bg-[#eef2e8] border-[#dce4d2]",
  AI_GENERATED_TEXT: "text-[#687653] bg-[#f0f2e9] border-[#dfe4d5]",
  IMAGE_AUTHENTICITY: "text-[#836f50] bg-[#f4efe5] border-[#e7ddca]",
  MULTIMODAL: "text-[#59684d] bg-[#e9efe4] border-[#d4dfcc]",
};

const statusClass = (status: string) => {
  switch (status) {
    case "READY":
      return "bg-[#edf3e8] text-[#63734f] border-[#d7e2ce]";

    case "DEPLOYED":
      return "bg-[#e5eee0] text-[#536845] border-[#cadbc0]";

    case "DEVELOPMENT":
      return "bg-[#f4f0e6] text-[#88754e] border-[#e6dcc8]";

    case "ARCHIVED":
      return "bg-[#f1f0ec] text-[#85837b] border-[#deddd7]";

    default:
      return "bg-[#f1f1ed] text-[#77766f] border-[#deddd7]";
  }
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const fetchModels = async () => {
  loading.value = true;
  error.value = "";

  try {
    const response = await $fetch<ModelsResponse>(
      `${apiBase}/api/models`,
      {
        credentials: "include",
      },
    );

    if (!response.success) {
      throw new Error(
        response.message || "Unable to load models.",
      );
    }

    models.value = response.models;
  } catch (err: any) {
    console.error("Model Lab fetch error:", err);

    error.value =
      err?.data?.message ||
      err?.message ||
      "Unable to load Model Lab.";
  } finally {
    loading.value = false;
  }
};

const openModel = (model: AIModel) => {
  selectedModel.value = model;
  showDetails.value = true;
};

const closeDetails = () => {
  showDetails.value = false;
  selectedModel.value = null;
};

onMounted(fetchModels);
</script>

<template>
  <div class="min-h-screen bg-[#f7f7f2] text-[#252923]">

    <!-- ================================================= -->
    <!-- Ambient background -->
    <!-- ================================================= -->

    <div class="pointer-events-none fixed inset-0 overflow-hidden">
      <div
        class="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-[#dfe7d5]/40 blur-3xl"
      />

      <div
        class="absolute -bottom-40 -right-32 h-[420px] w-[420px] rounded-full bg-[#e8e2d4]/45 blur-3xl"
      />
    </div>

    <main
      class="relative mx-auto max-w-7xl px-5 py-8 sm:px-8 lg:px-10 lg:py-10"
    >
      <div class="mb-6"><DashboardBackToDashboard /></div>

      <!-- ================================================= -->
      <!-- Header -->
      <!-- ================================================= -->

      <section class="mb-10">

        <div class="mb-5 flex items-center gap-2.5">
          <span
            class="h-2 w-2 rounded-full bg-[#7a8964]"
          />

          <span
            class="text-[11px] font-semibold uppercase tracking-[0.22em] text-[#7a806f]"
          >
            Intelligence / Model Lab
          </span>
        </div>

        <div
          class="flex flex-col justify-between gap-7 md:flex-row md:items-end"
        >
          <div class="max-w-3xl">

            <h1
              class="text-3xl font-semibold tracking-[-0.035em] text-[#242820] sm:text-4xl"
            >
              Model Lab
            </h1>

            <p
              class="mt-3 max-w-2xl text-sm leading-6 text-[#777b72]"
            >
              Manage the intelligence layer behind VeriLens —
              models, versions, evaluations, and experiments.
            </p>

          </div>

          <button
            type="button"
            class="group inline-flex items-center justify-center gap-2 rounded-xl border border-[#d9ddd2] bg-white px-4 py-2.5 text-sm font-medium text-[#59634f] shadow-[0_2px_8px_rgba(50,60,40,0.04)] transition hover:border-[#b9c6aa] hover:bg-[#f7f9f4] hover:shadow-[0_5px_18px_rgba(50,60,40,0.07)]"
            @click="fetchModels"
          >
            <svg
              class="h-4 w-4 transition-transform duration-500 group-hover:rotate-180"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.8"
                d="M4 4v5h5M20 20v-5h-5M5.6 9A7 7 0 0117.9 6.1L20 9M4 15l2.1 2.9A7 7 0 0018.4 15"
              />
            </svg>

            Refresh Registry
          </button>

        </div>
      </section>

      <!-- ================================================= -->
      <!-- Registry summary -->
      <!-- ================================================= -->

      <section
        v-if="!loading && !error"
        class="mb-7 grid gap-4 sm:grid-cols-3"
      >

        <div
          class="rounded-2xl border border-[#dfe2d9] bg-white px-5 py-4 shadow-[0_2px_10px_rgba(50,60,40,0.035)]"
        >
          <div class="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#94978e]">
            Registered models
          </div>

          <div class="mt-2 text-2xl font-semibold tracking-tight text-[#2d3329]">
            {{ models.length }}
          </div>
        </div>

        <div
          class="rounded-2xl border border-[#dfe2d9] bg-white px-5 py-4 shadow-[0_2px_10px_rgba(50,60,40,0.035)]"
        >
          <div class="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#94978e]">
            Model versions
          </div>

          <div class="mt-2 text-2xl font-semibold tracking-tight text-[#2d3329]">
            {{
              models.reduce(
                (total, model) =>
                  total + model.versions.length,
                0,
              )
            }}
          </div>
        </div>

        <div
          class="rounded-2xl border border-[#dfe2d9] bg-white px-5 py-4 shadow-[0_2px_10px_rgba(50,60,40,0.035)]"
        >
          <div class="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#94978e]">
            Experiments
          </div>

          <div class="mt-2 text-2xl font-semibold tracking-tight text-[#2d3329]">
            {{
              models.reduce(
                (total, model) =>
                  total + (model._count?.experiments || 0),
                0,
              )
            }}
          </div>
        </div>

      </section>

      <!-- ================================================= -->
      <!-- Loading -->
      <!-- ================================================= -->

      <section
        v-if="loading"
        class="grid gap-5 md:grid-cols-2 xl:grid-cols-4"
      >
        <div
          v-for="n in 4"
          :key="n"
          class="h-72 animate-pulse rounded-2xl border border-[#e0e2da] bg-white"
        />
      </section>

      <!-- ================================================= -->
      <!-- Error -->
      <!-- ================================================= -->

      <section
        v-else-if="error"
        class="rounded-2xl border border-[#e3d5cd] bg-[#fffaf7] p-7 shadow-[0_3px_15px_rgba(70,50,40,0.035)]"
      >
        <div class="flex items-start gap-4">

          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[#ead9d0] bg-[#f9eee9] text-sm font-semibold text-[#a56f5b]"
          >
            !
          </div>

          <div>
            <h2 class="font-semibold text-[#4c3932]">
              Unable to load Model Registry
            </h2>

            <p class="mt-1 text-sm leading-6 text-[#827871]">
              {{ error }}
            </p>

            <button
              type="button"
              class="mt-4 rounded-lg border border-[#d9ddd2] bg-white px-3.5 py-2 text-xs font-medium text-[#62695d] transition hover:bg-[#f5f6f1]"
              @click="fetchModels"
            >
              Try again
            </button>
          </div>

        </div>
      </section>

      <!-- ================================================= -->
      <!-- Registry -->
      <!-- ================================================= -->

      <template v-else>

        <div class="mb-5 flex items-end justify-between">

          <div>
            <h2
              class="text-lg font-semibold tracking-tight text-[#30362c]"
            >
              Model Registry
            </h2>

            <p class="mt-1 text-xs text-[#8b8e86]">
              {{ models.length }} intelligence
              {{ models.length === 1 ? "model" : "models" }}
              registered
            </p>
          </div>

        </div>

        <!-- ================================================= -->
        <!-- Model cards -->
        <!-- ================================================= -->

        <section
          class="grid gap-5 md:grid-cols-2 xl:grid-cols-4"
        >

          <button
            v-for="model in models"
            :key="model.id"
            type="button"
            class="group relative overflow-hidden rounded-2xl border border-[#dfe2d9] bg-white p-5 text-left shadow-[0_3px_12px_rgba(50,60,40,0.035)] transition duration-300 hover:-translate-y-1 hover:border-[#bdc9b1] hover:shadow-[0_12px_30px_rgba(50,60,40,0.08)]"
            @click="openModel(model)"
          >

            <!-- subtle accent -->
            <div
              class="pointer-events-none absolute right-0 top-0 h-24 w-24 translate-x-8 -translate-y-8 rounded-full bg-[#e8eee2] opacity-60 blur-2xl transition duration-300 group-hover:opacity-90"
            />

            <div class="relative">

              <!-- Icon / Status -->

              <div class="flex items-center justify-between">

                <div
                  class="flex h-11 w-11 items-center justify-center rounded-xl border text-[10px] font-bold tracking-wide"
                  :class="typeAccent[model.type]"
                >
                  {{ typeIcons[model.type] }}
                </div>

                <span
                  class="rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.12em]"
                  :class="statusClass(model.status)"
                >
                  {{ model.status }}
                </span>

              </div>

              <!-- Name -->

              <h3
                class="mt-6 text-[15px] font-semibold leading-5 tracking-[-0.01em] text-[#30362c]"
              >
                {{ model.name }}
              </h3>

              <p
                class="mt-2 min-h-[60px] text-xs leading-5 text-[#858981]"
              >
                {{
                  model.description ||
                  typeDescriptions[model.type]
                }}
              </p>

              <!-- Metadata -->

              <div
                class="mt-5 space-y-2.5 border-t border-[#eceee8] pt-4"
              >

                <div class="flex items-center justify-between text-xs">
                  <span class="text-[#a0a39b]">
                    Type
                  </span>

                  <span class="max-w-[150px] truncate text-right font-medium text-[#69715f]">
                    {{ typeLabels[model.type] }}
                  </span>
                </div>

                <div class="flex items-center justify-between text-xs">
                  <span class="text-[#a0a39b]">
                    Versions
                  </span>

                  <span class="font-medium text-[#59634f]">
                    {{ model.versions.length }}
                  </span>
                </div>

                <div class="flex items-center justify-between text-xs">
                  <span class="text-[#a0a39b]">
                    Experiments
                  </span>

                  <span class="font-medium text-[#59634f]">
                    {{ model._count?.experiments || 0 }}
                  </span>
                </div>

              </div>

              <!-- Open -->

              <div
                class="mt-5 flex items-center gap-1 text-xs font-semibold text-[#758460] transition group-hover:text-[#5d6e4d]"
              >
                Open model

                <span
                  class="transition-transform duration-200 group-hover:translate-x-1"
                >
                  →
                </span>
              </div>

            </div>
          </button>

        </section>

        <!-- ================================================= -->
        <!-- Empty -->
        <!-- ================================================= -->

        <section
          v-if="models.length === 0"
          class="mt-5 rounded-2xl border border-dashed border-[#d5d9ce] bg-white p-12 text-center"
        >
          <div
            class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-[#dce3d5] bg-[#f0f4ec] text-[#72805e]"
          >
            ML
          </div>

          <h3
            class="mt-4 text-sm font-semibold text-[#3c4337]"
          >
            No models registered
          </h3>

          <p
            class="mx-auto mt-2 max-w-sm text-xs leading-5 text-[#8b8e86]"
          >
            Add a model to begin building the VeriLens
            intelligence registry.
          </p>
        </section>

        <!-- ================================================= -->
        <!-- Intelligence areas -->
        <!-- ================================================= -->

        <section class="mt-10">

          <div class="mb-5">
            <div
              class="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#92968c]"
            >
              Model operations
            </div>

            <h2
              class="mt-2 text-lg font-semibold tracking-tight text-[#30362c]"
            >
              Intelligence workspace
            </h2>
          </div>

          <div class="grid gap-5 lg:grid-cols-3">

            <div
              class="rounded-2xl border border-[#dfe2d9] bg-white p-6 shadow-[0_3px_12px_rgba(50,60,40,0.03)]"
            >
              <div
                class="flex h-9 w-9 items-center justify-center rounded-xl bg-[#eef2e9] text-[10px] font-bold text-[#71805b]"
              >
                DS
              </div>

              <div
                class="mt-5 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#969990]"
              >
                Dataset
              </div>

              <h3
                class="mt-2 text-base font-semibold text-[#353b31]"
              >
                Evaluation datasets
              </h3>

              <p
                class="mt-2 text-xs leading-5 text-[#858981]"
              >
                Dataset metadata and sample statistics will
                appear here.
              </p>
            </div>

            <div
              class="rounded-2xl border border-[#dfe2d9] bg-white p-6 shadow-[0_3px_12px_rgba(50,60,40,0.03)]"
            >
              <div
                class="flex h-9 w-9 items-center justify-center rounded-xl bg-[#f0f2e9] text-[10px] font-bold text-[#71805b]"
              >
                MX
              </div>

              <div
                class="mt-5 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#969990]"
              >
                Metrics
              </div>

              <h3
                class="mt-2 text-base font-semibold text-[#353b31]"
              >
                Model evaluation
              </h3>

              <p
                class="mt-2 text-xs leading-5 text-[#858981]"
              >
                Accuracy, precision, recall, and F1 will be
                displayed here.
              </p>
            </div>

            <div
              class="rounded-2xl border border-[#dfe2d9] bg-white p-6 shadow-[0_3px_12px_rgba(50,60,40,0.03)]"
            >
              <div
                class="flex h-9 w-9 items-center justify-center rounded-xl bg-[#f3eee4] text-[10px] font-bold text-[#856f4d]"
              >
                EX
              </div>

              <div
                class="mt-5 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#969990]"
              >
                Experiments
              </div>

              <h3
                class="mt-2 text-base font-semibold text-[#353b31]"
              >
                Experiment workspace
              </h3>

              <p
                class="mt-2 text-xs leading-5 text-[#858981]"
              >
                Configurations and experiment results will
                appear here.
              </p>
            </div>

          </div>
        </section>

      </template>
    </main>

    <!-- ================================================= -->
    <!-- Model Details -->
    <!-- ================================================= -->

    <Teleport to="body">

      <div
        v-if="showDetails && selectedModel"
        class="fixed inset-0 z-50 flex items-center justify-center bg-[#252922]/35 p-4 backdrop-blur-md sm:p-6"
        @click.self="closeDetails"
      >

        <div
          class="max-h-[88vh] w-full max-w-2xl overflow-y-auto rounded-3xl border border-[#dce0d6] bg-[#fafaf6] shadow-[0_25px_80px_rgba(40,50,35,0.18)]"
        >

          <!-- Modal header -->

          <div
            class="flex items-start justify-between border-b border-[#e5e7e0] p-6 sm:p-7"
          >

            <div class="pr-6">

              <div
                class="mb-3 flex items-center gap-2"
              >
                <span
                  class="h-1.5 w-1.5 rounded-full bg-[#7b8966]"
                />

                <span
                  class="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#7b826f]"
                >
                  Model details
                </span>
              </div>

              <h2
                class="text-xl font-semibold tracking-tight text-[#2f352b]"
              >
                {{ selectedModel.name }}
              </h2>

              <p
                class="mt-2 text-sm leading-6 text-[#7f837b]"
              >
                {{ selectedModel.description }}
              </p>

            </div>

            <button
              type="button"
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[#e0e2db] bg-white text-[#858981] transition hover:bg-[#f1f3ed] hover:text-[#4f5948]"
              @click="closeDetails"
            >
              ✕
            </button>

          </div>

          <!-- Modal content -->

          <div class="space-y-7 p-6 sm:p-7">

            <!-- Metadata -->

            <div class="grid gap-3 sm:grid-cols-3">

              <div
                class="rounded-2xl border border-[#e1e4dc] bg-white p-4"
              >
                <div
                  class="text-[9px] font-semibold uppercase tracking-[0.16em] text-[#9a9d95]"
                >
                  Type
                </div>

                <div
                  class="mt-2 text-sm font-medium text-[#5f6955]"
                >
                  {{ typeLabels[selectedModel.type] }}
                </div>
              </div>

              <div
                class="rounded-2xl border border-[#e1e4dc] bg-white p-4"
              >
                <div
                  class="text-[9px] font-semibold uppercase tracking-[0.16em] text-[#9a9d95]"
                >
                  Provider
                </div>

                <div
                  class="mt-2 truncate text-sm font-medium text-[#5f6955]"
                >
                  {{ selectedModel.provider || "—" }}
                </div>
              </div>

              <div
                class="rounded-2xl border border-[#e1e4dc] bg-white p-4"
              >
                <div
                  class="text-[9px] font-semibold uppercase tracking-[0.16em] text-[#9a9d95]"
                >
                  Task
                </div>

                <div
                  class="mt-2 truncate text-sm font-medium text-[#5f6955]"
                >
                  {{ selectedModel.task || "—" }}
                </div>
              </div>

            </div>

            <!-- Versions -->

            <div>

              <div class="mb-4">

                <div
                  class="text-[9px] font-semibold uppercase tracking-[0.18em] text-[#979b91]"
                >
                  Model lifecycle
                </div>

                <h3
                  class="mt-2 text-sm font-semibold text-[#343a30]"
                >
                  Model Versions
                </h3>

                <p
                  class="mt-1 text-xs text-[#8a8e85]"
                >
                  Registered versions for this model.
                </p>

              </div>

              <div
                v-if="selectedModel.versions.length"
                class="space-y-2"
              >

                <div
                  v-for="version in selectedModel.versions"
                  :key="version.id"
                  class="flex items-center justify-between rounded-2xl border border-[#e1e4dc] bg-white p-4"
                >

                  <div>

                    <div
                      class="text-sm font-semibold text-[#4c5545]"
                    >
                      {{ version.version }}
                    </div>

                    <div
                      class="mt-1 text-xs text-[#92958d]"
                    >
                      {{
                        version.framework ||
                        "Framework not specified"
                      }}
                    </div>

                  </div>

                  <div class="text-right">

                    <div
                      class="inline-flex rounded-full border px-2 py-1 text-[9px] font-semibold uppercase tracking-[0.1em]"
                      :class="statusClass(version.status)"
                    >
                      {{ version.status }}
                    </div>

                    <div
                      class="mt-2 text-[10px] text-[#999c94]"
                    >
                      {{ formatDate(version.createdAt) }}
                    </div>

                  </div>

                </div>

              </div>

              <div
                v-else
                class="rounded-2xl border border-dashed border-[#d8dcd3] bg-white p-6 text-center text-xs text-[#92968d]"
              >
                No model versions registered yet.
              </div>

            </div>

          </div>
        </div>
      </div>

    </Teleport>
  </div>
</template>

