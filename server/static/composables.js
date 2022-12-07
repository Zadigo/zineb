function useRequests () {
  async function getSpiders () {
    try {
      const response = await client.get('/spiders')
      this.spiders = response.data.spiders
    } catch (error) {
      console.log(error)
    }
  }

  return {
    getSpiders
  }
}
