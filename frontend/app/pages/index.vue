<script setup lang="ts">
type Livro = {
  sku: string
  titulo: string
  preco_centavos: number
  estoque: number
  disponivel: number
}

type Reserva = {
  id: string
  cliente_id: string
  status: string
  itens: { sku: string; quantidade: number; preco_centavos: number }[]
  criado_em: string
  expira_em: string
}

type Linha = {
  sku: string
  quantidade: number
  preco_centavos: number
  valor_centavos: number
  desconto_centavos: number
  liquido_centavos: number
}

type Pedido = {
  id: string
  reserva_id: string
  cliente_id: string
  status: string
  linhas: Linha[]
  subtotal_centavos: number
  desconto_centavos: number
  total_centavos: number
  criado_em: string
  pago_em: string | null
}

const CLIENTE_ID = "cli_feira"

const route = useRoute()
const router = useRouter()

const erro = ref<string | null>(null)
const carregando = ref(false)

function mensagemDoErro(e: any) {
  return e?.data?.data?.erro?.mensagem ?? e?.data?.statusMessage ?? e?.statusMessage ?? "Algo deu errado."
}

// Os ids ficam na URL: atualizar a página não perde o estado, e o link é compartilhável.
const reservaId = computed(() => (route.query.reserva as string) || null)
const pedidoId = computed(() => (route.query.pedido as string) || null)

const { data: catalogo, refresh: recarregarCatalogo } = await useFetch<{ livros: Livro[] }>("/api/livros")

const { data: reserva, refresh: recarregarReserva } = await useAsyncData<Reserva | null>(
  "reserva",
  async () => {
    if (!reservaId.value) return null
    try {
      return await $fetch<Reserva>(`/api/reservas/${reservaId.value}`)
    } catch {
      return null
    }
  },
  { watch: [reservaId] },
)

const { data: pedido, refresh: recarregarPedido } = await useAsyncData<Pedido | null>(
  "pedido",
  async () => {
    if (!pedidoId.value) return null
    try {
      return await $fetch<Pedido>(`/api/pedidos/${pedidoId.value}`)
    } catch {
      return null
    }
  },
  { watch: [pedidoId] },
)

const livros = computed(() => catalogo.value?.livros ?? [])
const quantidades = reactive<Record<string, number>>({})

function quantidade(sku: string) {
  return quantidades[sku] ?? 0
}

function limite(livro: Livro) {
  // RN-03: no máximo 3 unidades por SKU, e nunca mais do que está disponível.
  return Math.min(3, livro.disponivel)
}

function ajustar(livro: Livro, passo: number) {
  quantidades[livro.sku] = Math.max(0, Math.min(limite(livro), quantidade(livro.sku) + passo))
}

function zerarEscolhas() {
  for (const sku of Object.keys(quantidades)) quantidades[sku] = 0
}

const itensEscolhidos = computed(() =>
  livros.value
    .filter((livro) => quantidade(livro.sku) > 0)
    .map((livro) => ({ sku: livro.sku, quantidade: quantidade(livro.sku) })),
)

const totalEscolhido = computed(() =>
  livros.value.reduce((soma, livro) => soma + livro.preco_centavos * quantidade(livro.sku), 0),
)

// --- contagem regressiva -------------------------------------------------
// agora só ganha valor depois da montagem, então servidor e cliente
// renderizam a mesma coisa na hidratação e o console fica limpo.
const agora = ref<number | null>(null)
let relogio: ReturnType<typeof setInterval> | undefined

onMounted(() => {
  agora.value = Date.now()
  relogio = setInterval(() => (agora.value = Date.now()), 1000)
})

onUnmounted(() => clearInterval(relogio))

const segundosRestantes = computed(() => {
  if (!reserva.value || agora.value === null) return null
  return Math.max(0, Math.floor((new Date(reserva.value.expira_em).getTime() - agora.value) / 1000))
})

