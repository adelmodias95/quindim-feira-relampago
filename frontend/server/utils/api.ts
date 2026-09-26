import type { H3Event } from "h3"

type Opcoes = { method?: "GET" | "POST"; body?: unknown }

// Ponte entre o servidor do Nuxt e a API Flask. O navegador nunca chega aqui.
export async function chamarApi<T>(event: H3Event, caminho: string, opcoes: Opcoes = {}): Promise<T> {
  const base = useRuntimeConfig(event).apiUrl

  try {
    return await $fetch<T>(`${base}${caminho}`, {
      method: opcoes.method ?? "GET",
      body: opcoes.body as Record<string, unknown> | undefined,
    })
  } catch (erro: any) {
    const corpo = erro?.data
    // Repassa o envelope de erro da API para a tela mostrar a mensagem certa.
    throw createError({
      statusCode: erro?.statusCode ?? 502,
      statusMessage: corpo?.erro?.mensagem ?? "Não foi possível falar com a API.",
      data: corpo,
    })
  }
}
