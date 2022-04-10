var CreateSpider = {
    name: 'CreateSpider',
    template: `
    <div class="form-row">
        <inputv-for="(field, i) in fields" :key="i" type="text" class="form-control">
    </div>
    `,
    data: () => ({
        newSpider: {
            name: null
        }
    }),
    computed: {
        fields() {
            return [
                { name: 'name', type: 'text' }
            ]
        }
    }
}
