var SpidersView = {
    name: 'SpidersView',
    components: {
        CreateSpider
    },  
    template: `
    <div class="card">
        <div class="card-header">
            <button :class="{ 'me-2': showCreate }" class="btn btn-primary" @click="showCreate=true">
                Create
            </button>

            <button v-if="showCreate" class="btn btn-secondary" @click="showCreate=false">
                Cancel
            </button>
        </div>

        <div v-if="hasSpiders" class="card-body">
            <transition name="general-transition">
                <create-spider v-if="showCreate" />

                <ul v-else class="list-group">
                    <router-link v-for="(spider, i) in spiders" :key="spider" :to="{ name: 'spider', params: { id: i } }" class="list-group-item">
                        {{ spider }}
                    </router-link>
                </ul>
            </transition>
        </div>

        <div v-else class="card-body">
            <ul class="list-group">
                <li class="list-group-item">
                    There are no spiders
                </li>
            </ul>
        </div>
    </div>
    `,
    data: () => ({
        spiders: [],
        showCreate: false
    }),

    computed: {
        hasSpiders () {
            return this.spiders.length > 0
        }
    },

    beforeMount() {
        this.setTitle('Spiders')
        client({
            method: 'get',
            url: '/spiders'
        })
        .then((response) => {
            this.spiders = response.data.spiders
        })
        .catch((error) => {
            console.log(error)
        })
    }
}
