export default defineNuxtConfig({
  compatibilityDate: "2026-09-25",
  modules: ["@nuxt/ui"],
  css: ["~/assets/css/main.css"],
  devtools: { enabled: false },
  // Só o servidor do Nuxt conhece a URL da API. NUXT_API_URL sobrescreve em produção.
  runtimeConfig: {
    apiUrl: "http://localhost:8000",
  },
})
