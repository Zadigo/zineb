import { defineStore } from 'pinia'

const spiderStore = defineStore('spiders', {
  state: () => ({
    spiders: []
  })
})

export {
  spiderStore
}
