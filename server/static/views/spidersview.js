var SpidersView = {
    name: 'SpidersView',
    components: {
        CreateSpider
    },  
    template: `
    <create-spider v-if="showCreate" @show-change="showCreate = false" />

    <div v-else class="card">
        <div class="card-header d-flex justify-content-end">
            <div class="btn-group">
                <button :class="{ 'me-2': showCreate }" class="btn btn-primary" @click="showCreate=true">
                    Create
                </button>

                <button class="btn btn-primary">
                    Refresh
                </button>     
            </div>
        </div>

        <div class="card-body">
            <div class="list-group">
                <div v-if="hasSpiders" class="list-group">
                    <router-link v-for="(spider, i) in spiders" :key="i" :to="{ name: 'spider_view', params: { id: i } }" class="list-group-item list-group-item-action">
                        {{ spider }}
                    </router-link>
                </div>

                <div v-else class="list-group-item">
                    You have no spiders
                </div>
            </div>
        </div>
    </div>
    `,
    // setup () {
    //     const { getSpiders } = useRequests()
    //     return {
    //         getSpiders
    //     }
    // },
    data () {
        return {
            spiders: [{ name: 'Google' }],
            showCreate: false
        }
    },
    computed: {
        hasSpiders () {
            return this.spiders.length > 0
        }
    },
    // beforeMount() {
    //     this.getSpiders()
    // },
    // methods: {
    //     async getSpiders () {
    //         try {
    //             const response = await client.get('/spiders')
    //             this.spiders = response.data.spiders
    //         } catch (error) {
    //             console.log(error)
    //         }
    //     }
    // }
}
