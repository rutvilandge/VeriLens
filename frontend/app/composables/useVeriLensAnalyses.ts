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

type AnalysisStats = {
  investigations: number;
  completed: number;
  processing: number;
  failed: number;
  evidence: number;
  analyzedEvidence: number;
  pendingEvidence: number;
};

type StatsResponse = {
  success: boolean;
  stats: AnalysisStats;
};

type AnalysesResponse = {
  success: boolean;
  analyses: Analysis[];
};

export const useVeriLensAnalyses = () => {
  const config = useRuntimeConfig();

  const apiBase =
    String(config.public.apiBase || "");

  const stats = useState<AnalysisStats>(
    "verilens-analysis-stats",
    () => ({
      investigations: 0,
      completed: 0,
      processing: 0,
      failed: 0,
      evidence: 0,
      analyzedEvidence: 0,
      pendingEvidence: 0,
    }),
  );

  const analyses = useState<Analysis[]>(
    "verilens-analyses",
    () => [],
  );

  const loading = useState(
    "verilens-analyses-loading",
    () => false,
  );

  const error = useState(
    "verilens-analyses-error",
    () => "",
  );

  const fetchStats = async () => {
    try {
      const response =
        await $fetch<StatsResponse>(
          `${apiBase}/api/analyses/stats`,
          {
            method: "GET",
            credentials: "include",
          },
        );

      if (!response.success) {
        throw new Error(
          "Unable to load analysis statistics",
        );
      }

      stats.value = { ...stats.value, ...response.stats };

      return response.stats;
    } catch (err) {
      console.error("Dashboard statistics request failed.");

      return null;
    }
  };

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
          "Unable to load analyses",
        );
      }

      analyses.value = response.analyses;

      return response.analyses;
    } catch (err) {
      console.error("Investigation list request failed.");

      error.value =
        "Unable to load your analyses.";

      return [];
    } finally {
      loading.value = false;
    }
  };

  const refreshDashboard = async () => {
    await Promise.all([
      fetchStats(),
      fetchAnalyses(),
    ]);
  };

  return {
    stats,
    analyses,
    loading,
    error,
    fetchStats,
    fetchAnalyses,
    refreshDashboard,
  };
};


