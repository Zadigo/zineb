const store = new Vuex.Store({
    state: () => ({
        currentSpider: {},
        spiders: [
            {
                name: 'Google'
            }
        ]
    }),
    actions: {
        setCurrentSpider ({ state }, id) {
            state.currentSpider = state.spiders[0]
        }
    },
    getters: {
    }
})
