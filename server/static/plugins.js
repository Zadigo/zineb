var repositories = {
    spiders: {
        create: (spiderDetails) => {
            return client({
                method: 'post',
                url: '/spiders',
                data: {
                    name: spiderDetails.name,
                    spider_type: spiderDetails.spiderType
                }
            })
        }
    },

    settings: {
        get: () => {
            return client({
                method: 'get',
                url: '/settings'
            })
        }
    }
}

var globalPlugin = {
    install: (Vue, options) => {
        Vue.prototype.$api = repositories
    }
}
