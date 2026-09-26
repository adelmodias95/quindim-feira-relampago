export default defineEventHandler(async (event) => {
  return await chamarApi(event, "/v1/livros")
})