const tempoRestante = computed(() => {
  const total = segundosRestantes.value
  if (total === null) return ""
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`
})

const reservaVencida = computed(
  () => reserva.value?.status === "expirada" || segundosRestantes.value === 0,
)

// --- navegação -----------------------------------------------------------

function irParaCatalogo() {
  erro.value = null
  router.replace({ query: {} })
}

function novaCompra() {
  zerarEscolhas()
  irParaCatalogo()
  recarregarCatalogo()
}

// --- ações ---------------------------------------------------------------

async function reservar() {
  erro.value = null
  carregando.value = true
  try {
    const nova = await $fetch<Reserva>("/api/reservas", {
      method: "POST",
      body: { cliente_id: CLIENTE_ID, itens: itensEscolhidos.value },
    })
    await router.replace({ query: { reserva: nova.id } })
    await recarregarCatalogo()
  } catch (e: any) {
    erro.value = mensagemDoErro(e)
    await recarregarCatalogo()
  } finally {
    carregando.value = false
  }
}

async function confirmar() {
  if (!reserva.value) return
  erro.value = null
  carregando.value = true
  try {
    const novo = await $fetch<Pedido>(`/api/reservas/${reserva.value.id}/confirmar`, { method: "POST" })
    zerarEscolhas()
    await router.replace({ query: { pedido: novo.id } })
    await recarregarCatalogo()
  } catch (e: any) {
    erro.value = mensagemDoErro(e)
    await recarregarReserva()
    await recarregarCatalogo()
  } finally {
    carregando.value = false
  }
}

async function atualizarPedido() {
  carregando.value = true
  await recarregarPedido()
  carregando.value = false
}

const corDoStatus: Record<string, "neutral" | "success" | "error"> = {
  aguardando_pagamento: "neutral",
  pago: "success",
  cancelado: "error",
}
</script>

<template>
  <UContainer class="py-10 max-w-3xl">
    <div class="flex items-start justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Feira Relâmpago</h1>
        <p class="text-sm text-muted">Clube Quindim — estoque pequeno, reserve antes de decidir.</p>
      </div>
      <UButton
        v-if="reserva || pedido"
        icon="i-lucide-arrow-left"
        variant="ghost"
        size="sm"
        @click="irParaCatalogo"
      >
        Catálogo
      </UButton>
    </div>

    <UAlert
      v-if="erro"
      color="error"
      variant="subtle"
      :title="erro"
      class="mb-6"
      :close="{ onClick: () => (erro = null) }"
    />

    <!-- Pedido -->
    <UCard v-if="pedido" class="mb-6">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">Pedido</span>
          <UBadge :color="corDoStatus[pedido.status] ?? 'neutral'" variant="subtle">
            {{ pedido.status }}
          </UBadge>
        </div>
        <p class="text-xs text-muted mt-1 font-mono">{{ pedido.id }}</p>
      </template>

      <div class="space-y-2">
        <div v-for="linha in pedido.linhas" :key="linha.sku" class="flex justify-between text-sm">
          <span>{{ linha.quantidade }}× {{ linha.sku }}</span>
          <span class="tabular-nums">
            {{ formatarBRL(linha.valor_centavos) }}
            <span v-if="linha.desconto_centavos > 0" class="text-success">
              − {{ formatarBRL(linha.desconto_centavos) }}
            </span>
            = <strong>{{ formatarBRL(linha.liquido_centavos) }}</strong>
          </span>
        </div>
      </div>

      <template #footer>
        <div class="space-y-1 text-sm tabular-nums">
          <div class="flex justify-between">
            <span>Subtotal</span><span>{{ formatarBRL(pedido.subtotal_centavos) }}</span>
          </div>
          <div class="flex justify-between text-success">
            <span>Desconto</span><span>− {{ formatarBRL(pedido.desconto_centavos) }}</span>
          </div>
          <div class="flex justify-between text-base font-semibold">
            <span>Total</span><span>{{ formatarBRL(pedido.total_centavos) }}</span>
          </div>
        </div>

        <p v-if="pedido.status === 'aguardando_pagamento'" class="text-sm text-muted mt-4">
          O pagamento é processado por um provedor externo, que avisa a API por webhook. O status muda
          quando esse evento chega.
        </p>

        <div class="flex gap-2 mt-4">
          <UButton variant="subtle" :loading="carregando" @click="atualizarPedido">
            Atualizar status
          </UButton>
          <UButton variant="ghost" @click="novaCompra">Nova compra</UButton>
        </div>
      </template>
    </UCard>

    <!-- Reserva -->
    <UCard v-else-if="reserva" class="mb-6">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">Reserva</span>
          <UBadge v-if="agora !== null" :color="reservaVencida ? 'error' : 'primary'" variant="subtle">
            {{ reservaVencida ? "expirada" : `expira em ${tempoRestante}` }}
          </UBadge>
        </div>
        <p class="text-xs text-muted mt-1 font-mono">{{ reserva.id }}</p>
      </template>

      <div class="space-y-2">
        <div v-for="item in reserva.itens" :key="item.sku" class="flex justify-between text-sm">
          <span>{{ item.quantidade }}× {{ item.sku }}</span>
          <span class="tabular-nums">{{ formatarBRL(item.preco_centavos * item.quantidade) }}</span>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-2">
          <UButton :loading="carregando" :disabled="reservaVencida" @click="confirmar">
            Confirmar compra
          </UButton>
          <UButton variant="ghost" @click="novaCompra">Nova compra</UButton>
        </div>
        <p v-if="reservaVencida" class="text-sm text-muted mt-2">
          A reserva expirou e as unidades voltaram para o catálogo.
        </p>
      </template>
    </UCard>

    <!-- Catálogo -->
    <template v-else>
      <UCard v-for="livro in livros" :key="livro.sku" class="mb-3">
        <div class="flex items-center justify-between gap-4">
          <div>
            <p class="font-medium">{{ livro.titulo }}</p>
            <p class="text-sm text-muted">
              {{ livro.sku }} · {{ formatarBRL(livro.preco_centavos) }} ·
              <span :class="livro.disponivel === 0 ? 'text-error' : ''">
                {{ livro.disponivel }} de {{ livro.estoque }} disponíveis
              </span>
            </p>
          </div>

          <div class="flex items-center gap-2">
            <UButton
              icon="i-lucide-minus"
              size="xs"
              variant="outline"
              :disabled="quantidade(livro.sku) === 0"
              @click="ajustar(livro, -1)"
            />
            <span class="w-6 text-center tabular-nums">{{ quantidade(livro.sku) }}</span>
            <UButton
              icon="i-lucide-plus"
              size="xs"
              variant="outline"
              :disabled="quantidade(livro.sku) >= limite(livro)"
              @click="ajustar(livro, 1)"
            />
          </div>
        </div>
      </UCard>

      <div class="flex items-center justify-between mt-6">
        <span class="text-sm text-muted tabular-nums">
          Total sem desconto: <strong>{{ formatarBRL(totalEscolhido) }}</strong>
        </span>
        <UButton :loading="carregando" :disabled="itensEscolhidos.length === 0" @click="reservar">
          Reservar por 15 minutos
        </UButton>
      </div>
    </template>
  </UContainer>
</template>
