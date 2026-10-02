type VeriLensUser = {
  id: string;
  name: string;
  email: string;
  createdAt: string;
};

type SessionResponse = {
  success: boolean;
  user: VeriLensUser;
};

export const useVeriLensSession = () => {
  const config = useRuntimeConfig();

  const apiBase =
    String(config.public.apiBase || "");

  const user = useState<VeriLensUser | null>(
    "verilens-user",
    () => null,
  );

  const loading = useState(
    "verilens-session-loading",
    () => false,
  );

  const error = useState(
    "verilens-session-error",
    () => "",
  );

  const fetchSession = async () => {
    loading.value = true;
    error.value = "";

    try {
      const response = await $fetch<SessionResponse>(
        `${apiBase}/api/session/me`,
        {
          method: "GET",
          credentials: "include",
        },
      );

      if (!response.success || !response.user) {
        throw new Error("Unable to load session");
      }

      user.value = response.user;

      return response.user;
    } catch (err) {
      console.error("VeriLens session error:", err);

      user.value = null;
      error.value = "Unable to load your workspace.";

      return null;
    } finally {
      loading.value = false;
    }
  };

  return {
    user,
    loading,
    error,
    fetchSession,
  };
};
