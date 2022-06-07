Vue.use(Vuex)

var store = new Vuex.Store({
    state: () => ({
        settings: {}
    }),

    mutations: {
        setSettings (state, data) {
            state.settings = data
        },
        updateSettings (state, data) {
            _.forEach(Object.keys(data), (key) => {
                state.settings[key] = data[key]
            })
        }
    },
    
    getters: {
        getSpiders (state) {
            return state.settings.SPIDERS
        }
    }
})
