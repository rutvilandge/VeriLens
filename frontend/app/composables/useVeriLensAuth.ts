type AuthResponse = {
  url?: string;
};

type CsrfResponse = {
  csrfToken: string;
};

export const useVeriLensAuth = () => {
  const config = useRuntimeConfig();

  const apiBase =
    String(config.public.apiBase || "");

  const loading = ref(false);
  const error = ref("");

  const login = async (
    email: string,
    password: string,
  ) => {
    loading.value = true;
    error.value = "";

    try {
      const csrfResponse = await $fetch<CsrfResponse>(
        `${apiBase}/auth/csrf`,
        {
          method: "GET",
          credentials: "include",
        },
      );

      const response = await $fetch<AuthResponse>(
        `${apiBase}/auth/callback/credentials`,
        {
          method: "POST",
          credentials: "include",

          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
            "X-Auth-Return-Redirect": "1",
          },

          body: new URLSearchParams({
            email,
            password,
            csrfToken: csrfResponse.csrfToken,
            callbackUrl:
              `${window.location.origin}/dashboard`,
          }),
        },
      );

      if (response.url) {
        window.location.href = response.url;
        return;
      }

      window.location.href = "/dashboard";
    } catch (err: unknown) {
      console.error("VeriLens login error:", err);

      error.value =
        "Invalid email or password. Please try again.";
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    try {
      const csrfResponse = await $fetch<CsrfResponse>(`${apiBase}/auth/csrf`, { credentials: "include" });
      await $fetch(`${apiBase}/auth/signout`, {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/x-www-form-urlencoded", "X-Auth-Return-Redirect": "1" },
        body: new URLSearchParams({ csrfToken: csrfResponse.csrfToken, callbackUrl: `${window.location.origin}/auth/login` }),
      });
    } catch {
      // A failed sign out is kept visible to the caller; credentials are never cleared client side.
      error.value = "Unable to sign out. Please try again.";
      return false;
    }
    window.location.href = "/auth/login";
    return true;
  };

  return { login, logout, loading, error };
};
