export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id")
  return await chamarApi(event, `/v1/pedidos/${id}`)
})
