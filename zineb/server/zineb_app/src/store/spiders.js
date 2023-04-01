import { defineStore } from 'pinia'

const useSpiders = defineStore('spiders', {
  state: () => ({
    spiders: [
      {
        name: 'Google',
        label: 'all'
      },
      {
        name: 'Kendall',
        label: 'fast'
      }
    ]
  })
})

export {
  useSpiders
}
