// Formata centavos inteiros como moeda brasileira, sem passar por float (RN-01).
export function formatarBRL(centavos: number): string {
  const sinal = centavos < 0 ? "-" : ""
  const absoluto = Math.abs(centavos)
  const reais = Math.floor(absoluto / 100)
  const resto = absoluto % 100
  return `${sinal}R$ ${reais.toLocaleString("pt-BR")},${String(resto).padStart(2, "0")}`
}
