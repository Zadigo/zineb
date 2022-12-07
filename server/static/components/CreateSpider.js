const CreateSpider = {
    name: 'CreateSpider',
    emits: {
        'show-change' () {
            return true
        }
    },
    template: `
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <input v-for="(field, i) in fields" v-model="newSpider[field.name]" :key="i" :id="field.name" :type="field.type" max="100" placeholder="Spider name" type="text" class="form-control">
                </div>

                <div class="card-footer d-flex justify-content-right">
                    <div class="btn-group">
                        <button type="button" @click="createSpider" class="btn btn-primary mt-">Create</button>
                        <button type="button" @click="$emit('show-change')" class="btn btn-danger mt-">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    </div>  
    `,
    data () {
        return {
            newSpider: {
                name: null
            }
        }
    },
    computed: {
        fields() {
            return [
                { name: 'name', type: 'text' }
            ]
        }
    },
    methods: {
        async createSpider () {
            this.$emit('show-change')
        }
    }
}
