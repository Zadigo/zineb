var SpiderView = {
    name: 'SpiderView', 
    template: `
    <div class="card">
        <div class="card-header">
            <h5 class="card-title">Spider name</h5>    
        </div>

        <div class="card-body">
            <h5 class="card-title">Urls</h5>
            
            <div class="list-group">
                <a href="http://example.com" class="list-group-item d-flex justify-content-between align-items-center" target="_blank">
                    <span>http://example.com</span>
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            </div>

            <div class="my-2">
                <h5 class="card-title">Proxies</h5>

                <div v-for="(proxy, i) in proxies" :key="i" class="d-flex justify-content-start gap-1 my-1">
                    <input v-model="proxies[i].netloc" type="text" class="form-control" placeholder="Netloc">
                    <input v-model="proxies[i].address" type="text" class="form-control" placeholder="Proxy address">
                    <button type="button" class="btn btn-info" @click="addProxy">Add</button>
                </div>
            </div>        
        </div>

        <div class="card-footer d-flex justify-content-end">
            <button class="btn btn-primary" @click="runSpider">
                <div v-if="running" class="spinner-grow spinner-grow-sm text-light  me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>

                <i v-else class="fa-solid fa-arrow-right me-2"></i>
                Run spider
            </button>
        </div>
    </div>
    `,
    data () {
        return {
            running: false,
            proxies: [
                {
                    netloc: null,
                    address: null 
                }
            ]
        }
    },
    methods: {
        async runSpider () {
            this.running = true
        },
        addProxy () {
            this.proxies.push({
                netloc: null,
                address: null
            })
        }
    },
    created () {
        try {
            this.$store.dispatch('setCurrentSpider', this.$route.params.id)
        } catch (e) {
            console.error('some', e)
        }
    }
}
