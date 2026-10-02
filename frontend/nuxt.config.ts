import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2026-09-28",

  modules: ["@vueuse/nuxt"],

  devtools: {
    enabled: true,
  },

  css: ["~/assets/css/main.css"],

  vite: {
    plugins: [tailwindcss()],
  },

  typescript: {
    strict: true,
    typeCheck: true,
  },

  runtimeConfig: {
    public: {
      apiBase: "",
    },
  },

  app: {
    head: {
      title: "VeriLens — Evidence Intelligence",

      meta: [
        {
          name: "description",
          content:
            "Multimodal AI authenticity and evidence intelligence platform.",
        },
        {
          name: "theme-color",
          content: "#f4f1e8",
        },
      ],
    },
  },
});
