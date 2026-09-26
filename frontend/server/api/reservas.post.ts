export default defineEventHandler(async (event) => {
  const corpo = await readBody(event)
  return await chamarApi(event, "/v1/reservas", { method: "POST", body: corpo })
})
